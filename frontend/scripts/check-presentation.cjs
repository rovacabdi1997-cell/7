const fs=require('fs'), ts=require('typescript'), assert=require('node:assert/strict');
const {join}=require('path');
const code=ts.transpileModule(fs.readFileSync(join(__dirname,'../features/data/presentation.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText;
const result={};new Function('exports',code)(result);
const adapt=result.presentationSnapshot;
const cycle=JSON.parse(fs.readFileSync(join(__dirname,'../public/replay/sunum.json'),'utf8'));
let checked=0;
for(const snapshot of cycle.snapshots){
 const original=JSON.stringify(snapshot), normalized=adapt(snapshot), line=normalized.lines.find(l=>l.id==='gipsokarton');
 assert.equal(JSON.stringify(snapshot),original,'source must be immutable');
 assert.deepEqual(adapt(normalized),normalized,'normalization must be idempotent');
 if(line){const keys=line.equipment.filter(e=>e.kind!=='feed').map(e=>e.assetKey), i=keys.indexOf('guradyjy');assert.deepEqual(keys.slice(i,i+4),['guradyjy','gyra-kesiji','bukjalayjy','gaplayjy']);
  const ids=new Set(line.equipment.map(e=>e.id));assert.equal(ids.size,line.equipment.length);assert(line.flow.every(f=>ids.has(f.fromId)&&ids.has(f.toId)));
  const real={...snapshot,lines:snapshot.lines.map(l=>({...l,mode:'HAKYKY'}))};assert.deepEqual(adapt(real),real,'never inject equipment in actual data');
 }
 checked++;
}
console.log(`${checked} replay snapshots passed: order, unique IDs, valid links, immutability, idempotence and real-data guard.`);
