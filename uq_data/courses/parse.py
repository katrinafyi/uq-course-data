import typing as T 

import datetime as dt
import bs4
import os
import json

from collections import namedtuple

import logging

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

CourseData = namedtuple('CourseData', 'data file')

logger = logging.getLogger(__name__)

Base = declarative_base()

class Course(Base):
    __tablename__ = 'courses'
    course_code = Column(String(16), primary_key=True, unique=True, index=True)

    course_name = Column(String)
    level = Column(String)
    faculty = Column(String)
    school = Column(String)
    units = Column(String)
    duration = Column(String)
    contact = Column(String)
    restricted = Column(String)
    incompatible = Column(String)
    prerequisites = Column(String)
    assessment_methods = Column(String)
    coordinator = Column(String)
    study_abroad = Column(String)
    description = Column(String)

    last_updated = Column(String)

    offerings = relationship('Offering', back_populates='course')

class Offering(Base):
    __tablename__ = 'offerings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String(16), ForeignKey('courses.course_code'))
    code = Column(String)
    year = Column(Integer)
    teaching_period = Column(String, nullable=True)

    course = relationship('Course', back_populates='offerings')


_local_tz = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo

_id_mapping = {
    'course-level': 'level',
    'course-faculty': 'faculty',
    'course-school': 'school',
    'course-units': 'units',
    'course-duration': 'duration',
    'course-contact': 'contact',
    'course-restricted': 'restricted',
    'course-incompatible': 'incompatible',
    'course-prerequisite': 'prerequisites',
    'course-assessment-methods': 'assessment_methods',
    'course-coordinator': 'coordinator',
    'course-studyabroard': 'study_abroad',
    'course-summary': 'description',
}

def parse_course_html(html_file: T.IO[T.Any], updated_time: dt.datetime=None) -> T.Dict:
    soup = bs4.BeautifulSoup(html_file.read(), features='lxml')

    data = {}
    def _find_section(element_id, output_key):
        try:
            return soup.find('p', {'id': element_id}).text.strip()
        except AttributeError:
            return ''

    # Get the course title by deleting " (ABCD1234)" from the heading.
    title = soup.find('h1', {'id': 'course-title'}).text
    
    data['course_code'] = course_code = title.split('(')[-1].replace(')', '')
    data['course_name'] = course_name = title.replace(' ('+course_code+')', '', 1)

    semesters = []
    semester_elements = soup.find('div', {'id': 'description'}).find_all('a', {'class': 'course-offering-year'})
    for sem_elem in semester_elements:
        semester_code = sem_elem['href'].split('&offer=')[1].split('&')[0]
        if '&year=' in sem_elem['href']:
            year = int(sem_elem['href'].split('&year=')[1].split('+')[0])
        else:
            year = dt.datetime.today().year
        teaching_period = None 
        if '(' in sem_elem.text: # possibly non-standard teaching period
            teaching_period = sem_elem.text.split('(')[1].split(')')[0]
            if teaching_period == 'Standard':
                teaching_period = None
        semesters.append({'code': semester_code, 'year': year, 'teaching_period': teaching_period})
        # # TODO: Will break for the first half of a year!!

    data['semesters'] = semesters

    for html_id, data_key in _id_mapping.items():
        data[data_key] = _find_section(html_id, data_key)
    # gets everything else

    if updated_time is None:
        updated_time = dt.datetime.now(dt.timezone.utc)
    data['last_updated'] = updated_time.isoformat()

    return data


def parse_all_courses_from_html(html_folder: str):

    for html_path in os.listdir(html_folder):
        html_path_full = os.path.join(html_folder, html_path)

        if not (os.path.isfile(html_path_full) and html_path.lower().endswith('.html')):
            continue 
        
        modified = dt.datetime.fromtimestamp(os.path.getmtime(html_path_full))
        modified = modified.replace(tzinfo=_local_tz)
        
        with open(html_path_full) as html_file:
            parsed_data = parse_course_html(html_file, modified)

        yield CourseData(parsed_data, html_path)

def parse_and_write_sqlite(html_folder):
    engine = create_engine('sqlite:///data/course_data.sqlite')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    s = Session()

    for data, path in parse_all_courses_from_html(html_folder):
        print(path)
        d = {k: v for k, v in data.items() if k != 'semesters'}
        q = s.query(Course).get(d['course_code'])
        if q:
            if q.last_updated < d['last_updated']:
                print('time to update') 
            else:
                print('not updating')
        else:
            s.add(Course(**d))

    s.commit()

def parse_and_write_json(output_folder: str, html_folder: str):
    # https://stackoverflow.com/a/39079819

    for data, path in parse_all_courses_from_html(html_folder):
        out_path_full = os.path.join(output_folder, path.upper().replace('.HTML', '.json'))
        modified = dt.datetime.fromisoformat(data['last_updated'])

        try:
            with open(out_path_full) as out_file:
                last_modified = dt.datetime.fromisoformat(json.load(out_file)['last_updated'])
        except OSError:
            last_modified = dt.datetime.min.replace(tzinfo=_local_tz)

        print('json', last_modified,   'HTML', modified )

        if last_modified > modified:
            print(f'{path}\'s JSON file is newer than the HTML file!')
            continue
        elif last_modified == modified:
            print(f'{path}\'s JSON file matches the HTML file.')
            continue
        else:
            print(f'{path}\'s JSON file is older than the HTML, parsing...')

        with open(out_path_full, 'w') as out_file:
            json.dump(data, out_file)

if __name__ == "__main__":
    parse_and_write_json('./course', './html')
    # parse_and_write_sqlite('./html')