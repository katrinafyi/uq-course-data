/* Should be executed in console of 
https://my.uq.edu.au/programs-courses/search.html?keywords=course&searchType=course&archived=false
*/

{
  const $ = x => document.querySelector(x);
  const $$ = x => Array.from(document.querySelectorAll(x));
  const courses = Array.from($('.listing').querySelectorAll('.code')).map(codeEl => {
    const code = codeEl.textContent.trim();
    const name = $('#course-'+code+'-title').textContent.trim();
    const href = 'https://my.uq.edu.au/programs-courses/course.html?course_code='+code;
    return {code, name, href};
  });
  console.log(JSON.stringify(courses, null, 2));
}
