import React, { useState } from 'react';

const initialForm = {
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
  companyName: '',
  companyLogo: null,
  phoneNumber: '',
  country: '',
  address: '',
  cnic: '',
};

const fieldLabels = {
  fullName: 'Full Name',
  email: 'Email',
  password: 'Password',
  confirmPassword: 'Confirm Password',
  companyName: 'Company Name',
  companyLogo: 'Company Logo',
  phoneNumber: 'Phone Number',
  country: 'Country',
  address: 'Address',
  cnic: 'CNIC',
};

export default function RegistrationPage() {
  const [form, setForm] = useState(initialForm);

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const getMissingField = () => Object.entries(form).find(([, value]) => {
    if (value instanceof File) {
      return false;
    }
    return String(value || '').trim().length === 0;
  });

  const handleSubmit = (event) => {
    event.preventDefault();
    const missingField = getMissingField();
    if (missingField) {
      alert(`Please fill ${fieldLabels[missingField[0]]}.`);
      return;
    }
    if (form.password !== form.confirmPassword) {
      alert('Password and Confirm Password must match.');
      return;
    }
    console.log('Registration form payload:', form);
    alert('Registration form submitted from frontend.');
  };

  return (
    <div className="mx-auto max-w-4xl py-6 text-slate-100">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold tracking-tight text-white">Registration</h2>
        <p className="text-xs text-slate-400">Create a company account request</p>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="grid gap-4 md:grid-cols-2">
          <FormField label="Full Name" value={form.fullName} onChange={(value) => updateField('fullName', value)} />
          <FormField label="Email" type="email" value={form.email} onChange={(value) => updateField('email', value)} />
          <FormField label="Password" type="password" value={form.password} onChange={(value) => updateField('password', value)} />
          <FormField label="Confirm Password" type="password" value={form.confirmPassword} onChange={(value) => updateField('confirmPassword', value)} />
          <FormField label="Company Name" value={form.companyName} onChange={(value) => updateField('companyName', value)} />
          <div>
            <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Company Logo
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={(event) => updateField('companyLogo', event.target.files?.[0] || null)}
              className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-300 outline-none transition file:mr-4 file:rounded-lg file:border-0 file:bg-teal-500 file:px-3 file:py-1.5 file:text-xs file:font-bold file:text-slate-950"
            />
          </div>
          <FormField label="Phone Number" type="tel" value={form.phoneNumber} onChange={(value) => updateField('phoneNumber', value)} />
          <FormField label="Country" value={form.country} onChange={(value) => updateField('country', value)} />
          <FormField label="CNIC" value={form.cnic} onChange={(value) => updateField('cnic', value)} />
          <div className="md:col-span-2">
            <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Address
            </label>
            <textarea
              rows="4"
              value={form.address}
              onChange={(event) => updateField('address', event.target.value)}
              className="w-full resize-none rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 outline-none transition focus:border-teal-500"
              placeholder="Enter company address"
            />
          </div>
        </div>

        <button
          type="submit"
          className="mt-6 w-full rounded-xl bg-teal-500 py-3 text-sm font-bold text-slate-950 transition hover:bg-teal-400"
        >
          Register
        </button>
      </form>
    </div>
  );
}

function FormField({ label, type = 'text', value, onChange }) {
  return (
    <div>
      <label className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-xl border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 outline-none transition focus:border-teal-500"
        placeholder={label}
      />
    </div>
  );
}
