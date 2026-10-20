const http=require('http'), fs=require('fs'), path=require('path');
const port=Number(process.env.PORT||3024);
// One site for both modes: recorded loop by default, live API when the address carries ?api=.
const root=path.resolve(__dirname,'site');
const mime={'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.pdf':'application/pdf','.txt':'text/plain; charset=utf-8','.woff2':'font/woff2','.webp':'image/webp','.mp4':'video/mp4','.ico':'image/x-icon'};
http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);return res.end();}
 let url;try{url=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400);return res.end();}
 let file=path.resolve(root,'.'+url);
 if(file!==root&&!file.startsWith(root+path.sep)){res.writeHead(403);return res.end();}
 if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
 if(!fs.existsSync(file)&&fs.existsSync(file+'.html'))file+='.html';
 if(!fs.existsSync(file)){res.writeHead(404);return res.end('Not found');}
 res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-cache'});
 if(req.method==='HEAD')return res.end();fs.createReadStream(file).pipe(res);
}).listen(port,'0.0.0.0',()=>console.log('Turkmen Gips v4 · http://localhost:'+port+'/sunum/TURKMEN-GIPS-BAKANLIK-SUNUMU.html'));
