import React, { useEffect, useState } from 'react';
import heroImage from '../assets/hero.png';

const fallbackProduct = {
  slug: 'crm-growth-suite',
  name: 'CRM Growth Suite',
  description: 'A complete customer management portal for sales, support, and account administration.',
  image: heroImage,
  modules: ['Lead Management', 'Customer Accounts', 'Support Tickets', 'Analytics'],
  pricing_plans: [
    {
      name: 'Starter',
      price: 29,
      currency: 'USD',
      billing_cycle: 'Monthly',
      features: ['Contact tracking', 'Basic reports', 'Email support'],
      limits: ['5 users', '2,000 contacts', '10 GB storage'],
    },
    {
      name: 'Business',
      price: 79,
      currency: 'USD',
      billing_cycle: 'Monthly',
      features: ['Automation', 'Advanced analytics', 'Priority support'],
      limits: ['25 users', '20,000 contacts', '100 GB storage'],
    },
  ],
};

export default function ProductDetails({ slug = 'crm-growth-suite', onBack, onBuySubscription }) {
  const [product, setProduct] = useState(fallbackProduct);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    fetch(`/api/products/${slug}/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Product details request failed');
        }
        return response.json();
      })
      .then((data) => {
        if (isMounted) {
          setProduct(data);
        }
      })
      .catch(() => {
        if (isMounted) {
          setProduct(fallbackProduct);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [slug]);

  const modules = product.modules || [];
  const plans = product.pricing_plans || product.pricingPlans || [];

  return (
    <div className="space-y-6 py-6 text-slate-100">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Product Details</h2>
          <p className="text-xs text-slate-400">Loaded from GET /api/products/{slug}/</p>
        </div>
        <button
          type="button"
          onClick={onBack}
          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-xs font-bold text-slate-300 transition hover:bg-slate-800"
        >
          Back to Products
        </button>
      </div>

      {isLoading && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 text-sm text-slate-400">
          Loading product details...
        </div>
      )}

      <section className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
        <img
          src={product.image || product.product_image || heroImage}
          alt={product.name || product.product_name}
          className="h-full min-h-80 w-full rounded-xl border border-slate-800 object-cover"
        />
        <div className="space-y-5 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div>
            <h3 className="text-3xl font-bold text-white">{product.name || product.product_name}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-400">{product.description}</p>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500">Modules</h4>
            <div className="mt-3 flex flex-wrap gap-2">
              {modules.map((module) => (
                <span key={module} className="rounded-lg border border-teal-500/20 bg-teal-500/10 px-3 py-1 text-xs font-semibold text-teal-300">
                  {module}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2">
        {plans.map((plan) => (
          <div key={plan.name} className="flex flex-col rounded-xl border border-slate-800 bg-slate-900 p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-lg font-bold text-white">{plan.name}</h4>
                <p className="text-xs text-slate-400">{plan.billing_cycle || plan.billingCycle} billing</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-teal-400">{plan.price}</p>
                <p className="text-xs font-semibold text-slate-500">{plan.currency}</p>
              </div>
            </div>

            <div className="mt-5 grid flex-1 gap-4 sm:grid-cols-2">
              <div>
                <h5 className="text-xs font-bold uppercase tracking-widest text-slate-500">Features</h5>
                <ul className="mt-2 space-y-2 text-sm text-slate-300">
                  {(plan.features || []).map((feature) => (
                    <li key={feature}>- {feature}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h5 className="text-xs font-bold uppercase tracking-widest text-slate-500">Limits</h5>
                <ul className="mt-2 space-y-2 text-sm text-slate-300">
                  {(plan.limits || []).map((limit) => (
                    <li key={limit}>- {limit}</li>
                  ))}
                </ul>
              </div>
            </div>
            <button
              type="button"
              onClick={onBuySubscription}
              className="mt-6 w-full rounded-xl bg-teal-500 py-3 text-sm font-bold text-slate-950 transition hover:bg-teal-400"
            >
              Buy Subscription
            </button>
          </div>
        ))}
      </section>
    </div>
  );
}
