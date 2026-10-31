import AuthGate from './AuthGate';
import './auth.css';
// DEMAISON_V18_REVIEW_FIX
// DEMAISON_V17_REFERENCE_DELIVERABLE
// DEMAISON_ALL_GEMINI_V15
// DEMAISON_SINGLE_PHOTO_V11_2
// DEMAISON_CLIENT_FINAL_V10
import DeMaisonReport from './DeMaisonReport';
import GeneratedHistory from './GeneratedHistory';
import { useEffect, useMemo, useRef, useState } from 'react';
import JSZip from 'jszip';
import { UploadCloud, ImagePlus, FolderOpen, FileArchive, Package, ChevronRight, ArrowLeft, Plus, Minus, Download, Check, RefreshCw, BarChart3, Wallet, Layers3, AlertCircle, X, Search, ShieldCheck, Sparkles } from 'lucide-react';
import './index.css';

const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const CATEGORIES = [
  { key: 'white', title: 'White Background' }, { key: 'lifestyle', title: 'Lifestyle' },
  { key: 'infographic', title: 'Infographic' }, { key: 'dimension', title: 'Dimension' },
  { key: 'closeup', title: 'Close-up' },
];
const blankCounts = () => Object.fromEntries(CATEGORIES.map(c => [c.key, 0]));
const imgFile = name => /\.(jpe?g|png|webp)$/i.test(name) && !/(^|\/)(\.|__MACOSX)/.test(name);
const clean = name => String(name || 'Product').replace(/[\\/:*?"<>|\x00-\x1f]/g, '_').trim() || 'Product';
const display = value => Number(value || 0).toLocaleString('en-IN');
const readSaved = (key, fallback) => { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } };
function imageURL(blob) { return URL.createObjectURL(blob); }
function FileThumb({ file }) {
  const [url, setUrl] = useState('');
  useEffect(() => { if (!file) return; const u = imageURL(file); setUrl(u); return () => URL.revokeObjectURL(u); }, [file]);
  return url ? <img className="thumb" src={url} alt={file.name} /> : null;
}
function ErrorText({ value }) { return value ? <div className="error"><AlertCircle size={16} /> {value}</div> : null; }

// Read nested folders dropped from Chrome/Edge File Explorer. The relative path is retained.
async function droppedFiles(items) {
  const entries = Array.from(items || []).map(item => item.webkitGetAsEntry?.()).filter(Boolean);
  const files = [];
  async function walk(entry, prefix = '') {
    if (entry.isFile) {
      const file = await new Promise((resolve, reject) => entry.file(resolve, reject));
      files.push({ file, path: prefix + file.name });
    } else if (entry.isDirectory) {
      const reader = entry.createReader();
      for (;;) {
        const batch = await new Promise((resolve, reject) => reader.readEntries(resolve, reject));
        if (!batch.length) break;
        for (const child of batch) await walk(child, prefix + entry.name + '/');
      }
    }
  }
  for (const entry of entries) await walk(entry);
  return files;
}
async function unpackZip(file) {
  const zip = await JSZip.loadAsync(file);
  const entries = Object.values(zip.files).filter(e => !e.dir && imgFile(e.name));
  if (!entries.length) throw new Error('ZIP contains no supported product images.');
  const unpacked = [];
  for (const e of entries) {
    const data = await e.async('blob');
    unpacked.push({ file: new File([data], e.name.split('/').at(-1), { type: data.type || 'image/jpeg' }), path: e.name });
  }
  return unpacked;
}
function groupedProducts(entries, type) {
  const valid = entries.filter(item => imgFile(item.file.name));
  const paths = valid.map(item => item.path.replace(/\\/g, '/').split('/').filter(Boolean));
  const tops = new Set(paths.map(parts => parts[0]));
  const seconds = new Set(paths.filter(parts => parts.length >= 3).map(parts => parts[1]));
  // Accept "Collection/SKU/photos", "SKU/photos", or one SKU folder.
  const rootName = paths[0]?.[0] || '';
  const stripCollectionRoot = type !== 'single' && tops.size === 1 &&
    paths.some(parts => parts.length >= 3) &&
    !paths.some(parts => parts.length === 2);
  const groups = new Map();
  for (let i = 0; i < valid.length; i++) {
    const item = valid[i];
    const parts = paths[i];
    const sku = type === 'single' ? item.file.name.replace(/\.[^.]+$/, '')
      : stripCollectionRoot ? (parts[1] || parts[0]) : parts[0];
    const key = clean(sku);
    if (!groups.has(key)) groups.set(key, {
      id: crypto.randomUUID(), sku: key, files: [], counts: blankCounts(),
      dimensions: { width: '', height: '', depth: '', unit: 'cm' }, note: '', selected: true
    });
    groups.get(key).files.push(item.file);
  }
  return [...groups.values()];
}

const authFetch = async (url, options = {}) => {
  const response = await fetch(url, { ...options, credentials: 'include' });
  if (response.status === 401) window.dispatchEvent(new Event('maison-auth-expired'));
  return response;
};

function StudioApp({ onLogout }) {
  const imageRef = useRef(null), folderRef = useRef(null), zipRef = useRef(null);
  const [page, setPage] = useState('create'), [step, setStep] = useState(1);
  const [batchName, setBatchName] = useState('New Collection');
  const [products, setProducts] = useState([]), [results, setResults] = useState([]);
  const [query, setQuery] = useState(''), [uploading, setUploading] = useState(false), [dragging, setDragging] = useState(false);
  const [working, setWorking] = useState(false), [message, setMessage] = useState(''), [error, setError] = useState('');
  const [progress, setProgress] = useState({ done: 0, total: 0 });
  const [usage, setUsage] = useState({}), [usageHistory, setUsageHistory] = useState(() => readSaved('dmd_usage_report_v1', []));
  const [balance, setBalance] = useState(() => readSaved('dmd_balance_v1', { amount: '', date: '' }));
  const [balanceEdit, setBalanceEdit] = useState(''), [confirm, setConfirm] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const selected = products.filter(p => p.selected);
  const total = selected.reduce((s, p) => s + Object.values(p.counts).reduce((a, v) => a + v, 0), 0);
  const approved = results.filter(r => r.approved);
  const completed = progress.total > 0 && progress.done === progress.total && !working;
  const visible = useMemo(() => products.filter(p => p.sku.toLowerCase().includes(query.toLowerCase())), [products, query]);
  async function refreshUsage() { try { const r = await authFetch(`${API}/api/maison/usage`); if (!r.ok) throw Error(); setUsage(await r.json()); } catch { setUsage(old => ({ ...old, offline: true })); } }
  useEffect(() => { refreshUsage(); }, []);
  useEffect(() => { localStorage.setItem('dmd_usage_report_v1', JSON.stringify(usageHistory)); }, [usageHistory]);
  useEffect(() => { localStorage.setItem('dmd_balance_v1', JSON.stringify(balance)); }, [balance]);
  useEffect(() => () => { results.forEach(r => URL.revokeObjectURL(r.url)); }, []);
  function configure(entries, type, label) {
    const ps = groupedProducts(entries, type);
    if (!ps.length) throw new Error('No JPG, PNG or WEBP images found.');
    results.forEach(r => URL.revokeObjectURL(r.url));
    setProducts(ps); setResults([]); setProgress({ done: 0, total: 0 }); setBatchName(label || 'Product Collection');
    setPage('create'); setStep(2); setMessage(`${ps.length} SKU${ps.length === 1 ? '' : 's'} imported.`);
  }
  async function handleImport(files, type, items) {
    setUploading(true); setError('');
    try {
      let entries = [];
      if (type === 'zip') { const file = files[0]; if (!file) return; entries = await unpackZip(file); }
      else if (type === 'drop' && items?.length) {
        entries = await droppedFiles(items);
        if (!entries.length) entries = files.map(f => ({ file: f, path: f.webkitRelativePath || f.name }));
      } else entries = files.map(file => ({ file, path: file.webkitRelativePath || file.name }));
      const mode = type === 'single' ? 'single' : 'batch';
      configure(entries, mode, type === 'zip' ? files[0].name.replace(/\.zip$/i, '') : 'Product Collection');
    } catch (e) { setError(e.message || 'Import failed.'); }
    finally { setUploading(false); }
  }
  function patch(id, data) { setProducts(prev => prev.map(p => p.id === id ? { ...p, ...data } : p)); }
  function quantity(id, key, delta) { setProducts(prev => prev.map(p => p.id === id ? { ...p, counts: { ...p.counts, [key]: Math.max(0, Math.min(30, p.counts[key] + delta)) } } : p)); }
  function applyPreset(type) { const counts = type === 'A' ? { white: 4, lifestyle: 1, infographic: 1, dimension: 1, closeup: 1 } : { white: 4, lifestyle: 1, infographic: 1, dimension: 1, closeup: 1 }; setProducts(prev => prev.map(p => p.selected ? { ...p, counts: { ...counts } } : p)); }
  function validate() {
    if (!selected.length) return 'Select at least one SKU.';
    if (!total) return 'Set at least one image quantity.';
    // V11.2: one genuine reference photo is enough to request AI-generated views.
    // Do not misrepresent unseen surfaces as guaranteed physically accurate.
    for (const p of selected) {
      if (!p.files.length) return `SKU ${p.sku}: upload at least one genuine product photo.`;
      if (Number(p.counts.dimension || 0) > 0 && ['width', 'height'].some(k => !(Number(p.dimensions[k]) > 0)))
        return `Enter real Length and Height for ${p.sku}. Breadth is optional.`;
    }
    return '';
  }

  async function requestImage(p, type, number) {
    // DEMAISON_CLIENT_FINAL_V10: front / side / top / three-quarter order.
    const form = new FormData();
    const ranked = [...p.files].sort((a, b) => {
      const rank = f => {
        const n = f.name.toLowerCase();
        if (/front|^1[._ -]/.test(n)) return 1;
        if (/side|^2[._ -]/.test(n)) return 2;
        if (/top|^3[._ -]/.test(n)) return 3;
        if (/angle|three.?quarter|45degree|opposite|^4[._ -]/.test(n)) return 4;
        return 99;
      };
      return rank(a) - rank(b);
    });
    // V11.2: prefer a matching supplied angle, but accept just one photo.
    const preferred = type === 'white' && ranked.length >= number ? ranked[number - 1] : ranked[0];
    const sourceFiles = preferred ? [preferred, ...ranked.filter(f => f !== preferred)] : [];
    sourceFiles.slice(0, 6).forEach(f => form.append('files', f, f.name));
    form.append('category', type); form.append('sku', p.sku); form.append('note', p.note);
    ['width', 'height', 'depth', 'unit'].forEach(k => form.append(k, p.dimensions[k] || (k === 'unit' ? 'cm' : '')));
    form.append('variation', String(number));
    const r = await authFetch(`${API}/api/studio/generate`, { method: 'POST', body: form });
    if (!r.ok) { const detail = await r.json().catch(() => ({})); throw new Error(`Image creation request failed (HTTP ${r.status}). Check backend logs.`); }
    return r.blob();
  }
  async function composeFromWhite(p, type, heroBlob) {
    // DEMAISON_CLIENT_FINAL_V10: local Pillow composition, ZERO Gemini credits.
    const form = new FormData();
    form.append('file', heroBlob, 'source.jpg');
    form.append('category', type);
    form.append('sku', p.sku);
    ['width', 'height', 'depth', 'unit'].forEach(k => form.append(k, p.dimensions[k] || (k === 'unit' ? 'cm' : '')));
    const r = await authFetch(`${API}/api/studio/compose-local`, { method: 'POST', body: form });
    if (!r.ok) throw new Error(`Local ${type} layout failed (HTTP ${r.status}); no Gemini call was made.`);
    return r.blob();
  }

  async function generate() {
    const problem = validate(); if (problem) { setError(problem); setConfirm(false); setStep(2); return; }
    setConfirm(false); setWorking(true); setStep(3); setError(''); setResults([]); setProgress({ done: 0, total });
    const made = []; const log = []; let done = 0;
    generationLoop: for (const p of selected) for (const cat of [...CATEGORIES].sort((a,b) =>
      ({white:1,dimension:2,infographic:3,closeup:4,lifestyle:5}[a.key] || 99) -
      ({white:1,dimension:2,infographic:3,closeup:4,lifestyle:5}[b.key] || 99))) for (let i = 1; i <= p.counts[cat.key]; i++) {
      setMessage(`${p.sku} · ${cat.title} · ${i}/${p.counts[cat.key]}`);
      const before = await authFetch(`${API}/api/maison/usage`).then(r => r.ok ? r.json() : null).catch(() => null);
      let success = false;
      try {
        const blob = await requestImage(p, cat.key, i);
        const item = { id: crypto.randomUUID(), productId: p.id, sku: p.sku, category: cat.key, categoryTitle: cat.title, number: i, blob, url: imageURL(blob), approved: false };
        made.push(item); setResults([...made]); success = true;
      } catch (e) { log.push(`${p.sku} / ${cat.title}: ${e.message}`); setError(log.join(' | ')); break generationLoop; }
      const after = await authFetch(`${API}/api/maison/usage`).then(r => r.ok ? r.json() : null).catch(() => null);
      const row = { id: crypto.randomUUID(), date: new Date().toLocaleString(), sku: p.sku, category: cat.title, image: i, success,
        requests: before && after ? Math.max(0, (after.requests || 0) - (before.requests || 0)) : null,
        inputTokens: before && after ? Math.max(0, (after.input_tokens || 0) - (before.input_tokens || 0)) : null,
        outputTokens: before && after ? Math.max(0, (after.output_tokens || 0) - (before.output_tokens || 0)) : null };
      setUsageHistory(prev => [row, ...prev].slice(0, 2000)); done++; setProgress({ done, total });
    }
    setWorking(false); setStep(4); setMessage(`${made.length} images created. ${log.length} failed. Review before export.`); refreshUsage();
  }
  async function regenerate(item) {
    if (working) return; const p = products.find(p => p.id === item.productId); if (!p) return;
    setWorking(true); setError('');
    const before = await authFetch(`${API}/api/maison/usage`).then(r => r.ok ? r.json() : null).catch(() => null);
    let success = false;
    try { const blob = await requestImage(p, item.category, item.number); const url = imageURL(blob);
      setResults(old => old.map(r => r.id === item.id ? { ...r, blob, url, approved: false } : r));
      // Keep old URL alive until after state change so displayed image does not flash.
      setTimeout(() => URL.revokeObjectURL(item.url), 1000); success = true;
    } catch (e) { setError(e.message); }
    const after = await authFetch(`${API}/api/maison/usage`).then(r => r.ok ? r.json() : null).catch(() => null);
    setUsageHistory(prev => [{ id: crypto.randomUUID(), date: new Date().toLocaleString(), sku: p.sku, category: item.categoryTitle + ' (retry)', image: item.number, success,
      requests: before && after ? Math.max(0, (after.requests || 0) - (before.requests || 0)) : null,
      inputTokens: before && after ? Math.max(0, (after.input_tokens || 0) - (before.input_tokens || 0)) : null,
      outputTokens: before && after ? Math.max(0, (after.output_tokens || 0) - (before.output_tokens || 0)) : null }, ...prev].slice(0, 2000));
    setWorking(false); refreshUsage();
  }
  function downloadOne(item) { const a = document.createElement('a'); a.href = item.url; a.download = `${clean(item.sku)}_${item.category}_${String(item.number).padStart(2, '0')}.jpg`; a.click(); }
  async function exportZip() {
    const zip = new JSZip();
    for (const p of selected) {
      const own = approved.filter(r => r.productId === p.id);
      // Every SKU gets its own directory; categories have separate numbered image sets.
      // DEMAISON_EXACT_V5: flat, deterministic numbering per SKU.
      const ordered = [...own].sort((a, b) => {
        const ac = CATEGORIES.findIndex(c => c.key === a.category);
        const bc = CATEGORIES.findIndex(c => c.key === b.category);
        return ac - bc || a.number - b.number;
      });
      ordered.forEach((r, i) => zip.file(`${clean(p.sku)}/${i + 1}.jpg`, r.blob));
    }
    const out = await zip.generateAsync({ type: 'blob' }); const url = imageURL(out);
    const a = document.createElement('a'); a.href = url; a.download = `${clean(batchName)}_Approved_Images.zip`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 3000);
  }
  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><img src="/de-maison-logo.png" alt="De Maison Decor logo" /><div><strong>DE MAISON DECOR</strong><small>IMAGE CREATION</small></div></div>
      <div className="nav-label">WORKSPACE</div>
      <button className={`nav ${page === 'create' ? 'active' : ''}`} onClick={() => setPage('create')}><ImagePlus size={18} /> Image Creation</button>
      <button className={`nav ${page === 'usage' ? 'active' : ''}`} onClick={() => { setPage('usage'); refreshUsage(); }}><BarChart3 size={18} /> Credits & Report</button>
      <button type="button" className={`nav ${page === 'history' ? 'active' : ''}`} onClick={() => setPage('history')}>▧ &nbsp; Generated Images</button>
      <button type="button" className="ma-logout" onClick={onLogout} aria-label="Log out of De Maison Decor"><span aria-hidden="true">↪</span> Logout</button>
    </aside>
    <main className="main">
      <header className="top"><div className="mobile-brand"><img src="/de-maison-logo.png" alt="" /> DE MAISON DECOR</div><span className="top-context">IMAGE CREATION WORKSPACE</span><button type="button" className="ma-logout-mobile" onClick={onLogout} aria-label="Log out">Logout</button></header>
      <div className="container">
        <div className="heading"><div><div className="eyebrow">DE MAISON DECOR / STUDIO</div><h1>{page === 'history' ? 'Generated Images' : page === 'usage' ? 'Credits & usage report' : 'Image Creation'}</h1><p>{page === 'history' ? 'All generated images, saved automatically for 30 days.' : page === 'usage' ? 'Generation activity, recorded tokens and billing balance.' : 'Create professional product images, organized beautifully by SKU.'}</p></div></div>
        {page === 'history' ? <GeneratedHistory /> : page === 'usage' ? <DeMaisonReport /> : <>
          <div className="stepbar"><span className={step >= 1 ? 'on' : ''}>01 Upload</span><ChevronRight size={15} /><span className={step >= 2 ? 'on' : ''}>02 Configure</span><ChevronRight size={15} /><span className={step >= 3 ? 'on' : ''}>03 Create</span><ChevronRight size={15} /><span className={step >= 4 ? 'on' : ''}>04 Download</span></div>
          {step === 1 && <div className="upload-layout">
            <section className="panel"><div className="section-kicker">SINGLE PRODUCT</div><h2>One image</h2><p>Upload one product photo to request the full 8-image set. Additional angles are optional.</p><button className="upload-single" disabled={uploading} onClick={() => imageRef.current?.click()}><ImagePlus size={27} /><span>Choose product image</span><small>JPG, PNG or WEBP</small></button><input ref={imageRef} type="file" hidden accept="image/jpeg,image/png,image/webp" onChange={e => { const f = [...e.target.files]; e.target.value = ''; handleImport(f, 'single'); }} /></section>
            <section className="panel batch-panel"><div className="section-kicker">MULTIPLE PRODUCTS</div><h2>SKU folder or ZIP</h2><p>Each SKU subfolder is treated as a separate product. Generated images return to the corresponding SKU folder.</p>
              <div className={`dropzone ${dragging ? 'dragging' : ''}`} onDragOver={e => { e.preventDefault(); setDragging(true); }} onDragLeave={e => { e.preventDefault(); setDragging(false); }} onDrop={e => { e.preventDefault(); setDragging(false); const files = Array.from(e.dataTransfer.files); if (files.length === 1 && /\.zip$/i.test(files[0].name)) handleImport(files, 'zip'); else handleImport(files, 'drop', e.dataTransfer.items); }}><UploadCloud size={31} /><strong>Drag & drop your folder or ZIP</strong><small>Or choose one of the options below</small><div className="drop-actions"><button disabled={uploading} onClick={() => folderRef.current?.click()}><FolderOpen size={16} /> Select folder</button><button disabled={uploading} onClick={() => zipRef.current?.click()}><FileArchive size={16} /> Select ZIP</button></div></div>
              <input ref={folderRef} type="file" hidden multiple webkitdirectory="" directory="" onChange={e => { const f = [...e.target.files]; e.target.value = ''; handleImport(f, 'folder'); }} /><input ref={zipRef} type="file" accept=".zip,application/zip" hidden onChange={e => { const f = [...e.target.files]; e.target.value = ''; handleImport(f, 'zip'); }} />
            </section><div className="notice full"><ShieldCheck size={18} /> Original images remain unchanged. The final ZIP contains one folder per SKU, with images numbered directly inside each SKU folder.</div></div>}
          {step === 2 && <><div className="section-top"><div><h2>Configure image creation</h2><p>{products.length} SKU(s) imported · {total} images selected</p></div><button className="secondary" onClick={() => setStep(1)}><ArrowLeft size={16} /> Change upload</button></div>
            <div className="toolbar"><div className="presets"><button onClick={() => applyPreset('A')}>Client preset: 8 / SKU <small>4 white + 4 others</small></button><button onClick={() => applyPreset('B')}>Client preset B <small>8 / SKU</small></button></div><div className="search"><Search size={17} /><input placeholder="Find SKU" value={query} onChange={e => setQuery(e.target.value)} /></div></div>
            <div className="sku-list">{visible.map(p => <section className="sku-card" key={p.id}><div className="sku-header"><label className="sku-title"><input type="checkbox" checked={p.selected} onChange={e => patch(p.id, { selected: e.target.checked })} /><span className="sku-icon"><Package size={19} /></span><span><strong>{p.sku}</strong><small>{p.files.length} original photo(s)</small></span></label><b>{Object.values(p.counts).reduce((s, n) => s + n, 0)} images</b></div><div className="thumbs">{p.files.slice(0, 5).map((f, i) => <FileThumb key={`${p.id}-${i}`} file={f} />)}{p.files.length > 5 && <span>+{p.files.length - 5}</span>}</div><div className="qty-grid">{CATEGORIES.map(c => <div className="qty" key={c.key}><span>{c.title}</span><div className="count"><button onClick={() => quantity(p.id, c.key, -1)} aria-label={`Decrease ${c.title}`}><Minus size={14} /></button><strong>{p.counts[c.key]}</strong><button onClick={() => quantity(p.id, c.key, 1)} aria-label={`Increase ${c.title}`}><Plus size={14} /></button></div></div>)}</div><div className="sku-extras"><label>Special instructions<input value={p.note} placeholder="Optional product-specific instructions" onChange={e => patch(p.id, { note: e.target.value })} /></label><div className="dimension"><span>Dimensions (needed only for Dimension images)</span><div>{[{ key: 'width', label: 'Length (L)' }, { key: 'depth', label: 'Breadth (B)' }, { key: 'height', label: 'Height (H)' }].map(({ key, label }) => <input key={key} type="number" step="any" min="0" value={p.dimensions[key]} placeholder={label} onChange={e => patch(p.id, { dimensions: { ...p.dimensions, [key]: e.target.value } })} />)}<select value={p.dimensions.unit} onChange={e => patch(p.id, { dimensions: { ...p.dimensions, unit: e.target.value } })}><option value="cm">cm</option><option value="mm">mm</option><option value="in">in</option></select></div></div></div></section>)}</div>
            <div className="bottom-actions"><span>{selected.length} SKUs · {total} requested images</span><button className="primary" onClick={() => { const issue = validate(); if (issue) setError(issue); else { setError(''); setConfirm(true); } }}><Sparkles size={17} /> Create {total} images</button></div></>}
          {step === 3 && <section className="progress-panel"><div className="pulse"><Sparkles size={30} /></div><h2>{working ? 'Creating your images' : 'Generation finished'}</h2><p>{message}</p><strong>{progress.done} / {progress.total}</strong><progress value={progress.done} max={progress.total || 1} /><small>Keep this tab open until complete.</small>{completed && <button className="primary" onClick={() => setStep(4)}>Review images <ChevronRight size={16} /></button>}</section>}
          {step === 4 && <><div className="section-top"><div><h2>Review & download</h2><p>{approved.length} approved / {results.length} created · {message}</p></div><div className="review-btns"><button className="secondary" onClick={() => setResults(prev => prev.map(r => ({ ...r, approved: true })))} disabled={!results.length}>Approve all</button><button className="primary" onClick={exportZip} disabled={!approved.length}><Download size={16} /> Download SKU ZIP ({approved.length})</button></div></div>
            <div className="filterline"><button className={categoryFilter === 'all' ? 'chosen' : ''} onClick={() => setCategoryFilter('all')}>All images</button>{CATEGORIES.map(c => <button key={c.key} className={categoryFilter === c.key ? 'chosen' : ''} onClick={() => setCategoryFilter(c.key)}>{c.title}</button>)}</div>
            <div className="gallery">{results.filter(r => categoryFilter === 'all' || r.category === categoryFilter).map(r => <div className="image-card" key={r.id}><div className="image-box"><img src={r.url} alt={`${r.sku} - ${r.categoryTitle}`} /><span>{r.categoryTitle}</span></div><div className="image-details"><strong>{r.sku}</strong><small>Image {String(r.number).padStart(2, '0')}</small><div><button className={`approve ${r.approved ? 'approved' : ''}`} onClick={() => setResults(prev => prev.map(x => x.id === r.id ? { ...x, approved: !x.approved } : x))}><Check size={15} /> {r.approved ? 'Approved' : 'Approve'}</button><button disabled={working} title="Regenerate (uses credits)" onClick={() => regenerate(r)}><RefreshCw size={15} /></button><button title="Download this image" onClick={() => downloadOne(r)}><Download size={15} /></button></div></div></div>)}</div>
            {!results.length && <div className="notice">No images were created. Check the error message and backend.</div>}
            <div className="bottom-actions"><button className="secondary" onClick={() => setStep(2)}>Back to SKU settings</button><button className="primary" disabled={!approved.length} onClick={exportZip}><Download size={16} /> Export approved images</button></div></>}
          <ErrorText value={error} />
          {confirm && <div className="overlay"><div className="dialog"><button className="close" onClick={() => setConfirm(false)} aria-label="Close"><X size={19} /></button><Sparkles size={26} className="gold" /><h2>Start creating?</h2><p>{selected.length} SKU(s), {total} images. This makes 8 PAID Gemini image requests per SKU (including infographic and dimensions). No automatic paid retries. Single photo is accepted; unseen AI-generated views are estimates, not exact scans.</p><div className="dialog-actions"><button className="secondary" onClick={() => setConfirm(false)}>Cancel</button><button className="primary" onClick={generate}>Confirm & create</button></div></div></div>}
        </>}
      </div>
      <nav className="mobile-nav"><button className={page === 'create' ? 'active' : ''} onClick={() => setPage('create')}><ImagePlus size={19} /> Create</button><button className={page === 'usage' ? 'active' : ''} onClick={() => { setPage('usage'); refreshUsage(); }}><BarChart3 size={19} /> Usage</button></nav>
    </main>
  </div>;
}


export default function App() {
  return <AuthGate>{(logout) => <StudioApp onLogout={logout} />}</AuthGate>;
}
