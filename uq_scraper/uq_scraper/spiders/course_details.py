# -*- coding: utf-8 -*-
import scrapy
import json 
import datetime
import random

seen = set()
try:
    with open('../data/course_details.json') as f:
        seen.update(x['code'] for x in json.load(f))
except FileNotFoundError: pass
print(len(seen), 'items already done.')
print()

course_urls = []
try:
    with open('../data/courses.json') as f:
        course_urls = [x['href'] for x in json.load(f) if x['code'] not in seen]
except FileNotFoundError: pass

random.shuffle(course_urls)
# course_urls = random.sample(course_urls, min(400, len(course_urls)))

class CourseDetailsSpider(scrapy.Spider):
    name = 'course_details'
    allowed_domains = ['my.uq.edu.au']
    start_urls = course_urls

    custom_settings = {
        'LOG_LEVEL': 'INFO',

        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        'COOKIES_ENABLED': False,
        
        'CONCURRENT_REQUESTS': 10,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
        'DOWNLOAD_DELAY': 0.5,
        'RETRY_TIMES': 10,

        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4,
        'AUTOTHROTTLE_DEBUG': True
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

        desc = ' '.join(response.css('#course-summary ::text').getall()).strip()
        out['description'] = desc

        left = response.css('#summary-content')
        for key, name in self._fields.items():
            value = left.css(f'#{key} ::text').getall() or None
            if value:
                value = ' '.join(value).strip()
            out[name] = value

            
        
        out['offerings'] = offers = []
        for table, archived in (('#course-current-offerings', False), 
                ('#course-archived-offerings', True)):
            for tr in response.css(f'{table} > tbody > tr'):
                fields = tr.css('td')
                sem = fields[0].css('a::text').get().strip()

                if ' (' in sem:
                    sem_and_year, tp = sem.split(' (', 1)
                    tp = tp[:-1]
                else:
                    sem_and_year = sem
                    tp = None
                sem, year = sem_and_year.split(', ', 1)
                
                link = fields[0].css('a::attr(href)').get()
                ecp = fields[3].css('a::attr(href)').get()
                offers.append({
                    'offer_code': link.split('offer=', 1)[1].split('&', 1)[0],
                    'link': response.urljoin(link),
                    'semester': sem,
                    'year': int(year),
                    'teaching_period': tp,
                    'archived': archived,
                    'location': fields[1].css('*::text').get(),
                    'mode': fields[2].css('*::text').get(),
                    'profile_id': None if not ecp else ecp.split('=')[-1],
                    'ecp': ecp
                })

        yield out
