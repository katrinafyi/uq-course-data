import urllib.request
import json.encoder

def parse_courses_html(html) -> list:
    courses = []
    for line in html:
        if line.startswith(b' <a href="#" class="code">'):
            courses.append(line.replace(b'<a href="#" class="code">', b'').replace(b'</a>', b'').strip().decode('utf-8'))
    return courses

if __name__ == "__main__":
    url = 'https://my.uq.edu.au/programs-courses/search.html?keywords=course&searchType=all&archived=false'
    with urllib.request.urlopen(url) as f:
        courses = parse_courses_html(f)
    with open('data/course_codes.json', 'w') as j:
        json.dump(courses, j)
    with open('data/course_codes.txt', 'w', newline='\n') as f:
        f.write('\n'.join(courses))