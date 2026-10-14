import { existsSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
const walk=dir=>readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.name.startsWith('.')||['node_modules','_monorepo-source','outputs'].includes(e.name)?[]:e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
const count=(html,regex)=>[...html.matchAll(regex)].length;
function verifyStatic(directory,domain,repositoryDirectory=directory){
  const issues=[]; const warnings=[];
  if(!existsSync(path.join(directory,'index.html')))return {issues:['Missing index.html'],warnings,pages:0};
  for(const f of ['robots.txt','sitemap.xml'])if(!existsSync(path.join(directory,f)))issues.push('Missing '+f);
  const pages=walk(directory).filter(f=>f.endsWith('.html'));
  for(const file of pages){
    const html=readFileSync(file,'utf8'),label=path.relative(directory,file);
    const noindex=/content=["'][^"']*noindex/i.test(html)||/(^|\/)(404|offline)\.html$/.test(label);
    if(count(html,/<title\b/gi)!==1)issues.push(label+': title count');
    if(!noindex&&count(html,/<h1\b/gi)!==1)issues.push(label+': H1 count');
    if(count(html,/<footer\b/gi)!==1)issues.push(label+': footer count');
    if(!/<nav\b|<header\b/i.test(html))issues.push(label+': navigation missing');
    if(!noindex&&!/<meta\b[^>]*name=["']description["']/i.test(html))issues.push(label+': description missing');
    if(!noindex&&!/<link\b[^>]*rel=["']canonical["']/i.test(html))issues.push(label+': canonical missing');
    for(const m of html.matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi))try{JSON.parse(m[1]);}catch{issues.push(label+': invalid JSON-LD');}
    if(!noindex&&!/application\/ld\+json/i.test(html))warnings.push(label+': structured data missing');
    for(const m of html.matchAll(/\b(?:href|src)=["']([^"']+)["']/gi)){
      let ref=m[1].replace(/&amp;/g,'&').split(/[?#]/)[0];
      if(!ref||/^[a-z]+:|^\/\//i.test(ref))continue;
      try{ref=decodeURIComponent(ref);}catch{issues.push(label+': malformed local reference');continue;}
      const target=ref.startsWith('/')?path.resolve(directory,'.'+ref):path.resolve(path.dirname(file),ref);
      if(!(target===directory||target.startsWith(directory+path.sep))){issues.push(label+': reference escapes output '+ref);continue;}
      const functionTarget=ref.startsWith('/api/')&&existsSync(path.join(repositoryDirectory,'functions',ref.slice(1)+'.ts'));
      if(!functionTarget&&!existsSync(target)&&!existsSync(target+'.html')&&!existsSync(path.join(target,'index.html')))issues.push(label+': missing local target '+ref);
    }
  }
  const routes=new Set();const visited=new Set();
  function sitemap(file){
    if(visited.has(file)||!existsSync(file))return;visited.add(file);
    const xml=readFileSync(file,'utf8'),index=/<sitemapindex\b/i.test(xml);
    for(const m of xml.matchAll(/<loc>\s*([^<]+)\s*<\/loc>/g)){
      let url;try{url=new URL(m[1].replace(/&amp;/g,'&'));}catch{issues.push('Invalid sitemap URL');continue;}
      if(domain&&url.hostname!==domain&&url.hostname!=='www.'+domain){issues.push('Sitemap noncanonical host '+url.hostname);continue;}
      let pathname;try{pathname=decodeURIComponent(url.pathname);}catch{issues.push('Invalid encoded sitemap path');continue;}
      const target=path.resolve(directory,'.'+pathname);
      if(target!==directory&&!target.startsWith(directory+path.sep)){issues.push('Sitemap path escapes output');continue;}
      if(index)sitemap(target);
      else{routes.add(url.pathname);if(!existsSync(target)&&!existsSync(target+'.html')&&!existsSync(path.join(target,'index.html')))issues.push('Sitemap target missing '+url.pathname);}
    }
  }
  sitemap(path.join(directory,'sitemap.xml'));
  return {issues:[...new Set(issues)],warnings:[...new Set(warnings)],pages:pages.length,sitemapRoutes:[...routes]};
}
const result=verifyStatic(path.resolve(process.argv[2]),process.argv[3],process.cwd());
console.log(JSON.stringify(result,null,2));
if(result.issues.length)process.exitCode=1;
