#! /bin/bash 

cd "$(dirname "$0")"
course_codes='./data/course_codes.txt'

mkdir -p html

while read code; do 
    code="${code//[[:space:]]/}"
    if [[ -f "./html/$code.html" ]]; then 
        echo "$code already downloaded."
    else 
        wget 'https://my.uq.edu.au/programs-courses/course.html?course_code='"$code" -O "./html/$code".html & 
    fi
done < "$course_codes"