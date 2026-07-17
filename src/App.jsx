// File: src/App.jsx
import React, { useState } from 'react';
import ForgotPassword from './components/ForgotPassword';
import ChangePassword from './components/ChangePassword';
import UserDashboard from './components/UserDashboard';
import AdminDashboard from './components/AdminDashboard';
import ProductLanding from './components/ProductLanding';
import ProductDetails from './components/ProductDetails';
import RegistrationPage from './components/RegistrationPage';
import LoginPage from './components/LoginPage';

export default function App() {
  const [screen, setScreen] = useState('landing'); // Screen states: landing, product-details, register, login, forgot, change-password, user-dashboard, admin-dashboard
  const [selectedProductSlug, setSelectedProductSlug] = useState('crm-growth-suite');

  const openProductDetails = (slug) => {
    setSelectedProductSlug(slug);
    setScreen('product-details');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Dynamic Selector Header */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold tracking-wider text-teal-400">
          SYSTEM<span className="text-white">PORTAL</span>
        </h1>
        <div className="flex flex-wrap gap-2 bg-slate-950 p-1 border border-slate-800 rounded-lg">
          <button
            onClick={() => setScreen('landing')}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition ${screen === 'landing' ? 'bg-slate-800 text-teal-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Page 1 (Landing)
          </button>
          <button
            onClick={() => setScreen('product-details')}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition ${screen === 'product-details' ? 'bg-slate-800 text-teal-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Page 2 (Details)
          </button>
          <button
            onClick={() => setScreen('register')}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition ${screen === 'register' ? 'bg-slate-800 text-teal-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Page 3 (Register)
          </button>
          <button
            onClick={() => setScreen('login')}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition ${screen === 'login' ? 'bg-slate-800 text-teal-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Page 4 (Login)
          </button>
          <button 
            onClick={() => setScreen('forgot')} 
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition ${screen === 'forgot' ? 'bg-slate-800 text-teal-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Page 5 (Forgot)
          </button>
          <button 
            onClick={() => setScreen('change-password')} 
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition ${screen === 'change-password' ? 'bg-slate-800 text-teal-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Page 6 (Change)
          </button>
          <button 
            onClick={() => setScreen('user-dashboard')} 
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition ${screen === 'user-dashboard' ? 'bg-slate-800 text-teal-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Page 7 (User DB)
          </button>
          <button 
            onClick={() => setScreen('admin-dashboard')} 
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition ${screen === 'admin-dashboard' ? 'bg-slate-800 text-teal-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Page 8 (Admin DB)
          </button>
        </div>
      </nav>

      {/* Main Content Area where different pages render dynamically */}
      <main className="max-w-5xl mx-auto p-6">
        {screen === 'landing' && (
          <ProductLanding onViewDetails={openProductDetails} />
        )}
        {screen === 'product-details' && (
          <ProductDetails
            slug={selectedProductSlug}
            onBack={() => setScreen('landing')}
            onBuySubscription={() => setScreen('register')}
          />
        )}
        {screen === 'register' && (
          <RegistrationPage />
        )}
        {screen === 'login' && (
          <LoginPage onForgotPassword={() => setScreen('forgot')} />
        )}
        {screen === 'forgot' && (
          <ForgotPassword onBackToLogin={() => setScreen('login')} />
        )}
        {screen === 'change-password' && (
          <ChangePassword onComplete={() => setScreen('user-dashboard')} />
        )}
        {screen === 'user-dashboard' && (
          <UserDashboard onTriggerPasswordChange={() => setScreen('change-password')} />
        )}
        {screen === 'admin-dashboard' && (
          <AdminDashboard />
        )}
      </main>
    </div>
  );
}
