# -*- coding: utf-8 -*-
import scrapy


class CourseCodesSpider(scrapy.Spider):
    name = 'course_codes'
    allowed_domains = ['my.uq.edu.au']
    start_urls = ['https://my.uq.edu.au/programs-courses/search.html?keywords=course&searchType=all&archived=false/']

    def parse(self, response):
        for li in response.css('#courses-container .listing > li'):
            yield {
                'code': li.css('.code::text').get(),
                'name': li.css('.title::text').get(),
                'href': response.urljoin(
                    li.css('a[href^="/programs-courses/"]::attr(href)').get().split('&offer=', 1)[0])
            }
