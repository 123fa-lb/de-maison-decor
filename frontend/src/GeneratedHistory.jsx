import { useEffect, useMemo, useState } from 'react';
const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const panel = {background:'#191c22',border:'1px solid #30343d',borderRadius:14,padding:18};
const fmt = s => new Date(s).toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short'});
export default function GeneratedHistory(){
  const [images,setImages]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState('');
  async function load(){
    setLoading(true);setError('');
    try{
      const res=await fetch(`${API}/api/history/images?limit=500`,{credentials:'include'});
      if(!res.ok)throw new Error(`HTTP ${res.status}`);
      const data=await res.json();setImages(data.images||[]);
    }catch(e){setError(e.message||'Could not load image history');}
    finally{setLoading(false)}
  }
  useEffect(()=>{load()},[]);
  const groups=useMemo(()=>{
    const result=new Map();
    for(const im of images){const date=im.created_at.slice(0,10);if(!result.has(date))result.set(date,[]);result.get(date).push(im)}
    return [...result.entries()];
  },[images]);
  return <div style={{display:'grid',gap:18,color:'#f2ede5'}}>
    <section className="panel" style={{padding:24}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:12,flexWrap:'wrap'}}>
        <div><h2 style={{margin:0}}>Generated Images</h2><p style={{color:'#aeb5c2',margin:'8px 0 0'}}>Every generated image is saved automatically for 30 days, even if you never download it.</p></div>
        <button onClick={load} style={{background:'#24221e',color:'#e9c78d',border:'1px solid #4c4534',padding:'10px 16px',borderRadius:9,cursor:'pointer'}}>Refresh</button>
      </div>
      <p style={{color:'#aeb5c2',fontSize:12,marginTop:12}}>Images are removed automatically after 30 days. History starts with images generated after this update.</p>
      {loading&&<p>Loading history...</p>}
      {error&&<p style={{color:'#ef9a9a'}}>History error: {error}</p>}
      {!loading&&!error&&images.length===0&&<p style={{color:'#aeb5c2'}}>No saved images yet. Generate a new image to see it here.</p>}
    </section>
    {groups.map(([date,items])=><section key={date} className="panel" style={{padding:22}}>
      <h3 style={{margin:'0 0 16px',color:'#efd09c'}}>{new Date(date+'T12:00:00').toLocaleDateString('en-IN',{day:'numeric',month:'long',year:'numeric'})} <span style={{color:'#aeb5c2',fontSize:13,fontWeight:400}}>· {items.length} images</span></h3>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(175px,1fr))',gap:14}}>
        {items.map(im=><div key={im.id} style={{...panel,padding:10,minWidth:0}}>
          <img src={`${API}/api/history/images/${im.id}`} alt={`${im.category} ${im.sku}`} loading="lazy" style={{width:'100%',aspectRatio:'1/1',objectFit:'contain',background:'#0d0f12',borderRadius:9}}/>
          <div style={{padding:'10px 3px 3px'}}><strong style={{display:'block',overflowWrap:'anywhere',fontSize:13}}>{im.sku}</strong><div style={{color:'#aeb5c2',fontSize:12,textTransform:'capitalize',marginTop:5}}>{im.category} · {fmt(im.created_at)}</div>
            <a href={`${API}/api/history/images/${im.id}`} download={`${im.sku}_${im.category}.jpg`} style={{display:'inline-block',marginTop:11,color:'#e9c78d',fontSize:13}}>View / Download ↗</a>
          </div>
        </div>)}
      </div>
    </section>)}
  </div>
}
