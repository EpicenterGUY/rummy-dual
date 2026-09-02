// Optional dependency-free preview. GitHub Pages continues to serve index.html directly.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {boardFixture,layoutFixture} from '../tests/helpers/m0r-layout-fixture.mjs';
const root=path.resolve(import.meta.dirname,'..');
const args=process.argv.slice(2), option=(key,fallback)=>args.includes(key)?args[args.indexOf(key)+1]:fallback;
const port=Number(option('--port','4173')),host=option('--host','127.0.0.1');
http.createServer((req,res)=>{
  const url=new URL(req.url,'http://preview.local');
  res.setHeader('Cache-Control','no-store');
  if(url.pathname==='/qa/m0r'){
    res.setHeader('Content-Type','text/html; charset=utf-8');return res.end(layoutFixture());
  }
  if(url.pathname==='/qa/board'){
    res.setHeader('Content-Type','text/html; charset=utf-8');return res.end(boardFixture(fs.readFileSync(path.join(root,'index.html'),'utf8')));
  }
  // Serve only the game entry point; do not expose Git metadata or other workspace files.
  if(!['/','/index.html'].includes(url.pathname)){res.writeHead(404);return res.end('Not found')}
  res.setHeader('Content-Type','text/html; charset=utf-8');res.end(fs.readFileSync(path.join(root,'index.html')));
}).listen(port,host,()=>console.log(`Static preview ready on port ${port}`));
