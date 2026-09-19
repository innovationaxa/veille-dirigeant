#!/usr/bin/env python3
"""Populate the English translation cache using a local Argos FR→EN CTranslate2 model.
No remote translation calls. Model directory must contain model/ and sentencepiece.model.
"""
import argparse,json,re
from pathlib import Path
from bs4 import BeautifulSoup,Comment
import ctranslate2,sentencepiece
p=argparse.ArgumentParser();p.add_argument('repository',type=Path);p.add_argument('--model',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);a=p.parse_args()
cache=json.loads(a.cache.read_text()) if a.cache.exists() else {}
index=BeautifulSoup((a.repository/'Archives/index.html').read_text(),'html.parser')
files=[a.repository/'index.html']+[a.repository/'Archives'/x['href'] for x in index.select('#list a')]
texts=set()
for path in files:
 soup=BeautifulSoup(path.read_text(),'html.parser');main=soup.select_one('main, .inner')
 for strong in main.find_all('strong'):strong.unwrap()
 main.smooth()
 for n in main.find_all(string=True):
  t=str(n).strip()
  if not isinstance(n,Comment) and re.search(r'[a-zÀ-ÿ]',t,re.I) and t not in cache:texts.add(t)
parts={t:re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ý«0-9])',t) for t in sorted(texts)}
segments=list(dict.fromkeys(x for v in parts.values() for x in v));results={}
sp=sentencepiece.SentencePieceProcessor(model_file=str(a.model/'sentencepiece.model'))
tr=ctranslate2.Translator(str(a.model/'model'),device='cpu',compute_type='int8',intra_threads=4)
for i in range(0,len(segments),48):
 batch=segments[i:i+48];tokens=[sp.encode(t,out_type=str) for t in batch]
 if any(len(t)>1024 for t in tokens):raise ValueError('Segment too long; split it before translation.')
 out=tr.translate_batch(tokens,beam_size=4,max_input_length=1024,max_decoding_length=1024)
 for src,dst in zip(batch,out):results[src]=''.join(dst.hypotheses[0]).replace('▁',' ').strip()
 print(f'{min(i+48,len(segments))}/{len(segments)}',flush=True)
for src,segs in parts.items():cache[src]=' '.join(results[x] for x in segs)
a.cache.parent.mkdir(parents=True,exist_ok=True);a.cache.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n')
