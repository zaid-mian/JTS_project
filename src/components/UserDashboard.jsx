// File: src/components/UserDashboard.jsx
import React from 'react';

export default function UserDashboard({ onTriggerPasswordChange }) {
  // Configured local mock simulation representing the logged-in operator
  const mockUser = {
    name: "Ayesha Malik",
    role: "System Operator",
    email: "ayesha@vortex-tech.com",
    lastLogin: "Today, 12:45 PM",
    organization: "Vortex Creative Ltd",
    accountStatus: "Active"
  };

  return (
    <div className="space-y-6 py-6 text-slate-100">
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-6 rounded-2xl">
        <div>
          <h2 className="text-2xl font-bold text-white">Welcome, {mockUser.name}!</h2>
          <p className="text-xs text-slate-400">Logged in as {mockUser.role} at {mockUser.organization}</p>
        </div>
        <button 
          onClick={onTriggerPasswordChange}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold border border-slate-700 transition"
        >
          Change Password
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* User Identity Parameters */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Account Information</h3>
          <div className="space-y-1.5 text-sm">
            <p className="text-slate-400">Email: <span className="text-slate-200">{mockUser.email}</span></p>
            <p className="text-slate-400">Organization: <span className="text-slate-200">{mockUser.organization}</span></p>
          </div>
        </div>

        {/* Security Parameters */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Access Credentials</h3>
          <div className="space-y-1.5 text-sm">
            <p className="text-slate-400">Active Status: <span className="text-emerald-400 font-semibold">{mockUser.accountStatus}</span></p>
            <p className="text-slate-400">Last Activity: <span className="text-slate-200">{mockUser.lastLogin}</span></p>
          </div>
        </div>

        {/* Action Logs */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">System Messages</h3>
          <p className="text-xs text-slate-400 italic">No warnings registered. Your profile is running on the latest build.</p>
        </div>
      </div>
    </div>
  );
}