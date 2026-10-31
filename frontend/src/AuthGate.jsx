import { useEffect, useState } from 'react';
import { Eye, EyeOff, LockKeyhole, ArrowRight, ShieldCheck } from 'lucide-react';
import './auth.css';

const API = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export default function AuthGate({ children }) {
  const [status, setStatus] = useState('checking');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [visible, setVisible] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [account, setAccount] = useState('');

  useEffect(() => {
    let active = true;
    fetch(`${API}/api/auth/me`, { credentials: 'include', cache: 'no-store' })
      .then(async (r) => {
        if (!active) return;
        if (r.ok) {
          const data = await r.json();
          if (active) { setAccount(data.username || ''); setStatus('ready'); }
        } else setStatus('login');
      })
      .catch(() => { if (active) { setStatus('login'); setError('Unable to connect to the backend.'); } });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    const expired = () => {
      setAccount(''); setPassword(''); setStatus('login');
      setError('Session expired. Please sign in again.');
    };
    window.addEventListener('maison-auth-expired', expired);
    return () => window.removeEventListener('maison-auth-expired', expired);
  }, []);

  async function signIn(e) {
    e.preventDefault();
    setError(''); setBusy(true);
    try {
      const r = await fetch(`${API}/api/auth/login`, {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(data.detail || 'Login failed');
      setAccount(data.username || username); setPassword(''); setStatus('ready');
    } catch (err) { setError(err.message || 'Could not sign in'); }
    finally { setBusy(false); }
  }

  async function signOut() {
    try {
      await fetch(`${API}/api/auth/logout`, { method: 'POST', credentials: 'include' });
    } catch (err) {
      console.warn('Logout request failed:', err);
    } finally {
      setAccount(''); setPassword(''); setError(''); setStatus('login');
    }
  }

  if (status === 'ready') return children(signOut, account);

  return (
    <div className="ma-auth-page">
      <main className="ma-auth-layout">
        <section className="ma-auth-left" aria-label="Studio sign in">
          <div className="ma-auth-form-wrap">
            <div className="ma-auth-brand">
              <img src="/de-maison-logo.png" alt="De Maison Decor logo" />
              <div><strong>DE MAISON DECOR</strong><span>IMAGE CREATION STUDIO</span></div>
            </div>
            {status === 'checking' ? (
              <div className="ma-auth-loading"><LockKeyhole size={18} /> Checking secure session…</div>
            ) : (
              <div className="ma-auth-login">
                <div className="ma-auth-eyebrow">WELCOME BACK</div>
                <h1>Sign in to your studio</h1>
                <p className="ma-auth-subtitle">Access your private product image creation workspace.</p>
                <form onSubmit={signIn}>
                  <label htmlFor="ma-user">Username</label>
                  <input id="ma-user" autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} placeholder="Enter your username" required />
                  <label htmlFor="ma-password">Password</label>
                  <div className="ma-auth-pass">
                    <input id="ma-password" type={visible ? 'text' : 'password'} autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password" required />
                    <button type="button" onClick={() => setVisible(v => !v)} aria-label={visible ? 'Hide password' : 'Show password'}>{visible ? <EyeOff size={18} /> : <Eye size={18} />}</button>
                  </div>
                  {error && <div className="ma-auth-error" role="alert">{error}</div>}
                  <button className="ma-auth-submit" type="submit" disabled={busy}>
                    {busy ? 'Signing in…' : 'Enter Studio'} <ArrowRight size={17} />
                  </button>
                </form>
                <div className="ma-auth-foot"><ShieldCheck size={15} /> Secure client access</div>
              </div>
            )}
          </div>
        </section>
        <aside className="ma-auth-right" aria-label="About De Maison Decor Studio">
          <div className="ma-auth-feature">
            <div className="ma-auth-eyebrow">DE MAISON DECOR / STUDIO</div>
            <h2>Product photography, <em>made for your catalogue.</em></h2>
            <p className="ma-auth-feature-desc">Turn your product photos into polished, marketplace-ready images. Create consistent visuals for every SKU, from a single product to an entire collection.</p>
            <div className="ma-auth-features">
              <div><span className="ma-auth-tick">✓</span><span><strong>Complete image sets</strong><small>White background, dimensions, close-ups, lifestyle and infographics</small></span></div>
              <div><span className="ma-auth-tick">✓</span><span><strong>Single product or batch upload</strong><small>Process individual images or organize multiple products by SKU</small></span></div>
              <div><span className="ma-auth-tick">✓</span><span><strong>Organized downloads</strong><small>Keep generated images together and export them in a ZIP</small></span></div>
            </div>
            <div className="ma-auth-preview" aria-hidden="true">
              <div className="ma-auth-preview-head"><span>IMAGE CREATION WORKFLOW</span><span className="ma-auth-preview-ready"><i /> Studio ready</span></div>
              <div className="ma-auth-preview-steps">
                <div><span className="ma-auth-step-num">01</span><strong>Upload</strong><small>Product photos</small></div>
                <ArrowRight size={17} />
                <div><span className="ma-auth-step-num">02</span><strong>Create</strong><small>Studio images</small></div>
                <ArrowRight size={17} />
                <div><span className="ma-auth-step-num">03</span><strong>Download</strong><small>Organized ZIP</small></div>
              </div>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
