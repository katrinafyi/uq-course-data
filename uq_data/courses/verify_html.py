import glob
import os

def analyse_html(html_folder):
    html = {
        'empty': [],
        'not_found': [],
        'normal': [],
    }
    for f in glob.glob(os.path.join(html_folder, '*')):
        if os.path.getsize(f) == 0:
            html['empty'].append(f)
            continue
        else:
            print(f)
            with open(f) as f_:
                if '<h1 id="course-notfound">The course you requested could not be found.</h1>' in f_.read():
                    html['not_found'].append(f)
                    continue
        html['normal'].append(f)
    return html


if __name__ == "__main__":
    import json
    with open('analysis.json', 'w') as f:
        d = analyse_html('./html')
        json.dump(d, f, indent=2)
    
    for x in d['empty']:
        os.remove(os.path.normpath(x))
    for x in d['not_found']:
        os.remove(x)
    