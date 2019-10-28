# (Unofficial) UQ Course Data API

`uq_data` is a Python module describing a data structure for UQ courses 
and programs. Planned features:

 - Course details
 - Program and major details
 - Course, program and major requirements represented as a graph
 - Verification of above requirements

`uq_scraper` is a scraper for UQ course data, written using scrapy. Scraped 
data is stored as JSON files in `data`.  

Usage:

1. Clone this repository and cd into `uq_scraper`.
2. Install `python3.7`.
3. Install `pip`, then `pip install pipenv`.
4. `python3 -m pipenv install` to install from Pipfile. 
   May need to remove `pypiwin32` from Pipfile, see [this issue](https://github.com/mhammond/pywin32/issues/1177).
5. Activate the pipenv shell using `pipenv shell`.
6. To scrape course codes:

       python3 -m scrapy crawl course_codes -o ../data/courses.json
    
   To scrape course details (after course codes):
   
       python3 -m scrapy crawl course_details -o ../data/course_details.json
