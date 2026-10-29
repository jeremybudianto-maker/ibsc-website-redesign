const searchData = [
 {
  "title": "About IBSC",
  "url": "about.html",
  "text": "Established in 2017, Yuan Ze University’s International Bachelor in Strategic Communication prepares students to communicate with purpose in a multilingual, multicultural world."
 },
 {
  "title": "Academics",
  "url": "academics.html",
  "text": "Build a foundation in strategic communication and public relations, then explore the subjects and experiences that connect with your interests."
 },
 {
  "title": "Admissions",
  "url": "admissions.html",
  "text": "Discover an English-taught degree in strategic communication at Yuan Ze University. Choose the admission pathway that applies to you and follow the current official guidance."
 },
 {
  "title": "Carlos Hernández Mercado",
  "url": "faculty-carlos-hernandez.html",
  "text": "Rhetoric, philosophy of writing, and the rhetoric of health and medicine."
 },
 {
  "title": "Ching-Pu Chen",
  "url": "faculty-ching-pu-chen.html",
  "text": "Decision science, negotiation, professional ethics, and crisis decision-making."
 },
 {
  "title": "Chun-Hao Li",
  "url": "faculty-chun-hao-li.html",
  "text": "Population studies, historical demography, and urban studies."
 },
 {
  "title": "I-Chun Liu",
  "url": "faculty-i-chun-liu.html",
  "text": "Public and cultural policy, social welfare, and health insurance research."
 },
 {
  "title": "Robert “Coach” Johanson",
  "url": "faculty-robert-johanson.html",
  "text": "Business English, professional presentations, sociolinguistics, and language learning."
 },
 {
  "title": "Ying-Ting Wang",
  "url": "faculty-ying-ting-wang.html",
  "text": "Social demography, health inequality, family, and well-being."
 },
 {
  "title": "News & Stories",
  "url": "news.html",
  "text": "Stories from the IBSC community, from cultural discovery to the moments that bring students together."
 },
 {
  "title": "Faculty & Staff",
  "url": "people.html",
  "text": "Meet the IBSC faculty and affiliated faculty whose expertise connects language, communication, culture, policy, and professional practice."
 },
 {
  "title": "Student resources",
  "url": "resources.html",
  "text": "Plan your studies, take part in campus life and prepare for what comes next. Find the IBSC information you need in one place."
 },
 {
  "title": "Discover Taiwan's Creative Industry",
  "url": "story-creative-industry.html",
  "text": "An international student visit explored how cultural heritage becomes part of Taiwan’s contemporary creative industries."
 },
 {
  "title": "International Pizza Party",
  "url": "story-international-pizza.html",
  "text": "A relaxed gathering gave students room to share experiences, exchange perspectives, and make new friends."
 },
 {
  "title": "Night of Glory – IBSC Student Association",
  "url": "story-night-of-glory.html",
  "text": "Celebrating cross-cultural service and the students behind “We Are The World: Unity in Diversity.”"
 },
 {
  "title": "Student Life",
  "url": "student-life.html",
  "text": "Campus life is part of the IBSC experience. Connect with classmates, take part in student activities and discover new perspectives through a community that crosses cultures."
 },
 {
  "title": "International admission guide",
  "url": "admissions.html#international-guide",
  "text": "Prepare for an English-taught degree in strategic communication. Understand the applicant category, gather your documents and submit through YZU’s official application portal. Check the applicant category Prepare your document folder English and document preparation Complete your application Questions before you apply?"
 },
 {
  "title": "Overseas compatriot, Hong Kong and Macau guide",
  "url": "admissions.html#overseas-guide",
  "text": "YZU offers a dedicated direct admission route for overseas compatriot, Hong Kong and Macau applicants. Start with your status and the evidence needed for review. Understand the category Gather evidence for your application Plan for document verification Follow the direct application process Get the right help"
 },
 {
  "title": "Undergraduate admissions",
  "url": "admissions.html#domestic-guide",
  "text": "Explore YZU’s undergraduate admission routes, then prepare for the route that applies to you. IBSC’s portfolio and interview guidance can help you explain your interests and achievements. Choose your admission route Complete each application step Keep your application current"
 },
 {
  "title": "Individual application information",
  "url": "admissions.html#individual-guide",
  "text": "Explore YZU’s undergraduate admission routes, then prepare for the route that applies to you. IBSC’s portfolio and interview guidance can help you explain your interests and achievements. Prepare your learning portfolio Prepare for the interview"
 },
 {
  "title": "Scholarships and financial support",
  "url": "admissions.html#scholarships-panel",
  "text": "Explore the types of support described by IBSC and YZU. Your applicant category, entry year and the current award announcement determine the relevant rules. Types of support International and overseas compatriot students Understand renewal conditions Prepare for an application"
 },
 {
  "title": "Curriculum and course map",
  "url": "academics.html#curriculum-panel",
  "text": "IBSC connects strategic communication, practical English, design and digital media. Follow the learning pathway and explore selected published courses. An interdisciplinary education Your learning pathway Selected published courses Make a plan that fits"
 },
 {
  "title": "IBSC Student Association",
  "url": "student-life.html#association-panel",
  "text": "Meet peers, develop leadership skills and help shape campus life. The Student Association brings the IBSC community together through shared experiences. Connect, contribute and grow Student life in action Find your way to take part"
 },
 {
  "title": "Global opportunities",
  "url": "student-life.html#global-panel",
  "text": "Study abroad offers a different classroom, a new cultural perspective and a chance to put communication into practice. Start by understanding how an exchange works. What an exchange involves Prepare your application From nomination to departure Other international experiences"
 },
 {
  "title": "Service learning",
  "url": "student-life.html#service-panel",
  "text": "Service learning connects participation with reflection. Understand the hours, activity process and service log before you begin. Understand the requirement From activity to approved hours Write and submit your reflection"
 },
 {
  "title": "Careers and further study",
  "url": "resources.html#careers-panel",
  "text": "Communication skills travel across industries. Use your IBSC studies to explore the kinds of work, questions and professional environments that interest you. Explore your direction Connect study with professional experience Continue your learning Build a practical next step"
 },
 {
  "title": "Internships",
  "url": "resources.html#internships-panel",
  "text": "Connect what you study with the work of an organization. An internship is an opportunity to explore professional interests and develop through experience. Learning beyond the classroom Prepare for a conversation Make your learning visible Talk with the program"
 },
 {
  "title": "Yuan Ze University",
  "url": "about.html#university-panel",
  "text": "Yuan Ze University, Taoyuan, Taiwan. University information, academic community, location and contact."
 }
];
const menu = document.querySelector('#menu-dialog');
const search = document.querySelector('#search-dialog');
let lastTrigger;
function openDialog(dialog,trigger){lastTrigger=trigger;dialog.showModal();document.body.classList.add('locked');if(dialog===search) document.querySelector('#site-search').focus();}
document.querySelectorAll('[data-open-menu]').forEach(b=>b.addEventListener('click',()=>openDialog(menu,b)));
document.querySelectorAll('[data-open-search]').forEach(b=>b.addEventListener('click',()=>openDialog(search,b)));
document.querySelectorAll('dialog').forEach(d=>{
 d.querySelector('[data-close]').addEventListener('click',()=>d.close());
 d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}});
 d.addEventListener('close',()=>{document.body.classList.remove('locked');if(d.dataset.restoreFocus!=='false')lastTrigger?.focus();delete d.dataset.restoreFocus;});
});
const input=document.querySelector('#site-search');
const results=document.querySelector('#search-results');
function updateSearch(){
 const q=input.value.trim().toLowerCase();
 const found=searchData.filter(d=>!q||(d.title+' '+d.text).toLowerCase().includes(q));
 results.replaceChildren();
 const status=document.createElement('p');status.className='search-hint';status.textContent=q?`${found.length} ${found.length===1?'result':'results'} for “${input.value.trim()}”`:'Explore IBSC';results.append(status);
 found.forEach(d=>{const a=document.createElement('a');a.className='search-result';a.href=d.url;const h=document.createElement('h3');h.textContent=d.title;const p=document.createElement('p');p.textContent=d.text;a.append(h,p);results.append(a);});
 if(!found.length){const p=document.createElement('p');p.textContent='Try “curriculum”, “faculty”, “apply” or “student life”.';p.className='search-hint';results.append(p);}
}
input.addEventListener('input',updateSearch);updateSearch();

