import { useState } from 'react';
import { Login } from './components/Login.jsx';
import { RegisterForm } from './components/Form.jsx';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userPowiat, setUserPowiat] = useState('');

  if (!isLoggedIn) {
    return <Login onLogin={(powiat) => { setIsLoggedIn(true); setUserPowiat(powiat); }} />;
  }

  return <RegisterForm powiat={userPowiat} onLogout={() => setIsLoggedIn(false)} />;
}

export default App;
