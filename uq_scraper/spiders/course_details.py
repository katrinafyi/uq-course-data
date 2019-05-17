# -*- coding: utf-8 -*-
import scrapy
import json 
import datetime

BASE = 'https://my.uq.edu.au'

seen = set()
with open('./data/course_details.json') as f:
    for l in f:
        if l.startswith('{"code": "'):
            l = l[:30]
            l = l.replace('{"code": "', '', 1)
            code, _ = l.split('"', 1)
            seen.add(code)
print(len(seen), 'items already done.')
print()

with open('./data/courses.json') as f:
    course_urls = [BASE+x['href'] for x in json.load(f) if x['code'] not in seen]

class CourseDetailsSpider(scrapy.Spider):
    name = 'course_details'
    allowed_domains = ['my.uq.edu.au']
    start_urls = course_urls

    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
        'RETRY_TIMES': 10,
    }

    _fields = {
        'course-level': 'level',
        'course-faculty': 'faculty',
        'course-school': 'school',
        'course-units': 'units',
        'course-duration': 'duration',
        'course-contact': 'contact',
        'course-incompatible': 'incompatible',
        'course-prerequisite': "prerequisite",
        'course-companion': 'companion',
        'course-restricted': 'restricted',
        'course-assessment-methods': 'assessment',
        'course-coordinator': 'coordinator',
        'course-studyabroard': 'study_abroad'
    }

    def parse(self, response):
        out = {
            'code': response.css('#course-title::text').get().split('(')[-1][:-1],
            'name': response.css('.breadcrumb-wrapper>ul>li:nth-child(2)::text').get(),
            'current': response.css('#course-current-offerings').get() is not None,
            '_updated': datetime.datetime.utcnow().isoformat()
        }

        desc = '\n'.join(response.css('#course-summary ::text').getall()).strip()
        out['description'] = desc

        left = response.css('#summary-content')
        for key, name in self._fields.items():
            value = left.css(f'#{key} ::text').getall() or None
            if value:
                value = ' '.join(value).strip()
            out[name] = value

            
        
        out['offerings'] = offers = []
        for tr in response.css('.offerings > tbody > tr'):
            fields = tr.css('td')
            sem = fields[0].css('a::text').get().strip()

            if ' (' in sem:
                sem_and_year, tp = sem.split(' (', 1)
                tp = tp[:-1]
            else:
                sem_and_year = sem
                tp = None
            sem, year = sem_and_year.split(', ', 1)
            
            ecp = fields[3].css('a::attr(href)').get()
            offers.append({
                'code': None if not ecp else ecp.split('=')[-1],
                'semester': sem,
                'year': int(year),
                'teaching_period': tp,
                'location': fields[1].css('*::text').get(),
                'mode': fields[2].css('*::text').get(),
                'ecp': ecp
            })

        yield out
