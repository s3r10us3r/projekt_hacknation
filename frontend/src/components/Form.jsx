import React, { useState } from 'react';
import axios from 'axios';


const Icon = ({ name }) => <span className={`icon-${name}`}>{/* SVG lub inna ikona */}</span>;
const Logo = () => <img className='logo' src="public/logo.svg.webp" alt="Logo" />
const FIELD_LABELS = {
    opis: 'Opis przedmiotu',
    miejsce_znalezienia : 'Miejsce znalezienia',
};

const FilePreview = ({ files, onRemove }) => (
    <ul className="file-preview-list">
        {files.map((file, index) => (
            <li key={index} className="file-preview-item">
                <Icon name="image" />
                <span className="file-name">{file.name}</span>
                <button className="remove-btn" onClick={() => onRemove(index)} title="Usuń plik">
                  X
                </button>
            </li>
        ))}
    </ul>
);

const parseBackendError = (backendMsg) => {
    const fieldErrors = {};
    const globalError = [];
    
    const DEFAULT_ERROR_DESCRIPTION = "Wprowadzona wartość jest nieprawidłowa lub brakuje wymaganego pola.";
    if (Array.isArray(backendMsg)) {
        globalError.push("Wystąpiły błędy walidacji w formularzu. Sprawdź zaznaczone pola.");
        
        for (const fieldName of backendMsg) {
            const label = FIELD_LABELS[fieldName] || fieldName;
            fieldErrors[fieldName] = `"${label}": ${DEFAULT_ERROR_DESCRIPTION}`;
        }
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
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileSelect = (e) => {
    const newFiles = Array.from(e.target.files);
    if (newFiles.length > 0) {
        setSelectedFiles(prev => [...prev, ...newFiles]);
    }
    e.target.value = null; 
  };

  const handleFileRemove = (indexToRemove) => {
    setSelectedFiles(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleAiAnalysis = async () => {
    if (selectedFiles.length === 0) return;

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('photos', file);
    });

    setAiLoading(true);
    try {
        const res = await axios.post('/api/narzedzia/auto_uzupelnianie', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        setErrorMsg(''); 
        
        setForm(prev => ({
            ...prev,
            kategoria: res.data.kategoria || 'inne',
            opis: res.data.opis || prev.opis,
        }));
        
        setSelectedFiles([]); 

    } catch (err) {
        const backendMsg = err.response?.data?.error || err.message;
        setErrorMsg(`Błąd analizy AI: ${backendMsg}`);
    } finally {
        setAiLoading(false);
    }
  };

  const handleAiUpload = async (e) => {
    const files = e.target.files;
    if (files.length == 0) return;

    const formData = new FormData();
        
    for (let i = 0; i < files.length; i++) {
        formData.append('photos', files[i]); 
    }

    setAiLoading(true);
    try {
      const res = await axios.post('/api/narzedzia/auto_uzupelnianie', formData, {
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
      await axios.post('/api/rzeczy_znalezione', form);
      setSuccessMsg('✅ Pomyślnie dodano do rejestru!');
      setForm({ 
        ...initialFormState, 
        data_znalezienia: form.data_znalezienia,
        data_przekazania: form.data_przekazania,
        opis: '',
        kategoria: 'inne',
        miejsce_znalezienia: '',
        status: 'do_odbioru'
      });
      setTimeout(() => setSuccessMsg(''), 5000);
    } catch (err) {
      const backendMsg = err.response?.data?.fields || err.message;
      
      const { fieldErrors: parsedFieldErrors, globalError } = parseBackendError(backendMsg);
      
      console.log('dupa', parsedFieldErrors);
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
            {/* ... AppBar ... */}
            <div className="app-bar">
                <div className="toolbar">
                    {Logo()}
                    <h2 className="title">ZnAIdź ({powiat})</h2>
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
                            <p className="ai-subtitle">Wgraj zdjęcia - system rozpozna kategorię i opis.</p>
                        </div>
                        
                        <label className="upload-btn" htmlFor="file-upload" disabled={aiLoading}>
                            <Icon name="file-upload" /> Dodaj zdjęcie
                            <input 
                                type="file" 
                                id="file-upload" 
                                hidden 
                                accept="image/*" 
                                multiple 
                                onChange={handleFileSelect} 
                                disabled={aiLoading} 
                            />
                        </label>
                        
                        <button
                            className="analyze-btn" 
                            onClick={handleAiAnalysis}
                            disabled={selectedFiles.length === 0 || aiLoading}
                        >
                            {aiLoading ? 'Analiza...' : 'Analizuj zdjęcia'}
                            {aiLoading && <div className="loader"></div>}
                        </button>
                        
                    </div>
                    
                    {selectedFiles.length > 0 && (
                        <div className="file-preview-container">
                            <FilePreview files={selectedFiles} onRemove={handleFileRemove} />
                            <p className="helper-text-files">Wybrano: {selectedFiles.length} zdjęć. Kliknij "Analizuj", aby uzupełnić formularz.</p>
                        </div>
                    )}


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

                        <div className={`grid-item ${fieldErrors.miejsce_znalezienia ? 'has-error' : ''}`}>
                            <label htmlFor="miejsce_znalezienia">Miejsce znalezienia</label>
                            <input 
                                id="miejsce_znalezienia" type="text" className="form-input"
                                placeholder="Ulica, park, plac..."
                                name="miejsce_znalezienia"
                                value={form.miejsce_znalezienia}
                                onChange={handleChange}
                            />
                            {fieldErrors.miejsce_znalezienia && <p className="field-error">{fieldErrors.miejsce_znalezienia}</p>}
                        </div>
                        
                        <div className="grid-item"></div> {/* Puste pole dla wyrównania */}

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
