import React, { useState } from 'react';
import axios from 'axios';
import { 
  Container, Box, Typography, TextField, Button, Paper, 
  AppBar, Toolbar, FormControl, InputLabel, Select, MenuItem, 
  CircularProgress, Alert, Grid, FormHelperText
} from '@mui/material';
import { CloudUpload, Logout, AutoAwesome, Send, Save } from '@mui/icons-material';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userPowiat, setUserPowiat] = useState('');

  if (!isLoggedIn) {
    return <Login onLogin={(powiat) => { setIsLoggedIn(true); setUserPowiat(powiat); }} />;
  }

  return <RegisterForm powiat={userPowiat} onLogout={() => setIsLoggedIn(false)} />;
}

// --- 1. LOGIN ---
function Login({ onLogin }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await axios.post('/login', form);
      onLogin(res.data.powiat);
    } catch (err) {
      setError("Błędny email lub hasło.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xs" sx={{ mt: 10 }}>
      <Paper elevation={6} sx={{ p: 4, display: 'flex', flexDirection: 'column', gap: 3, borderRadius: 3 }}>
        <Box textAlign="center">
          <Typography variant="h4" fontWeight="bold" color="primary">🏛️ System Zgub</Typography>
          <Typography variant="body2" color="textSecondary">Logowanie Urzędnika</Typography>
        </Box>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField label="Email" fullWidth value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
        <TextField label="Hasło" type="password" fullWidth value={form.password} onChange={e => setForm({...form, password: e.target.value})} />
        <Button variant="contained" size="large" onClick={handleSubmit} disabled={loading} sx={{ py: 1.5 }}>
          {loading ? <CircularProgress size={24} color="inherit"/> : 'Zaloguj się'}
        </Button>
      </Paper>
    </Container>
  );
}

