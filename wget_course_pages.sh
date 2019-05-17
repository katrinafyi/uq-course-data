#! /bin/bash 

cd "$(dirname "$0")"
course_codes='./data/course_codes.txt'
wget_list='./_wget_list.txt'

mkdir -p html

# 

aria2c -c -j3 -x10 --auto-file-renaming=false  --dir=./html -i ./data/_aria_list.txt

s=''
# rm -f "$wget_list"
# while read code; do 
#     s="$s"'https://my.uq.edu.au/programs-courses/course.html?course_code='"$code
# "
# done < "$course_codes"
# echo "$s" > "$wget_list"



# wget -E -H -e robots=off -P ./html/ -i ./data/_url_list.txt