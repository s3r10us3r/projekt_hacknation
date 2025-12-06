import React, { useState } from 'react';
import axios from 'axios';


const Icon = ({ name }) => <span className={`icon-${name}`}>{/* SVG lub inna ikona */}</span>;
const Logo = () => <img className='logo' src="public/2560px-Logo_Ministerstwa_Cyfryzacji.svg.png" alt="Logo" />
const FIELD_LABELS = {
    opis: 'Opis przedmiotu',
    adres_znalezienia: 'Adres znalezienia',
    adres_znalezienia_opis: 'Szczegóły miejsca',
    telefon_kontaktowy: 'Telefon kontaktowy',
};

const parseBackendError = (backendMsg) => {
    const fieldErrors = {};
    const globalError = [];
    const regex = /Błąd walidacji schemy: (.*?) w polu deque\(\['(.*?)'\]\)/;
    const match = backendMsg.match(regex);

    if (match) {
        const errorDescription = match[1];
        const fieldName = match[2];
        const label = FIELD_LABELS[fieldName] || fieldName;
        fieldErrors[fieldName] = `Błąd pola "${label}": ${errorDescription.includes('not of type') ? 'Wprowadź prawidłowy tekst/liczbę' : errorDescription}`;
        globalError.push("❌ Wystąpiły błędy walidacji w formularzu. Sprawdź zaznaczone pola.");
    } else {
        globalError.push(`Błąd zapisu: ${backendMsg}`);
    }
    return { fieldErrors, globalError: globalError.join(' ') };
};