function revealInformation(hash,scroll=false,moveFocus=false,animate=true){
 let id;
 try{id=decodeURIComponent(hash.replace(/^#/,''));}catch{return;}
 const target=document.getElementById(id);
 if(!target)return;
 for(let element=target;element;element=element.parentElement){
  if(element.tagName==='DETAILS')element.open=true;
 }
 if(moveFocus){
  const focusTarget=target.tagName==='DETAILS'?target.querySelector('summary'):target;
  if(focusTarget.tagName!=='SUMMARY')focusTarget.tabIndex=-1;
  focusTarget.focus({preventScroll:true});
 }
 if(scroll){
  requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:animate&&!matchMedia('(prefers-reduced-motion: reduce)').matches?'smooth':'instant'}));
 }
}
document.addEventListener('click',event=>{
 const anchor=event.target.closest('a[href]');
 if(!anchor||anchor.classList.contains('skip')||event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
 const destination=new URL(anchor.href,location.href);
 const pagePath=path=>{const clean=path.replace(/\/+$/,'').replace(/\.html$/,'');return clean==='/index'||clean===''?'/':clean;};
 if(destination.origin!==location.origin||pagePath(destination.pathname)!==pagePath(location.pathname)||!destination.hash)return;
 let id;
 try{id=decodeURIComponent(destination.hash.slice(1));}catch{return;}
 if(!document.getElementById(id))return;
 event.preventDefault();
 document.querySelectorAll('dialog[open]').forEach(dialog=>{dialog.dataset.restoreFocus='false';dialog.close();});
 history.pushState(null,'',destination.hash);
 revealInformation(destination.hash,true,true);
});
window.addEventListener('hashchange',()=>revealInformation(location.hash,true));
window.addEventListener('popstate',()=>revealInformation(location.hash,true));
if(location.hash)revealInformation(location.hash);
window.addEventListener('load',()=>{if(location.hash)revealInformation(location.hash,true,false,false);},{once:true});