// --- 2. FORMULARZ ZGODNY ZE SCHEMĄ ---
function RegisterForm({ onLogout, powiat }) {
  
  // Stan inicjalny - tylko pola, których NIE uzupełnia backend automatycznie
  const initialFormState = {
    data_znalezienia: new Date().toISOString().split('T')[0], // Dziś
    data_przekazania: new Date().toISOString().split('T')[0], // Dziś (można zmienić)
    kategoria: 'inne',
    opis: '',
    adres_znalezienia: '',
    adres_znalezienia_opis: '',
    status: 'do_odbioru'
    // UWAGA: powiat, adres_odbioru, email, telefon -> Backend pobiera z sesji!
  };

  const [form, setForm] = useState(initialFormState);
  const [aiLoading, setAiLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

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

  const handleSubmit = async () => {
    setSubmitLoading(true);
    setErrorMsg('');
    setSuccessMsg('');
    
    try {
      await axios.post('/lost_item', form);
      setSuccessMsg('✅ Pomyślnie dodano do rejestru!');
      // Reset formularza (zachowujemy daty)
      setForm({ 
        ...initialFormState, 
        data_znalezienia: form.data_znalezienia,
        data_przekazania: form.data_przekazania
      });
      setTimeout(() => setSuccessMsg(''), 5000);
    } catch (err) {
      // Obsługa błędu walidacji JSON Schema z backendu
      const backendMsg = err.response?.data?.message || err.message;
      setErrorMsg(`Błąd zapisu: ${backendMsg}`);
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f4f6f8', minHeight: '100vh', pb: 4 }}>
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, color: '#333' }}>
            Rejestracja Zgub ({powiat})
          </Typography>
          <Button color="inherit" onClick={onLogout} startIcon={<Logout />}>Wyloguj</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Paper elevation={0} sx={{ p: 4, borderRadius: 3, border: '1px solid #e0e0e0' }}>
          
          {/* AI SECTION */}
          <Box mb={4} p={3} bgcolor="#e3f2fd" borderRadius={2} border="1px dashed #2196f3" display="flex" alignItems="center" gap={2}>
            <AutoAwesome color="primary" fontSize="large" />
            <Box flexGrow={1}>
              <Typography variant="subtitle1" fontWeight="bold">AI Auto-uzupełnianie</Typography>
              <Typography variant="body2" color="textSecondary">Wgraj zdjęcie - system rozpozna kategorię i opis.</Typography>
            </Box>
            <Button variant="contained" component="label" disabled={aiLoading} startIcon={<CloudUpload />}>
              {aiLoading ? 'Analiza...' : 'Wgraj zdjęcie'}
              <input type="file" hidden accept="image/*" onChange={handleAiUpload} />
            </Button>
          </Box>

          {successMsg && <Alert severity="success" sx={{ mb: 3 }}>{successMsg}</Alert>}
          {errorMsg && <Alert severity="error" sx={{ mb: 3 }}>{errorMsg}</Alert>}

          {/* FORMULARZ */}
          <Grid container spacing={3}>
            
            {/* DATY */}
            <Grid item xs={12} sm={6}>
              <TextField 
                label="Data znalezienia (wymagane)" type="date" fullWidth InputLabelProps={{ shrink: true }} required
                value={form.data_znalezienia}
                onChange={e => setForm({...form, data_znalezienia: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField 
                label="Data przekazania do biura" type="date" fullWidth InputLabelProps={{ shrink: true }}
                value={form.data_przekazania}
                onChange={e => setForm({...form, data_przekazania: e.target.value})}
                helperText="Jeśli inna niż data znalezienia"
              />
            </Grid>

            {/* KATEGORIA I STATUS */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Kategoria</InputLabel>
                <Select 
                  value={form.kategoria} label="Kategoria"
                  onChange={e => setForm({...form, kategoria: e.target.value})}
                >
                  {/* Zgodne ze Schema Enum */}
                  <MenuItem value="dokumenty_i_portfele">Dokumenty i portfele</MenuItem>
                  <MenuItem value="elektronika">Elektronika</MenuItem>
                  <MenuItem value="odziez_i_akcesoria">Odzież i akcesoria</MenuItem>
                  <MenuItem value="klucze">Klucze</MenuItem>
                  <MenuItem value="bizuteria_i_zegarki">Biżuteria i zegarki</MenuItem>
                  <MenuItem value="pieniadze">Pieniądze</MenuItem>
                  <MenuItem value="inne">Inne</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
               <FormControl fullWidth required>
                <InputLabel>Status</InputLabel>
                <Select 
                  value={form.status} label="Status"
                  onChange={e => setForm({...form, status: e.target.value})}
                >
                  <MenuItem value="do_odbioru">Do odbioru</MenuItem>
                  <MenuItem value="odebrano">Odebrano</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* OPIS */}
            <Grid item xs={12}>
              <TextField 
                label="Opis przedmiotu" multiline rows={4} fullWidth required
                placeholder="Szczegółowy opis, cechy, kolor, marka..."
                value={form.opis}
                onChange={e => setForm({...form, opis: e.target.value})}
              />
            </Grid>

            {/* LOKALIZACJA */}
            <Grid item xs={12} sm={6}>
              <TextField 
                label="Adres znalezienia" fullWidth 
                placeholder="Ulica, park, plac..."
                value={form.adres_znalezienia}
                onChange={e => setForm({...form, adres_znalezienia: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField 
                label="Szczegóły miejsca" fullWidth 
                placeholder="np. autobus 175, ławka przy stawie"
                value={form.adres_znalezienia_opis}
                onChange={e => setForm({...form, adres_znalezienia_opis: e.target.value})}
              />
            </Grid>

            {/* SUBMIT */}
            <Grid item xs={12}>
              <Box display="flex" justifyContent="flex-end" mt={2}>
                <Button 
                  variant="contained" size="large" 
                  color="primary" 
                  startIcon={<Save />}
                  onClick={handleSubmit}
                  disabled={submitLoading}
                  sx={{ px: 5, py: 1.5 }}
                >
                  {submitLoading ? 'Zapisywanie...' : 'Zapisz w rejestrze'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
}

export default App;
