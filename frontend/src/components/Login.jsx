import { useState } from 'react';
import axios from 'axios';

const Logo = () => <img className='logo' src="public/2560px-Logo_Ministerstwa_Cyfryzacji.svg.png" alt="Logo" />

export function Login({ onLogin }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await axios.post('/api/konta/logowanie', form);
      onLogin(res.data.powiat);
    } catch (err) {
      setError("Błędny email lub hasło.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="app-bar">
        <div className="toolbar">
          {Logo()}
        </div>
      </div>
    <div className='login-container'>
      <div className='container'>
        <div className='paper'>
          <div className='header'>
            <h1>System Zgub</h1>
            <p>Logowanie Urzędnika</p>
          </div>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <input
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              className="input-field"
              required
            />
            <input
              type="password"
              placeholder="Hasło"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="input-field"
              required
            />
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Ładowanie...' : 'Zaloguj się'}
            </button>
          </form>
        </div>
      </div>
    </div>
   </>
  );
}
