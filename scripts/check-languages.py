#!/usr/bin/env python3
"""Check paired editions, language links, source URLs and complete archive lists."""
from pathlib import Path
from urllib.parse import urlsplit
import argparse,posixpath,re
from bs4 import BeautifulSoup
p=argparse.ArgumentParser();p.add_argument('repository',type=Path);root=p.parse_args().repository
soup=lambda rel:BeautifulSoup((root/rel).read_text(),'html.parser')
index=soup('Archives/index.html');files=['index.html','Archives/index.html']+['Archives/'+a['href'].split('/')[-1] for a in index.select('#list a')]
assert len(files)==32
for rel in files:
 fr,en=soup(rel),soup('en/'+rel)
 assert fr.html['lang']=='fr' and en.html['lang']=='en',rel
 assert len(en.select('.language-switch'))==1 and len(fr.select('.language-switch'))==1
 for lang,doc,url in [('fr',fr,'/'+rel),('en',en,'/en/'+rel)]:
  assert doc.select_one('.language-switch [aria-current="page"]')['lang']==lang
  for el in doc.select('a[href], link[href]'):
   href=el['href'];u=urlsplit(href)
   if u.scheme or href.startswith('#'):continue
   path=posixpath.normpath(posixpath.join(posixpath.dirname(url),u.path)).lstrip('/')
   assert (root/path).is_file(),(rel,href,path)
 if rel!='Archives/index.html':
  assert len(fr.select('article'))==len(en.select('article'))==6
  for a,b in zip(fr.select('article'),en.select('article')):
   assert [x['href'] for x in a.select('a[href]')]==[x['href'] for x in b.select('a[href]')],rel
  assert len(fr.select('.takeaway'))==len(en.select('.takeaway'))
  assert [a['href'] for a in fr.select('.bonus a')]==[a['href'] for a in en.select('.bonus a')]
 assert len(en.select('.translation-note'))==1
 assert 'Pour ajouter cette page' not in str(en)
 assert not en.select('.language-switch a[href*="/en/en/"]')
assert len(soup('en/Archives/index.html').select('#list li'))==30
print('PASS: 32 bilingual page pairs; 30 archives each; all local navigation and source links preserved.')
