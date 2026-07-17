// File: src/components/AdminDashboard.jsx
import React, { useState } from 'react';

export default function AdminDashboard() {
  // Page 8 Required Display Parameters (Company Logo, Company Name, Owner Name, Email, Status, Approve & Reject Actions)
  const [applications, setApplications] = useState([
    {
      id: 1,
      companyLogo: "🌟",
      companyName: "Skyline Ventures",
      ownerName: "Zainab Ahmed",
      email: "zainab@skyline.com",
      status: "Pending"
    },
    {
      id: 2,
      companyLogo: "💠",
      companyName: "Apex Software Lab",
      ownerName: "Bilal Malik",
      email: "bilal@apexlab.io",
      status: "Pending"
    }
  ]);

  const handleApprove = (id) => {
    setApplications(applications.map(app => 
      app.id === id ? { ...app, status: 'Approved' } : app
    ));
  };

  const handleReject = (id) => {
    setApplications(applications.map(app => 
      app.id === id ? { ...app, status: 'Rejected' } : app
    ));
  };

  return (
    <div className="space-y-6 py-6 text-slate-100">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold tracking-tight text-white">Admin Control Dashboard</h2>
        <p className="text-xs text-slate-400">Evaluate and approve registered workspace requests</p>
      </div>

      <div className="space-y-4">
        {applications.map((app) => (
          <div 
            key={app.id} 
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-wrap justify-between items-center gap-6"
          >
            {/* Left Section: Company Logo, Name, Owner Name, and Email */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-slate-950 rounded-xl flex items-center justify-center text-xl border border-slate-800">
                {app.companyLogo}
              </div>
              <div className="space-y-1">
                <h4 className="text-base font-bold text-white">{app.companyName}</h4>
                <div className="text-xs space-y-0.5">
                  <p className="text-slate-300">Owner Name: <span className="font-semibold text-teal-400">{app.ownerName}</span></p>
                  <p className="text-slate-400">Email: {app.email}</p>
                </div>
              </div>
            </div>

            {/* Right Section: Status Badge, Approve Button, Reject Button */}
            <div className="flex items-center gap-4">
              <span className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wider ${
                app.status === 'Approved' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 
                app.status === 'Rejected' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 
                'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
              }`}>
                {app.status}
              </span>

              {app.status === 'Pending' && (
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleApprove(app.id)}
                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 rounded-lg text-xs font-bold transition"
                  >
                    Approve
                  </button>
                  <button 
                    onClick={() => handleReject(app.id)}
                    className="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-slate-950 rounded-lg text-xs font-bold transition"
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}