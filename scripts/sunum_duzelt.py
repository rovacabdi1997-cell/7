"""Review fixes (2026-10-21) applied to the presentation source in sunum/.

Idempotent: running twice changes nothing. Every replacement must match exactly
once on the first run, otherwise the script stops before writing anything.
"""
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

SUNUM = Path(__file__).resolve().parent.parent / "sunum"
B = SUNUM / "TURKMEN-GIPS-BAKANLIK-SUNUMU.html"
A = SUNUM / "TURKMEN-GIPS-AKYM-SHEMASY.html"
J = SUNUM / "presentation-v4.js"
MARK = "/*tg-duzeltme-2026-10-21*/"


def rep(text, old, new, what, count=1):
    if old not in text and new in text:
        return text
    n = text.count(old)
    if n != count:
        sys.exit(f"{what}: beklenen {count}, bulunan {n}")
    return text.replace(old, new)


# ---------------------------------------------------------------- Bakanlık
b = B.read_text(encoding="utf-8")
if MARK not in b:
    # Y1 — Türkmence etiketler
    for old, new, what in [
        ("<small>SIMULATED · SANLY PANEL</small>", "<small>SIMULÝASIÝA · SANLY PANEL</small>", "açılış 1"),
        ("<small>A WE B BÖLÜMLERI · SIMULATED</small>", "<small>A WE B BÖLÜMLERI · SIMULÝASIÝA</small>", "açılış TV"),
        ("ÝERLI DEMO · SIMULATED", "ÝERLI SYNAG · SIMULÝASIÝA", "işgärler etiketi"),
        ('<div class="mode">● SIMULATED</div>', '<div class="mode">● SIMULÝASIÝA</div>', "üst rozet"),
        ('<i class="dot"></i> DEMO • SIMULÝASIÝA</div>', '<i class="dot"></i> SIMULÝASIÝA</div>', "üst durum"),
        ("EKOLOGIÝA • COMPLIANCE • RESMI ÇEŞME", "EKOLOGIÝA • KADALARA LAÝYKLYK • RESMI ÇEŞME", "ekologiýa"),
        ("DATA MODE • OFFICIAL_DOCUMENT", "ÇEŞME • RESMI RESMINAMA", "ekologiýa rozet"),
        ("DIGITAL TWIN • ZAWOD IÇI MEÝILNAMA", "SANLY EKIZ • ZAWOD IÇI MEÝILNAMA", "meýilnama"),
        ("eyebrow:'Mapping • Digital Twin'", "eyebrow:'Sanly karta • Sanly ekiz'", "aşama MAP"),
        ("aýratyn “ACTUAL” gatlagy", "aýratyn “HAKYKY ÖLÇEG” gatlagy", "ACTUAL"),
        ("commissioning wagtynda", "işe girizilende", "commissioning"),
        ("saklaýyş / store plasterboard meýdany", "saklaýyş meýdany", "store plasterboard"),
        ("20 million m² maksady", "20 mln m² maksady", "million"),
        ("Çevrimdışı işleýär · Modelleşdirilen maglumat · PLC ýazma ýok",
         "Internetsiz işleýär · SIMULÝASIÝA maglumatlary · PLC-ä ýazma ýok", "açılış notu"),
        ("ENJAMLAR · BAUMAK SANAWY · SANJIN", "ENJAMLAR · ZAWOD ENJAM SANAWY", "enjamlar başlık"),
        ("Kodlar Baumak enjam sanawyndan we Sanjin teklibinden alyndy", "Kodlar zawodyň enjam sanawyndan alyndy", "enjamlar notu"),
        ("A BÖLÜMI • SANJIN GIPSOKARTON HATY", "A BÖLÜMI • GIPSOKARTON HATY", "kuwwat A"),
        ("377 asset", "377 enjam", "asset"),
        ("<strong>ZONE:</strong>", "<strong>Zolak:</strong>", "ZONE"),
        ("<strong>ASSET:</strong>", "<strong>Enjam:</strong>", "ASSET"),
        ("<strong>ROUTE:</strong>", "<strong>Ugur:</strong>", "ROUTE"),
        ("<strong>SAFETY:</strong>", "<strong>Howpsuzlyk:</strong>", "SAFETY"),
        ("<strong>INVENTORY:</strong>", "<strong>Ammar:</strong>", "INVENTORY"),
        # Y3 — hukuki ad (alt bilgi + kapak)
        ("<div>TÜRKMEN GIPS • AKYLLY ZAWOD ULGAMY • PREZENTASIÝA V1.0</div>",
         "<div>“AK BULUT” HJ • TÜRKMEN GIPS • AKYLLY ZAWOD ULGAMY</div>", "alt bilgi"),
        ("<h1>TÜRKMEN GIPS</h1><h2>HOJALYK JEMGYÝETI • AKYLLY ZAWOD</h2>",
         "<h1>TÜRKMEN GIPS</h1><h2>HOJALYK JEMGYÝETI • AKYLLY ZAWOD</h2>"
         "<div class=\"legal-name\">“Ak Bulut” hojalyk jemgyýeti · Türkmen Gips markasy</div>", "kapak"),
    ]:
        b = rep(b, old, new, what)

    # Y2 — makine kartlarında tedarikçi yerine iç kod (A-01 …)
    # Gipsokarton cards carry supplier refs (Sanjin …, saha REF); dry-mix cards keep plant codes (1-005-…).
    b, n = re.subn(r"<i>(\d\d)</i><b>([^<]+)</b><small>(?!1-)[^<]*</small>",
                   r"<i>\1</i><b>\2</b><small>A-\1</small>", b)
    if n != 11:
        sys.exit(f"Sanjin kodları: beklenen 11, bulunan {n}")

    # K4 — senaryo düğmeleri kalkar; tek demo düzeni 6 dakikalık döngüdür.
    b, n = re.subn(r'<div class="footer-actions">.*?</div>', '<div class="footer-actions"></div>', b, count=1, flags=re.S)
    if n != 1:
        sys.exit("senaryo düğmeleri bulunamadı")

    # K1 — sabit olay tablosu ve uyarı: içerik canlı kayıttan dolar (presentation-v4.js).
    b, n = re.subn(r'(<tbody id="alarmRows">).*?(</tbody>)', r'\1\2', b, count=1, flags=re.S)
    if n != 1:
        sys.exit("alarmRows bulunamadı")

    css = (MARK +
           ".legal-name{margin:-4px 0 14px;font-size:13px;font-weight:800;letter-spacing:.04em;opacity:.8}"
           # K3 — boş "PDF AÇ" paneli: düğmeler kalan yüksekliği kaplamasın.
           ".layout-side{grid-template-rows:auto auto auto 1fr}"
           ".map-actions{align-self:start}"
           ".map-actions a,.map-actions button{display:flex;align-items:center;justify-content:center;min-height:42px;font-size:11px}"
           # Y7 — koyu modda uyarı kartı ve rozetler tema renginde.
           "html[data-tema=koyu] .warning,body.tema-koyu .warning{background:rgba(255,180,84,.08)!important;border-color:rgba(255,180,84,.35)!important;color:#EAF3F7!important}"
           ".warning.calm{background:rgba(30,158,106,.08)!important;border-color:rgba(30,158,106,.35)!important}"
           ".warning.calm b{color:#1E9E6A!important}")
    i = b.find("</style>")
    b = b[:i] + css + "\n" + b[i:]
    B.write_text(b, encoding="utf-8")
    print("Bakanlık: tamam")
