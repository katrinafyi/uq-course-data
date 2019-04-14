import bs4 

import re

from ..course_list import CourseList
from ..prereqs import *

class ProgramParser:
    """Abstract class representing a parser for a whole degree's course list.

    Concrete subclasses should define methods to parse a certain page.

    """
    
    def __init__(self):
        self.root_course_list = None
        self.current_course_list = None

    def parse_program(self, html: bs4.BeautifulSoup):
        root = html.find('div', {'id': 'program-course-list'})
        self.parse_program_title(root.find('h1').decode_contents())

        
        for planlist in root.find_all('div', {'class': 'planlist'}):
            title = planlist.find('h1').decode_contents()
            self.parse_plan_list(planlist, title)

            for courselist in planlist.find_all('div', {'class': 'courselist'}):
                table = courselist.find('table', {'class': 'courses'})
                prev = table.find_previous_sibling('p')
                self.parse_course_list(courselist)
                courses = self.parse_course_table(table, prev.decode_contents())
                self.handle_course_table(courses)

        self.parse_endnotes(root.find('div', {'id': 'endnotes'}))

    def parse_endnotes(self, div: bs4.Tag):
        #print(div)
        pass

    def parse_program_title(self, title: str):
        """Parses the program name.
        """
        raise NotImplementedError()
    

    def parse_course_table(self, table: bs4.Tag, text: str):
        """Parses the given course table and returns the courses as a list of 
        nodes.
        
        Arguments:
            table {bs4.Tag} -- table.courses containing list of courses.
            text {str} -- text immediately preceding this table.
    
        Raises:
            NotImplementedError -- [description]
        """
        # print('Handling course table')
        courses = []
        tbody = table.find('tbody')
        for row in tbody('tr'):
            # parse text code, units and name of this row.
            tds = row.findAll('td')
            code = tds[0].text.replace('[', '').strip() 
            if code == 'or': continue
            units = float(tds[1].text)
            name = tds[2].text.strip()
            # build course node
            node = CourseNode(code, units, name)

            # handle OR cases
            classes = row.get('class', [])
            if 'option' in classes:
                if 'first' in classes:
                    courses.append(Or([node]))
                else:
                    courses[-1].children.append(node)
            else:
                courses.append(node)
        # print(courses)
        return courses

    def handle_course_table(self, courses: list):
        """Attaches the given course list to the appropriate course list."""
        raise NotImplementedError()

    def parse_course_list(self, div: bs4.Tag):
        """Parses a div.courselist and performs some action on the current 
        CourseList."""
        raise NotImplementedError()

    def parse_plan_list(self, div: bs4.Tag, title: str):
        """Parses given planlist. Should create CourseList object to use for 
        the div.
        
        Arguments:
            div {bs4.Tag} -- div.planlist to parse.
        
        Raises:
            NotImplementedError -- [description]
        """
        raise NotImplementedError()

class BMathParser(ProgramParser):
    units_regex = re.compile(r'(\d+)\s+units?')

    def parse_program_title(self, h1: str):
        self.current_course_list = CourseList(h1)
        self.root_course_list = self.current_course_list

        self.current_node = None

    def parse_plan_list(self, div, title: str):
        course_list = CourseList(title)
        if title.startswith('Part '):
            if title in ('Part A', 'Part C'):
                course_list.node = And()
            course_list.set_depth(self.current_course_list, 1)
        else:
            course_list.node = And()
            course_list.set_depth(self.current_course_list, 2)
        self.current_course_list = course_list

    def handle_course_table(self, courses: list):
        self.current_node.children.extend(courses)

    def parse_course_list(self, div):
        text = div.find('p').text.strip()
        if text:
            units = self.units_regex.search(text).groups()[0]
            units = int(units)
            self.current_node = UnitsOf(units=units)
            self.current_course_list.node.children.append(self.current_node)

def main():
    from urllib.request import urlopen
    
    print('Scraper test')
    with open('2393.html') as f:
    # with urlopen('https://my.uq.edu.au/programs-courses/program_list.html?acad_prog=2393') as f:
        soup = bs4.BeautifulSoup(f)
        parser = BMathParser()
        parser.parse_program(soup)
        print(str(parser.root_course_list))
        x = parser.root_course_list.sublists[1].sublists[1]
        print(pretty_string(x.node))
        x = parser.root_course_list.sublists[0]
        print(pretty_string(x.node))

if __name__ == "__main__":
    main()