export function RegisterForm({ onLogout, powiat }) {
  
  const initialFormState = {
    data_znalezienia: new Date().toISOString().split('T')[0],
    data_przekazania: new Date().toISOString().split('T')[0],
    kategoria: 'inne',
    opis: '',
    adres_znalezienia: '',
    adres_znalezienia_opis: '',
    status: 'do_odbioru'
  };

  const [form, setForm] = useState(initialFormState);
  const [aiLoading, setAiLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const handleAiUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('photos', file);

    setAiLoading(true);
    try {
      const res = await axios.post('/form_autocomplete', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setForm(prev => ({
        ...prev,
        kategoria: res.data.kategoria || 'inne',
        opis: res.data.opis || prev.opis
      }));
    } catch (err) {
      alert("Błąd AI");
    } finally {
      setAiLoading(false);
    }
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFieldErrors(prev => ({ ...prev, [name]: undefined }));
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    setSubmitLoading(true);
    setErrorMsg('');
    setSuccessMsg('');
    setFieldErrors({});
    
    try {
      await axios.post('/lost_item', form);
      setSuccessMsg('✅ Pomyślnie dodano do rejestru!');
      setForm({ 
        ...initialFormState, 
        data_znalezienia: form.data_znalezienia,
        data_przekazania: form.data_przekazania,
        opis: '',
        kategoria: 'inne',
        adres_znalezienia: '',
        adres_znalezienia_opis: '',
        status: 'do_odbioru'
      });
      setTimeout(() => setSuccessMsg(''), 5000);
    } catch (err) {
      const backendMsg = err.response?.data?.message || err.message;
      
      const { fieldErrors: parsedFieldErrors, globalError } = parseBackendError(backendMsg);
      
      setFieldErrors(parsedFieldErrors);
      if (Object.keys(parsedFieldErrors).length > 0) {
          setErrorMsg(globalError);
      } else {
          setErrorMsg(`Błąd zapisu: ${backendMsg}`);
      }
      
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="app-bar">
        <div className="toolbar">
          {Logo()}
          <h2 className="title">Rejestracja Zgub ({powiat})</h2>
          <button className="logout-btn" onClick={onLogout}>
            <Icon name="logout" /> Wyloguj
          </button>
        </div>
      </div>

      <div className="container-large">
        <div className="paper register-paper">
          
          <div className="ai-box">
            <Icon name="auto-awesome" />
            <div className="ai-text-content">
              <p className="ai-title">AI Auto-uzupełnianie</p>
              <p className="ai-subtitle">Wgraj zdjęcie - system rozpozna kategorię i opis.</p>
            </div>
            <label className="upload-btn" htmlFor="file-upload" disabled={aiLoading}>
              {aiLoading ? 'Analiza...' : 'Wgraj zdjęcie'}
              <input type="file" id="file-upload" hidden accept="image/*" onChange={handleAiUpload} disabled={aiLoading} />
              {aiLoading && <div className="loader"></div>}
            </label>
          </div>

          {successMsg && <div className="alert-success">{successMsg}</div>}
          {errorMsg && <div className="alert-error">{errorMsg}</div>}

          <div className="form-grid">
            
            <div className={`grid-item ${fieldErrors.data_znalezienia ? 'has-error' : ''}`}>
              <label htmlFor="data_znalezienia">Data znalezienia (wymagane)</label>
              <input 
                id="data_znalezienia" type="date" className="form-input" required
                name="data_znalezienia"
                value={form.data_znalezienia}
                onChange={handleChange}
              />
               {fieldErrors.data_znalezienia && <p className="field-error">{fieldErrors.data_znalezienia}</p>}
            </div>
            <div className={`grid-item ${fieldErrors.data_przekazania ? 'has-error' : ''}`}>
              <label htmlFor="data_przekazania">Data przekazania do biura</label>
              <input 
                id="data_przekazania" type="date" className="form-input"
                name="data_przekazania"
                value={form.data_przekazania}
                onChange={handleChange}
              />
              <p className="helper-text">Jeśli inna niż data znalezienia</p>
              {fieldErrors.data_przekazania && <p className="field-error">{fieldErrors.data_przekazania}</p>}
            </div>

            <div className={`grid-item ${fieldErrors.kategoria ? 'has-error' : ''}`}>
              <label htmlFor="kategoria">Kategoria (wymagane)</label>
              <select 
                id="kategoria" className="form-input" required
                name="kategoria"
                value={form.kategoria} 
                onChange={handleChange}
              >
                <option value="dokumenty_i_portfele">Dokumenty i portfele</option>
                <option value="elektronika">Elektronika</option>
                <option value="odziez_i_akcesoria">Odzież i akcesoria</option>
                <option value="klucze">Klucze</option>
                <option value="bizuteria_i_zegarki">Biżuteria i zegarki</option>
                <option value="pieniadze">Pieniądze</option>
                <option value="inne">Inne</option>
              </select>
              {fieldErrors.kategoria && <p className="field-error">{fieldErrors.kategoria}</p>}
            </div>
            <div className={`grid-item ${fieldErrors.status ? 'has-error' : ''}`}>
              <label htmlFor="status">Status (wymagane)</label>
              <select 
                id="status" className="form-input" required
                name="status"
                value={form.status} 
                onChange={handleChange}
              >
                <option value="do_odbioru">Do odbioru</option>
                <option value="odebrano">Odebrano</option>
              </select>
              {fieldErrors.status && <p className="field-error">{fieldErrors.status}</p>}
            </div>

            <div className={`grid-item ${fieldErrors.adres_znalezienia ? 'has-error' : ''}`}>
              <label htmlFor="adres_znalezienia">Adres znalezienia</label>
              <input 
                id="adres_znalezienia" type="text" className="form-input"
                placeholder="Ulica, park, plac..."
                name="adres_znalezienia"
                value={form.adres_znalezienia}
                onChange={handleChange}
              />
              {fieldErrors.adres_znalezienia && <p className="field-error">{fieldErrors.adres_znalezienia}</p>}
            </div>
            <div className={`grid-item ${fieldErrors.adres_znalezienia_opis ? 'has-error' : ''}`}>
              <label htmlFor="adres_znalezienia_opis">Szczegóły miejsca</label>
              <input 
                id="adres_znalezienia_opis" type="text" className="form-input"
                placeholder="np. autobus 175, ławka przy stawie"
                name="adres_znalezienia_opis"
                value={form.adres_znalezienia_opis}
                onChange={handleChange}
              />
              {fieldErrors.adres_znalezienia_opis && <p className="field-error">{fieldErrors.adres_znalezienia_opis}</p>}
            </div>
            
            <div className="grid-item"></div>

            <div className={`grid-full ${fieldErrors.opis ? 'has-error' : ''}`}>
              <label htmlFor="opis">Opis przedmiotu (wymagane)</label>
              <textarea 
                id="opis" className="form-textarea" required
                placeholder="Szczegółowy opis, cechy, kolor, marka..."
                name="opis"
                rows="4"
                value={form.opis}
                onChange={handleChange}
              ></textarea>
              {fieldErrors.opis && <p className="field-error">{fieldErrors.opis}</p>}
            </div>
            
            <div className="grid-full button-row">
              <button 
                type="button" className="submit-btn save-btn"
                onClick={handleSubmit}
                disabled={submitLoading}
              >
                <Icon name="save" />
                {submitLoading ? 'Zapisywanie...' : 'Zapisz w rejestrze'}
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}