else:
    print("Bakanlık: zaten düzeltilmiş")

# ------------------------------------------------------------ presentation-v4
j = J.read_text(encoding="utf-8")
if MARK not in j:
    j = rep(j, "'SIMULATED · Işjeň näsazlyk ýok. Meýilleşdirilen gözegçilik.'",
            "'SIMULÝASIÝA · Işjeň näsazlyk ýok. Meýilleşdirilen gözegçilik.'", "iş kartı metni")
    j = rep(j, "small.textContent='ÝERLI DEMO · '+r.timestamp", "small.textContent='ÝERLI SYNAG · '+r.timestamp", "iş kartı kaydı")
    # O9 — panel gizleme tek sınıf üzerinden; ölü güneş kaydı kalkar.
    j = rep(j, "all('#capacityPanel,#ecologyPanel,#layoutPanel,#machinesPanel,.v4-panel')",
            "all('.capacity-panel,.feature-panel,#ecologyPanel,#layoutPanel,.v4-panel')", "panel gizleme")
    j = rep(j, "solar:'solarPanel',", "", "güneş haritası")
    # K1 — olaylar, uyarı ve aşama metrikleri TV ile aynı kayıttan.
    live = MARK + r"""
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
"""
    # The script is one IIFE; the code must sit inside it to see lastSnapshot.
    end = j.rstrip().rfind("})();")
    if end == -1:
        sys.exit("presentation-v4.js: IIFE sonu bulunamadı")
    j = j[:end] + live + "\n" + j[end:]
    J.write_text(j, encoding="utf-8")
    print("presentation-v4.js: tamam")
