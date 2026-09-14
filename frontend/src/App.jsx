import { useEffect, useMemo, useState } from "react";
export default function App() {
  const [token, setToken] = useState(localStorage.getItem("edmms_token") || "");
  const [me, setMe] = useState(JSON.parse(localStorage.getItem("edmms_me") || "null"));
  const [form, setForm] = useState({ username: "ceo", password: "ChangeMe!2026" });
  const [meetings, setMeetings] = useState([]);
  const [voice, setVoice] = useState("Book a secret meeting tomorrow");
  const [out, setOut] = useState(null);
  const headers = useMemo(() => ({ "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) }), [token]);
  useEffect(() => { if (!token) return; fetch("/api/meetings", { headers }).then(r => r.json()).then(d => Array.isArray(d) && setMeetings(d)); }, [token]);
  async function login(e) {
    e.preventDefault();
    const res = await fetch("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) }).then(r => r.json());
    if (res.access_token) { setToken(res.access_token); setMe(res.user); localStorage.setItem("edmms_token", res.access_token); localStorage.setItem("edmms_me", JSON.stringify(res.user)); }
    else alert(res.detail || "login failed");
  }
  if (!token) return (<div className="wrap"><div className="card"><h1>EDMMS</h1><form onSubmit={login}><input value={form.username} onChange={e=>setForm({...form,username:e.target.value})}/><input type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/><button className="gold">Sign in</button></form></div></div>);
  return (<div><div className="banner">SECURE ENVIRONMENT · {me?.clearance}</div><div className="wrap"><div className="card"><h3>Meetings</h3><ul>{meetings.map(m => <li key={m.id}>{m.title} ({m.classification})</li>)}</ul></div><div className="card"><h3>Voice booking</h3><textarea value={voice} onChange={e=>setVoice(e.target.value)}/><button className="gold" onClick={async()=>{const r=await fetch("/api/voice/book",{method:"POST",headers,body:JSON.stringify({language:"en",transcript:voice})}).then(x=>x.json());setOut(r);}}>Submit</button>{out && <pre>{JSON.stringify(out,null,2)}</pre>}</div></div></div>);
}