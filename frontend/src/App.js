import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Inventory from './components/Inventory';
import Billing from './components/Billing';
import Toast from './components/Toast';
import './App.css';

function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="app">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      <main className="main-content">
        {activeView === 'dashboard' && <Dashboard showToast={showToast} />}
        {activeView === 'inventory' && <Inventory showToast={showToast} />}
        {activeView === 'billing' && <Billing showToast={showToast} />}
      </main>
      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  );
}

export default App;