else:
    print("presentation-v4.js: zaten düzeltilmiş")

# ------------------------------------------------------------- Akış şeması
a = A.read_text(encoding="utf-8")
if MARK not in a:
    a = rep(a, 'e.textContent="SIMULATED · SUNUM PROTOTIPI"', 'e.textContent="SIMULÝASIÝA · SUNUM NUSGASY"', "şema rozet")
    a = rep(a, "Modelleşdirilen maglumat · Sunum prototipi", "SIMULÝASIÝA · Sunum nusgasy", "şema çip")
    for old, new in [('s:"Control Tower"', 's:"Dolandyryş merkezi"'), ('s:"WMS"', 's:"Ammar ulgamy"'),
                     ('s:"CMMS"', 's:"Hyzmat ulgamy"'), ('s:"QMS"', 's:"Hil ulgamy"'), ('s:"WFM"', 's:"Işgär ulgamy"')]:
        a = rep(a, old, new, old)
    # K1 — şema göstergeleri Bakanlık ile aynı tanımlar; verisi olmayan gösterge yok.
    a = rep(a, '{k:"kiln",     l:"Peçiň debiti",           u:"t/sag",  d:1, base:24.6, spark:true, target:25},',
            '{k:"kiln",     l:"Işleýän enjam",          u:"",       d:0, base:17,   spark:true},', "KPI peç")
    a = rep(a, '{k:"oee",      l:"OEE · Samaralylyk",      u:"%",      d:1, base:78.4, spark:true},',
            '{k:"oee",      l:"A bölümi · netijelilik", u:"%",      d:1, base:91,   spark:true},', "KPI OEE")
    a = rep(a, '{k:"power",    l:"Häzirki kuwwat",         u:"MW",     d:2, base:4.12, spark:true},',
            '{k:"power",    l:"A bölümi · meýilnama",   u:"%",      d:1, base:97,   spark:true},', "KPI kuwwat")
    a = rep(a, 'new Date(2026,0,13,9,42,18+Math.floor(s)).toLocaleTimeString("tr-TR")',
            'new Date(Date.now()+5*3600e3).toISOString().slice(11,19)', "şema saati")
    bind = "<script>" + MARK + r"""
(function(){
 let snap=null;const orig=val;
 fetch('../replay/sunum.json').then(r=>r.json()).then(c=>{
  const pick=()=>{const d=new Date(Date.now()+5*3600e3),sec=(d.getUTCMinutes()*60+d.getUTCSeconds())%c.cycleSeconds;
   snap=c.snapshots[Math.floor(sec/c.stepSeconds)%c.snapshots.length];
   if(window.TgPresentation)snap=window.TgPresentation.presentationSnapshot(snap);
   const open=snap.alarms.filter(a=>a.state!=='CLEARED'),map={CRITICAL:'crit',WARNING:'warn',INFO:'ok'};
   SCEN.normal.events=open.length?open.map(a=>({t:String(a.startedAt).slice(11,16),s:map[a.severity]||'ok',src:a.lineId==='gipsokarton'?'A BÖLÜMI':'B BÖLÜMI',x:a.equipment+': '+a.message,m:'SIMULÝASIÝA'})):[{t:d.toISOString().slice(11,16),s:'ok',src:'ZAWOD',x:'Işjeň waka ýok. Ähli enjamlar kadaly işleýär.',m:'SIMULÝASIÝA'}];
   activeAlarms=renderFeed();};
  pick();setInterval(pick,1000);}).catch(()=>{});
 val=function(k){
  if(!snap)return orig(k);
  const a=snap.lines.find(l=>l.id==='gipsokarton'),b=snap.lines.find(l=>l.id==='gury-garyndy');
  switch(k.k){
   case 'boardOut':return a?a.speed.value*60*1.2:0;
   case 'powderOut':return b?b.speed.value:0;
   case 'kiln':return snap.lines.flatMap(l=>l.equipment).filter(e=>e.status==='RUNNING').length;
   case 'oee':return a?a.efficiencyPct.value:0;
   case 'power':return a?a.fulfilmentPct.value:0;
   case 'alarm':return snap.alarms.filter(x=>x.state!=='CLEARED').length;
  }
  return orig(k);};
})();
</script>
<style>.scen{display:none!important}</style>
<script src="shared-presentation.js"></script>"""
    i = a.rfind("</body>")
    if i == -1:
        i = len(a)  # the file has no body tags; append at the end
    a = a[:i] + bind + "\n" + a[i:]
    A.write_text(a, encoding="utf-8")
    print("Akış şeması: tamam")
else:
    print("Akış şeması: zaten düzeltilmiş")
