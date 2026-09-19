#!/usr/bin/env python3
"""Build static English pages from the 30 current French editions and reviewed cache.
Usage: python build-english.py REPOSITORY --cache PATH --overrides PATH
Requires beautifulsoup4. Missing translations fail instead of publishing mixed pages.
"""
import argparse, json, re, posixpath
from pathlib import Path
from bs4 import BeautifulSoup, Comment

ap=argparse.ArgumentParser();ap.add_argument('repository',type=Path);ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--overrides',type=Path,required=True)
args=ap.parse_args();root=args.repository
cache=json.loads(args.cache.read_text());cache.update(json.loads(args.overrides.read_text()))
ui={
 'FR':'FR','EN':'EN',
 'Ctrl + D':'Ctrl + D','⌘ + D':'⌘ + D',
 'Ajouter à mes favoris':'Add to bookmarks',
 'Pour ajouter cette page à vos favoris, appuyez sur':'To bookmark this page, press',
 '(Windows) ou':'(Windows) or','(Mac).':'(Mac).',
 'Sur mobile, ouvrez le menu de votre navigateur ou le menu de partage, puis choisissez « Ajouter aux favoris » ou l’étoile ☆.':'On mobile, open your browser or share menu, then choose “Add to bookmarks” or the star ☆.',
 '6 actus':'6 stories','pour comprendre demain, dès aujourd’hui.':'to understand tomorrow, today.',
 'pour l’essentiel':'for the essentials','pour tout lire':'for the full edition',
 'Chaque matin':'Every morning','mise à jour automatique':'automatically updated',
 'Ce que vous avez raté :':'In case you missed it:', 'Nos Archives':'Our Archives',
 '← Édition du jour':'← Today’s edition',
 'Retrouvez les 30 dernières éditions, de la plus récente à la plus ancienne.':'Browse the latest 30 editions, from newest to oldest.',
 'Une visite ou un workshop en équipe au Future Lab ?':'A team visit or workshop at the Future Lab?',
 'Demander une session':'Request a session','ou écrivez-nous à':'or email us at',
 'Diffusion interne':'Internal circulation','Diffusion interne.':'Internal circulation.',
 "Sélection et commentaires du Future Lab, sans valeur de position officielle. Sélection compilée chaque matin avec l'aide de l'IA sur les 24–48 dernières heures, priorité aux sources françaises et primaires ; chaque fait est lié à sa source et les chiffres non sourcés ne sont pas publiés. ·":"News selection and commentary by the Future Lab, not an official position. Compiled each morning with AI assistance from the previous 24–48 hours, prioritising French and primary sources; facts are linked to their sources and unsourced figures are not published. ·",
 'Consulter les éditions précédentes':'Browse previous editions','Lire l’édition du jour':'Read today’s edition','Proposer un sujet':'Suggest a topic',
 'powered by':'powered by','futurelab@axa.fr':'futurelab@axa.fr','×':'×',
}
attrs={'Fermer l’aide aux favoris':'Close bookmark help','À retenir':'Key takeaway','Éditions précédentes':'Previous editions','Votre rendez-vous de lecture':'Your reading guide','Navigation':'Navigation'}
months={'janvier':'January','février':'February','mars':'March','avril':'April','mai':'May','juin':'June','juillet':'July','août':'August','septembre':'September','octobre':'October','novembre':'November','décembre':'December'}
days={'Lundi':'Monday','Mardi':'Tuesday','Mercredi':'Wednesday','Jeudi':'Thursday','Vendredi':'Friday','Samedi':'Saturday','Dimanche':'Sunday'}
index=BeautifulSoup((root/'Archives/index.html').read_text(),'html.parser')
archives=['Archives/'+a['href'] for a in index.select('#list a')];assert len(archives)==30
files=['index.html','Archives/index.html']+archives
missing=set()
def date_en(t):
 for a,b in {**days,**months}.items(): t=re.sub(r'\b'+a+r'\b',b,t,flags=re.I)
 return t.replace('1er ','1 ')
