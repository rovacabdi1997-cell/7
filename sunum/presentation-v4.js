/* Shared TV routes consume the same replay/API data and compiled component. */
(() => {
 const one=s=>document.querySelector(s), all=s=>Array.from(document.querySelectorAll(s));
 let selectedTV='1', lastSnapshot=null, records=[];
 const params=new URLSearchParams(location.search);
 const theme=()=>document.documentElement.dataset.tema==='koyu'?'koyu':'acik';
 function tvURL(){const p=new URLSearchParams({tema:theme()});const api=params.get('api');if(api&&/^https?:\/\/[^/?#]+$/.test(api))p.set('api',api);return '../tv/'+selectedTV+'/?'+p;}
 function setTV(id){selectedTV=id;one('#sharedTV').src=tvURL();all('[data-tv]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.tv===id)));}
 // Extend the existing feature panel mechanism, retaining all original products.
 hideFeaturePanels=()=>all('.capacity-panel,.feature-panel,#ecologyPanel,#layoutPanel,.v4-panel').forEach(p=>p.classList.add('hidden'));
 function openV4(name){openFeature(name,'#'+({tv:'tvPanel',workers:'workersPanel'})[name],true);all('#nav button').forEach(b=>b.classList.toggle('active',b.dataset.feature===name));if(name==='tv')setTV(selectedTV);}
 all('[data-feature]').forEach(b=>b.onclick=()=>{location.hash=b.dataset.feature;openV4(b.dataset.feature);});
 all('[data-tv]').forEach(b=>b.onclick=()=>setTV(b.dataset.tv));
 one('#startTV').onclick=()=>{location.hash='tv';openV4('tv');};
 const themeButton=document.createElement('button');themeButton.className='tema-button';themeButton.textContent=theme()==='koyu'?'Açyk tema':'Garaňky tema';
 themeButton.onclick=()=>{params.set('tema',theme()==='koyu'?'acik':'koyu');location.search=params.toString();};one('.header-right').prepend(themeButton);
 // Same names/order as each TV, read from the shared production snapshot.
 function showSnapshot(snapshot){snapshot=window.TgPresentation.presentationSnapshot(snapshot);lastSnapshot=snapshot;window.updatePresentationKPIs();const machines=snapshot.lines.flatMap(l=>l.equipment.map(e=>({...e,lineId:l.id})));const select=one('#workMachine'), previous=select.value;
  if(select.options.length!==machines.length){select.replaceChildren(...machines.map(e=>{const o=document.createElement('option');o.value=e.id;o.textContent=e.name+' · '+e.lineId;return o;}));if(machines.some(e=>e.id===previous))select.value=previous;}
  updateMachine();
  if(location.hash==='#tv'){const labels=snapshot.lines.find(l=>l.id===(selectedTV==='1'?'gipsokarton':'gury-garyndy'))?.equipment.filter(e=>e.kind!=='feed').map(e=>e.name);if(labels)one('#tvPanel').setAttribute('aria-label',labels.join(' → '));}
 }
 function updateMachine(){const id=one('#workMachine').value;const equipment=lastSnapshot?.lines.flatMap(l=>l.equipment).find(e=>e.id===id);const alarm=lastSnapshot?.alarms.find(a=>a.equipment===equipment?.name&&a.state!=='CLEARED');one('#machineSays').value=alarm?alarm.equipment+': '+alarm.message:'SIMULÝASIÝA · Işjeň näsazlyk ýok. Meýilleşdirilen gözegçilik.';}
 window.updatePresentationKPIs=()=>{
  const board=lastSnapshot?.lines.find(l=>l.id==='gipsokarton'),dry=lastSnapshot?.lines.find(l=>l.id==='gury-garyndy');
  const values={a:board?.outputToday.value,b:dry?.outputToday.value,kiln:null,oee:board?.efficiencyPct.value,power:null,alarms:lastSnapshot?.alarms.filter(a=>a.state!=='CLEARED').length};
  for(const [key,value] of Object.entries(values)){const el=one('[data-kpi="'+key+'"]');if(el)el.textContent=value==null?'—':fmtTk(value,key==='b'||key==='oee'?1:0);}
  const labels={a:['A BÖLÜMI · ŞU GÜN','m²'],b:['B BÖLÜMI · ŞU GÜN','t'],kiln:['BIŞIRIŞ · MAGLUMAT ÝOK','ÝOK'],oee:['LINIÝA NETIJELILIGI','%'],power:['ENERGIÝA · MAGLUMAT ÝOK','ÝOK']};
  for(const [key,[label,unit]] of Object.entries(labels)){const box=one('[data-kpi="'+key+'"]')?.closest('.kpi');if(box){box.querySelector('.label').textContent=label;box.querySelector('.unit').textContent=unit;}}
  one('#donutPower').textContent='—';one('#tagA').textContent='Maglumat ýok';
 };
 one('#workMachine').onchange=updateMachine;
 const api=params.get('api');
 if(api&&/^https?:\/\/[^/?#]+$/.test(api)) {const stream=new EventSource(api+'/api/stream');stream.addEventListener('snapshot',e=>{try{showSnapshot(JSON.parse(e.data));}catch{}});stream.onerror=()=>{one('#machineSays').value='Baglanyşyk ýok · Öňki maglumat täzelenmedi';};}
 else fetch('../replay/sunum.json').then(r=>{if(!r.ok)throw Error('replay');return r.json();}).then(cycle=>{function tick(){const d=new Date(Date.now()+5*3600000),second=(d.getUTCMinutes()*60+d.getUTCSeconds())%cycle.cycleSeconds;showSnapshot(cycle.snapshots[Math.floor(second/cycle.stepSeconds)%cycle.snapshots.length]);}tick();setInterval(tick,1000);}).catch(()=>{one('#machineSays').value='Maglumat ýok';one('#workForm button').disabled=true;});
 try{records=JSON.parse(localStorage.getItem('tg-work-cards-v4')||'[]');if(!Array.isArray(records))records=[];}catch{records=[];}
 function renderRecords(){const log=one('#workLog');log.replaceChildren();for(const r of records.slice().reverse()){const a=document.createElement('article');const title=document.createElement('b');title.textContent=[r.machineName,r.owner,r.state].join(' · ');const p=document.createElement('p');p.textContent=r.reply;const small=document.createElement('small');small.textContent='ÝERLI SYNAG · '+r.timestamp;a.append(title,p,small);log.append(a);}}
 one('#workForm').onsubmit=e=>{e.preventDefault();const equipment=lastSnapshot?.lines.flatMap(l=>l.equipment).find(m=>m.id===one('#workMachine').value);if(!equipment)return;
  const record={id:crypto.randomUUID?.()||String(Date.now()),assetId:equipment.id,machineName:equipment.name,sourceMode:equipment.mode,says:one('#machineSays').value,action:one('#workAction').value,owner:one('#workOwner').value,reply:one('#workReply').value.trim(),state:one('#workState').value,timestamp:new Date().toISOString(),dataMode:'LOCAL_DEMO'};
  if(!record.reply)return;const updated=[...records,record];try{localStorage.setItem('tg-work-cards-v4',JSON.stringify(updated));records=updated;renderRecords();one('#workResult').textContent='Ýerli demo karty saklandy.';one('#workReply').value='';}catch{one('#workResult').textContent='Ýazgy saklanmady. Brauzeriň ýady elýeterli däl.';}
 };
 one('#exportWork').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(records,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='turkmen-gips-yerli-demo-is-kartlary.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};renderRecords();
 // Worker edits stay explicitly marked; documentary source photos remain separate.
 const stageImages={1:'visuals/w1-operator-yas-uc.jpg',3:'visuals/w3-hil-barlag.jpg',4:'visuals/w2-bakim-guradyjy.jpg',5:'visuals/w4-torbalama.jpg',8:'visuals/w5-hat-yani-ekran.jpg'};
 const oldSelect=selectStage;selectStage=(i,manual=false)=>{oldSelect(i,manual);if(stageImages[current])one('#machineVideo').src=stageImages[current];};
 one('#introVideo').classList.add('intro-background');
 one('.silos').innerHTML=Array.from({length:9},(_,i)=>'<div class="silo"><small>1-005-'+(510+i*10)+'</small><em>ÝOK · dereje ölçegi ýok</em></div>').join('');
 function routeV4(){const name=location.hash.slice(1);if(['tv','workers'].includes(name))openV4(name);else{const p=one('.v4-panel:not(.hidden)');if(p)p.classList.add('hidden');}}
 window.addEventListener('hashchange',routeV4);routeV4();
 const schema=one('#schemaFrame')||one('.schema-frame');if(schema){const url=new URL(schema.getAttribute('src'),location.href);url.searchParams.set('tema',theme());schema.src=url.href;}
/*tg-duzeltme-2026-10-21*/
 (function(){
  const sev={CRITICAL:['red','MÖHÜM'],WARNING:['amber','DUÝDURYŞ'],INFO:['blue','MAGLUMAT']};
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const lineOf={'FM-01':'gipsokarton','A-01-07':'gipsokarton','A-01-09':'gipsokarton','A-01-12':'gipsokarton'};
  function metrics(s){
   if(!s)return null;const open=s.alarms.filter(a=>a.state!=='CLEARED');
   const id=(typeof stages!=='undefined'&&stages[current])?stages[current].id:'';const l=s.lines.find(x=>x.id===lineOf[id]);
   if(l)return [['Liniýanyň tizligi',fmtTk(l.speed.value,1)+' '+l.speed.unit],['Şu gün',fmtTk(l.outputToday.value,0)+' '+l.outputToday.unit],['Meýilnama',fmtTk(l.fulfilmentPct.value,1)+' %'],['Netijelilik',fmtTk(l.efficiencyPct.value,1)+' %'],['Duruşlar',fmtTk(l.stopsToday.value,0)+' sany'],['Işjeň waka',open.filter(a=>a.lineId===l.id).length+' sany']];
   const eq=s.lines.flatMap(x=>x.equipment);const a=s.lines.find(x=>x.id==='gipsokarton'),b=s.lines.find(x=>x.id==='gury-garyndy');
   return [['Işleýän enjam',eq.filter(e=>e.status==='RUNNING').length+' / '+eq.length],['A bölümi şu gün',a?fmtTk(a.outputToday.value,0)+' m²':'—'],['B bölümi şu gün',b?fmtTk(b.outputToday.value,1)+' t':'—'],['Işjeň waka',open.length+' sany'],['Maglumat','SIMULÝASIÝA'],['PLC-ä ýazma','Ýok']];
  }
  function paint(){
   const s=lastSnapshot;if(!s)return;
   const m=metrics(s),box=document.getElementById('metrics');
   if(m&&box)box.innerHTML=m.map(x=>'<div class="metric"><span>'+esc(x[0])+'</span><b>'+esc(x[1])+'</b></div>').join('');
   const open=s.alarms.filter(a=>a.state!=='CLEARED');
   const rows=document.getElementById('alarmRows');
   if(rows){const list=s.alarms.slice(0,4);rows.innerHTML=list.length?list.map(a=>{const v=sev[a.severity]||sev.INFO;return '<tr><td>'+esc(String(a.startedAt).slice(11,16))+'</td><td><span class="badge '+v[0]+'">'+v[1]+'</span></td><td>'+esc(a.equipment)+'</td><td>'+esc(a.message)+'</td></tr>';}).join(''):'<tr><td colspan="4">Waka ýok</td></tr>';}
   const w=document.getElementById('warning');
   if(w){const top=open.find(a=>a.severity==='CRITICAL')||open.find(a=>a.severity==='WARNING');
    w.classList.toggle('calm',!top);
    w.innerHTML=top?'<b>△ '+esc(top.equipment)+'</b><span>'+esc(top.message)+' · SIMULÝASIÝA</span>':'<b>✓ Işjeň duýduryş ýok</b><span>Ähli enjamlar kadaly işleýär · SIMULÝASIÝA</span>';}
   const st=document.getElementById('machineStatus');
   if(st)st.textContent=s.lines.some(l=>l.status==='FAULT')?'NÄSAZLYK':'IŞLEÝÄR';
  }
  const prevSelect=selectStage;selectStage=(i,manual=false)=>{prevSelect(i,manual);paint();};
  setInterval(paint,1000);
 })();

})();
