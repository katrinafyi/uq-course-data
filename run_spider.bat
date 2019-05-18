@echo off

scrapy crawl course_details -o data/course_details.json
REM :start
REM timeout 600
REM goto start