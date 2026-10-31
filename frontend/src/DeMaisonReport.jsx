const authFetch = (url, options = {}) => fetch(url, { ...options, credentials: 'include' });
// DEMAISON_RESET_CSV_V3
// DEMAISON_SIMPLE_REPORT_V2
import {useEffect,useMemo,useState} from 'react';
const API=(import.meta.env.VITE_API_URL||'http://localhost:8000').replace(/\/$/,'');
const STORAGE='demaison-indian-balance-v1';
const money=(v,d=2)=>v==null||!Number.isFinite(v)?'—':'₹'+Number(v).toLocaleString('en-IN',{minimumFractionDigits:d,maximumFractionDigits:d});
const today=()=>{const d=new Date();return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`};
const safeStore=()=>{try{return JSON.parse(localStorage.getItem(STORAGE)||'null')}catch{return null}};
const csv=v=>{const str=String(v??'');const safe=/^[\s]*[=+@-]/.test(str)?'\''+str:str;return '"'+safe.replaceAll('"','""')+'"'};
const dayLabel=s=>new Date(s+'T12:00:00').toLocaleDateString('en-IN',{day:'numeric',month:'short'});
function downloadCsv(name,rows,periodLabel='Selected period',rangeLabel=''){
 const generated=rows.filter(r=>r.success);
 const known=generated.filter(r=>r.inr!=null&&Number.isFinite(r.inr));
 const unknown=generated.length-known.length;
 const total=known.reduce((sum,r)=>sum+r.inr,0);
 const folderMap=new Map();
 for(const r of rows){const sku=(r.sku||'Unassigned').trim()||'Unassigned';if(!folderMap.has(sku))folderMap.set(sku,[]);folderMap.get(sku).push(r)}
 const byDay=new Map();
 for(const r of rows){
  const date=r.date||'Unknown';
  if(!byDay.has(date))byDay.set(date,[]);
  byDay.get(date).push(r);
 }
 const endDate=rows.length?rows.map(r=>r.date).filter(Boolean).sort().at(-1):'';
 const startDate=rows.length?rows.map(r=>r.date).filter(Boolean).sort()[0]:'';
 const sheet=[
  ['DE MAISON DECOR — IMAGE USAGE REPORT'],
  ['Report period',periodLabel],['Selected date range',rangeLabel],['First recorded date',startDate],['Last recorded date',endDate],['Exported on',new Date().toLocaleString('en-IN')],
  ['Currency','INR (₹)'],['Cost basis','Estimated only — NOT actual Google billing'],
  ['Total requests',rows.length],['Generated images',generated.length],['Cost available for',known.length],
  ['Images with unknown cost',unknown],['Estimated total (₹)',unknown?'PARTIAL — '+total.toFixed(2):total.toFixed(2)],
  [],['DATE-WISE SUMMARY'],
  ['Date (YYYY-MM-DD)','Requests','Generated images','Unknown costs','Estimated total (₹)'],
  ...[...byDay.entries()].sort((a,b)=>a[0].localeCompare(b[0])).map(([date,rr])=>{
    const unknownCount=rr.filter(r=>r.success&&r.inr==null).length;
    const sum=rr.reduce((v,r)=>v+(Number.isFinite(r.inr)?r.inr:0),0);
    return [date,rr.length,rr.filter(r=>r.success).length,unknownCount,unknownCount?'PARTIAL — '+sum.toFixed(2):sum.toFixed(2)];
  }),
  [],['FOLDER-WISE SUMMARY'],
  ['Folder / SKU','Requests','Generated images','Unknown costs','Estimated total (₹)'],
  ...[...folderMap.entries()].map(([folder,rr])=>[folder,rr.length,rr.filter(r=>r.success).length,rr.filter(r=>r.success&&r.inr==null).length,rr.some(r=>r.success&&r.inr==null)?'PARTIAL — '+rr.reduce((v,r)=>v+(r.inr||0),0).toFixed(2):rr.reduce((v,r)=>v+(r.inr||0),0).toFixed(2)]),
  [],['INDIVIDUAL IMAGE REQUESTS'],
  ['Date (YYYY-MM-DD)','Recorded time','Folder / SKU','Image type','Attempt','Status','Input tokens','Output tokens','Estimated cost (₹)','Cost explanation'],
  ...rows.map(r=>[r.date,r.time,r.sku,r.category,r.variation,r.success?'Generated':'Failed',r.input_tokens,r.output_tokens,r.inr==null?'Unavailable':r.inr.toFixed(4),r.cost_status||'']),
 ];
 const content=sheet.map(row=>row.map(csv).join(',')).join('\r\n');
 const blob=new Blob(['\ufeff'+content],{type:'text/csv;charset=utf-8'});
 const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export default function DeMaisonReport(){
 const [data,setData]=useState(null),[error,setError]=useState(''),[loading,setLoading]=useState(false);
 const [period,setPeriod]=useState('7'),[end,setEnd]=useState(today());
 const [selected,setSelected]=useState(''),[saved,setSaved]=useState(safeStore);
 const [amount,setAmount]=useState('');
 const [fx,setFx]=useState(saved?.fx==null?'90':String(saved.fx));
 const [message,setMessage]=useState('');
 const [confirmDelete,setConfirmDelete]=useState(false);
 async function load(){setLoading(true);try{const r=await authFetch(`${API}/api/maison/report?days=365&_=${Date.now()}`,{cache:'no-store'});if(!r.ok)throw Error(`Backend error ${r.status}`);const j=await r.json();setData(j);setError('')}catch(e){setError(e.message)}finally{setLoading(false)}}
 useEffect(()=>{load();const timer=setInterval(load,15000);return()=>clearInterval(timer)},[]);
 const rate=Number(saved?.fx||fx)||0;
 const all=useMemo(()=>(data?.records||[]).map(r=>({...r,inr:r.estimated_cost_usd==null?null:Number(r.estimated_cost_usd)*rate})),[data,rate]);
 const filtered=useMemo(()=>{const days=Number(period);const date=new Date(end+'T12:00:00');date.setDate(date.getDate()-days+1);const start=`${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;return all.filter(r=>r.date>=start&&r.date<=end)},[all,end,period]);
 const groups=useMemo(()=>{const m=new Map();for(const r of filtered){const name=(r.sku||'Unassigned').trim()||'Unassigned';if(!m.has(name))m.set(name,[]);m.get(name).push(r)}return [...m.entries()].map(([name,rows])=>({name,rows,images:rows.filter(r=>r.success).length,cost:rows.reduce((s,r)=>s+(r.inr||0),0),unknown:rows.some(r=>r.success&&r.inr==null)})).sort((a,b)=>b.cost-a.cost)},[filtered]);
 const visible=groups.find(g=>g.name===selected);
 const known=filtered.reduce((s,r)=>s+(r.inr||0),0);
 const missing=filtered.filter(r=>r.success&&r.inr==null).length;
 const generated=filtered.filter(r=>r.success).length;
 const retries=filtered.filter(r=>Number(r.variation)>1).length;
 const later=all.filter(r=>saved&&Number(r.id)>Number(saved.baselineId));
 const laterUnknown=later.some(r=>r.success&&r.inr==null);
 const spent=later.reduce((s,r)=>s+(r.inr||0),0);
 const historyComplete=!saved||!data||!data.start_date||saved.savedAt.slice(0,10)>=data.start_date;
 const remaining=saved&&data&&!laterUnknown&&historyComplete?saved.amount-spent:null;
 function deleteBalance(){
  if(!confirmDelete){setConfirmDelete(true);setMessage('Confirm karne ke liye Delete Credits dobara dabao.');return}
  localStorage.removeItem(STORAGE);setSaved(null);setAmount('');setConfirmDelete(false);setMessage('Saved credits deleted. Report history safe hai.');
 }
 function refreshReport(){
  setEnd(today());setPeriod('7');setSelected('');setMessage('');setConfirmDelete(false);
  setAmount('');setError('');load();
}
 function saveBalance(){
  const a=Number(amount),r=Number(fx);
  if(!amount.trim()||!Number.isFinite(a)||a<0||!Number.isFinite(r)||r<=0){setMessage('Sahi balance aur conversion rate enter karo.');return}
  if(!data){setMessage('Pehle backend report load hone do.');return}
  const next={amount:a,fx:r,baselineId:Math.max(0,...all.map(x=>Number(x.id)||0)),savedAt:new Date().toISOString()};
  localStorage.setItem(STORAGE,JSON.stringify(next));setSaved(next);setAmount('');setSelected('');setConfirmDelete(false);setMessage('Balance save ho gaya. Ab nayi images ka estimated kharch track hoga.');
 }
 const chart=useMemo(()=>{const points=[];const days=Number(period);for(let i=days-1;i>=0;i--){const d=new Date(end+'T12:00:00');d.setDate(d.getDate()-i);const k=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;const rr=filtered.filter(r=>r.date===k);points.push({date:k,value:rr.reduce((s,r)=>s+(r.inr||0),0),count:rr.filter(r=>r.success).length})}return points},[end,period,filtered]);
 const max=Math.max(0.01,...chart.map(p=>p.value));
 const card={background:'#191c22',border:'1px solid #30343d',borderRadius:14,padding:'18px 20px'};
 const tiny={fontSize:12,color:'#aeb5c2'};
 const button={border:'1px solid #4c4534',borderRadius:9,background:'#24221e',color:'#e9c78d',padding:'10px 15px',cursor:'pointer'};
 const input={border:'1px solid #4b4f57',borderRadius:9,background:'#12151a',color:'#f5f2ec',padding:'10px 12px',maxWidth:'100%'};
 return <div style={{display:'grid',gap:20,color:'#f2ede5'}}>
  <section className="panel" style={{padding:24}}>
   <div style={{display:'flex',justifyContent:'space-between',gap:12,alignItems:'center',flexWrap:'wrap'}}><div><h2 style={{margin:0}}>Credits & Report</h2><p style={{margin:'8px 0 0',color:'#aeb5c2'}}>Credits, folder-wise image costs aur reports — sab ₹ mein.</p></div><span style={{...tiny}}>Auto refresh · 15 sec</span></div>
   <div style={{display:'flex',gap:12,alignItems:'end',flexWrap:'wrap',marginTop:20}}>
    <label style={{display:'grid',gap:7,flex:'1 1 180px',fontSize:13}}>Enter your credits (₹)<input style={input} type="number" min="0" step="0.01" placeholder="Enter amount in ₹" value={amount} onChange={e=>setAmount(e.target.value)}/></label>
    <button type="button" style={button} onClick={saveBalance}>Save Credits</button>
    {saved&&<button type="button" style={{...button,color:'#f1a6a6',borderColor:'#694545',background:'#281e20'}} onClick={deleteBalance}>{confirmDelete?'Confirm Delete':'Delete Credits'}</button>}
   </div>
   <details style={{marginTop:10,color:'#aeb5c2',fontSize:12}}><summary style={{cursor:'pointer'}}>Estimate settings</summary><div style={{display:'flex',gap:10,alignItems:'center',marginTop:9,flexWrap:'wrap'}}><span>1 USD ≈ ₹</span><input type="number" min="1" step="0.01" style={{...input,width:110}} value={fx} onChange={e=>setFx(e.target.value)}/><span>Ye estimated conversion hai, actual billed rate nahi. Rate badalne par Save Credits dabao.</span></div></details>
   {message&&<p style={{color:'#d6b77d',fontSize:12,marginTop:10}}>{message}</p>}
   <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))',gap:12,marginTop:20}}>
    <div style={card}><div style={tiny}>Starting balance</div><div style={{fontSize:28,color:'#efd09c',marginTop:10,fontWeight:600}}>{saved?money(saved.amount):'—'}</div></div>
    
    <div style={card}><div style={tiny}>Estimated remaining</div><div style={{fontSize:28,color:'#efd09c',marginTop:10,fontWeight:600}}>{money(remaining)}</div></div>
   </div>
   {saved&&<p style={{...tiny,marginTop:12}}>Last saved: {new Date(saved.savedAt).toLocaleString('en-IN')} · Balance badalne par naya amount enter karke Save Credits karo. {laterUnknown?'Kuch images ki cost unknown hai, isliye remaining unavailable hai.':''}</p>}
  </section>
  <section className="panel" style={{padding:24}}>
   <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:12,flexWrap:'wrap'}}><div><h2 style={{margin:0}}>Usage Report</h2><p style={{color:'#aeb5c2',margin:'8px 0 0'}}>Folder (SKU) par click karke har image ka estimated kharch dekho. Reset & Refresh se filters normal ho jayenge; history delete nahi hogi.</p></div></div>
   <div style={{display:'flex',gap:12,alignItems:'center',flexWrap:'wrap',margin:'20px 0'}}><label style={{display:'grid',gap:5,fontSize:12}}>Date<input type="date" value={end} onChange={e=>{setEnd(e.target.value);setSelected('')}} style={input}/></label><label style={{display:'grid',gap:5,fontSize:12}}>Report<select style={input} value={period} onChange={e=>{setPeriod(e.target.value);setSelected('')}}><option value="1">Daily</option><option value="7">7 Days</option><option value="30">30 Days</option></select></label><button style={{...button,alignSelf:'end'}} onClick={refreshReport}>Reset & Refresh</button></div>
   <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))',gap:12}}><div style={card}><div style={tiny}>Images</div><strong style={{fontSize:25}}>{generated}</strong></div><div style={card}><div style={tiny}>Folders / SKU</div><strong style={{fontSize:25}}>{groups.length}</strong></div><div style={card}><div style={tiny}>Estimated cost</div><strong style={{fontSize:25,color:'#efd09c'}}>{money(known)}</strong></div><div style={card}><div style={tiny}>Regenerations</div><strong style={{fontSize:25}}>{retries}</strong></div></div>
   <div style={{...card,marginTop:18}}><div style={{display:'flex',justifyContent:'space-between',gap:10,flexWrap:'wrap'}}><strong>Spending trend</strong><span style={tiny}>Estimated ₹ per day</span></div><div style={{height:170,display:'flex',alignItems:'end',gap:Math.max(3,14-Number(period)/3),marginTop:16,borderBottom:'1px solid #454951',paddingBottom:6}}>{chart.map(p=><div key={p.date} title={`${dayLabel(p.date)} · ${money(p.value)} · ${p.count} images`} style={{flex:1,minWidth:2,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'end',height:'100%',gap:5}}><div style={{...tiny,fontSize:Number(period)>7?9:11,whiteSpace:'nowrap'}}>{Number(period)<=7?money(p.value,1):''}</div><div style={{width:'100%',maxWidth:48,minHeight:p.value>0?4:2,height:`${p.value/max*125}px`,borderRadius:'5px 5px 0 0',background:p.value>0?'linear-gradient(180deg,#edcb8f,#a98448)':'#3b3d42'}}/><span style={{...tiny,fontSize:Number(period)>7?9:11}}>{Number(period)<=7?dayLabel(p.date):p.date.slice(-2)}</span></div>)}</div></div>
   {missing>0&&<p style={{color:'#e9b879',fontSize:12,marginTop:12}}>{missing} image(s) ki cost available nahi. Total sirf known estimates ka hai.</p>}
   <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:10,flexWrap:'wrap',margin:'22px 0 12px'}}><h3 style={{margin:0}}>Folder-wise spending</h3><span style={tiny}>Click to view images</span></div>
   <div style={{display:'grid',gap:9}}>{groups.map(g=><button key={g.name} type="button" onClick={()=>setSelected(selected===g.name?'':g.name)} style={{...card,width:'100%',textAlign:'left',color:'#f2ede5',cursor:'pointer',display:'flex',alignItems:'center',gap:14,justifyContent:'space-between',background:selected===g.name?'#27231d':'#191c22'}}><span style={{display:'flex',gap:12,alignItems:'center',minWidth:0}}><span style={{fontSize:22}}>▣</span><span style={{display:'grid',gap:4,minWidth:0}}><strong style={{overflowWrap:'anywhere'}}>{g.name}</strong><small style={tiny}>{g.images} images · {g.rows.length} requests</small></span></span><span style={{display:'flex',gap:12,alignItems:'center',flexShrink:0}}><strong style={{color:'#efd09c'}}>{g.unknown?'Partial · ':''}{money(g.cost)}</strong><span>{selected===g.name?'⌃':'⌄'}</span></span></button>)}{!groups.length&&<p style={{color:'#aeb5c2'}}>Is period mein koi recorded image nahi hai.</p>}</div>
   {visible&&<div style={{...card,marginTop:14}}><div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:10,flexWrap:'wrap'}}><div><h3 style={{margin:0}}>{visible.name} — Image Details</h3><p style={{...tiny,marginTop:6}}>Har image ka estimated kharch</p></div></div><div style={{overflowX:'auto',marginTop:12}}><table style={{width:'100%',borderCollapse:'collapse',fontSize:13}}><thead><tr>{['Date','Image type','Attempt','Status','Estimated cost'].map(h=><th key={h} style={{textAlign:'left',padding:10,borderBottom:'1px solid #42454b',color:'#d9b781'}}>{h}</th>)}</tr></thead><tbody>{visible.rows.map(r=><tr key={r.id}><td style={{padding:10,borderBottom:'1px solid #2e3239'}}>{r.date} {r.time}</td><td style={{padding:10,borderBottom:'1px solid #2e3239',textTransform:'capitalize'}}>{r.category}</td><td style={{padding:10,borderBottom:'1px solid #2e3239'}}>{r.variation||1}</td><td style={{padding:10,borderBottom:'1px solid #2e3239'}}>{r.success?'Generated':'Failed'}</td><td style={{padding:10,borderBottom:'1px solid #2e3239',color:'#efd09c'}}>{money(r.inr)}</td></tr>)}</tbody></table></div></div>}
   <p style={{...tiny,marginTop:18}}>Folder = recorded SKU name. Costs are estimates from recorded API usage and model pricing, converted at the saved USD/INR rate. Actual Google deductions, taxes, top-ups and other API activity can differ. Unknown costs are not silently counted as zero.</p>
   {error&&<p style={{color:'#ef9a9a'}}>Report error: {error}</p>}{loading&&!data&&<p>Loading report...</p>}
  </section>
 </div>;
}