def translate(t):
 if t in ui:return ui[t]
 if t in cache:return cache[t]
 if re.match(r'^(Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\b',t,re.I):return date_en(t)
 if not re.search(r'[A-Za-zÀ-ÿ]',t) or re.fullmatch(r'\d+ min',t):return t
 missing.add(t);return t

def switch(soup,rel,lang):
 for x in soup.select('.language-switch'):x.decompose()
 nav=soup.new_tag('nav',attrs={'class':'language-switch','aria-label':'Langue' if lang=='fr' else 'Language'})
 for code,label,url in [('fr','Français','/'+rel),('en','English','/en/'+rel)]:
  a=soup.new_tag('a',href=url,attrs={'lang':code,'hreflang':code,'aria-label':label});a.string=code.upper()
  if code==lang:a['aria-current']='page'
  nav.append(a)
 soup.select_one('.mast .top').append(nav)
 for el in soup.select('link[rel="alternate"][hreflang]'):el.decompose()
 for code,url in [('fr','/'+rel),('en','/en/'+rel)]:
  soup.head.append(soup.new_tag('link',rel='alternate',hreflang=code,href=url))
 if not soup.select_one('link[href="/assets/language.css"]'):
  soup.head.append(soup.new_tag('link',rel='stylesheet',href='/assets/language.css'))

outputs={}
for rel in files:
 src=(root/rel).read_text();fr=BeautifulSoup(src,'html.parser')
 switch(fr,rel,'fr');outputs[rel]=str(fr)
 en=BeautifulSoup(src,'html.parser');en.html['lang']='en'
 for strong in en.select('main strong, .inner strong'):strong.unwrap()
 en.smooth()
 for n in list(en.body.find_all(string=True)):
  if isinstance(n,Comment) or any(p.name in ['svg','style','script'] for p in n.parents):continue
  raw=str(n);t=raw.strip()
  if not t:continue
  translated=translate(t)
  n.replace_with(raw[:len(raw)-len(raw.lstrip())]+translated+raw[len(raw.rstrip()):])
 en.title.string='future.now — '+('Our Archives' if rel=='Archives/index.html' else '6 stories to understand tomorrow')
 for el in en.select('[aria-label]'):
  if el['aria-label'] in attrs:el['aria-label']=attrs[el['aria-label']]
 for el in en.select('[href]'):
  href=el['href']
  if href.startswith(('https:','http:','mailto:','#')):continue
  resolved=posixpath.normpath(posixpath.join(posixpath.dirname('/'+rel),href))
  if resolved.lstrip('/') in files:el['href']='/en'+resolved
  elif resolved.startswith('/assets/'):el['href']=resolved
 for script in en.find_all('script'):
  if script.get('id')=='cowork-artifact-meta':
   data=json.loads(script.string);data['description']='future.now — 6 stories to understand tomorrow, today. Powered by future.lab. English translation.';script.string=json.dumps(data,ensure_ascii=False)
  elif script.string:
   script.string=script.string.replace('Pour ajouter cette page à vos favoris, appuyez sur','To bookmark this page, press').replace(', puis confirmez dans votre navigateur.',', then confirm in your browser.')
 notice=en.new_tag('p',attrs={'class':'translation-note'})
 notice.append('Automatically translated from French. ')
 link=en.new_tag('a',href='/'+rel,attrs={'lang':'fr','hreflang':'fr'});link.string='Read the original';notice.append(link)
 first=en.select_one('.edtitle, .archive-title');first.insert_before(notice)
 switch(en,rel,'en')
 outputs['en/'+rel]=str(en)
if missing:
 print('MISSING',json.dumps(sorted(missing),ensure_ascii=False,indent=2));raise SystemExit(1)
for rel,html in outputs.items():
 target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html.rstrip()+'\n')
print(f'{len(files)} French pages with switch and {len(files)} English pages built.')
