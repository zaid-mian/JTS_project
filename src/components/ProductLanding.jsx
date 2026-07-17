import React, { useEffect, useState } from 'react';
import heroImage from '../assets/hero.png';

const fallbackProducts = [
  {
    id: 1,
    slug: 'crm-growth-suite',
    name: 'CRM Growth Suite',
    description: 'A complete customer management portal for sales teams, support staff, and company administrators.',
    image: heroImage,
  },
  {
    id: 2,
    slug: 'support-desk-pro',
    name: 'Support Desk Pro',
    description: 'Track tickets, manage customer issues, and keep service teams aligned from one clean dashboard.',
    image: heroImage,
  },
  {
    id: 3,
    slug: 'sales-automation-hub',
    name: 'Sales Automation Hub',
    description: 'Manage follow-ups, automate lead stages, and keep revenue teams focused on the next best action.',
    image: heroImage,
  },
];

export default function ProductLanding({ onViewDetails }) {
  const [products, setProducts] = useState(fallbackProducts);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    fetch('/api/products/')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Products request failed');
        }
        return response.json();
      })
      .then((data) => {
        if (!isMounted) return;
        const productList = Array.isArray(data) ? data : data.results || fallbackProducts;
        setProducts(productList);
      })
      .catch(() => {
        if (isMounted) {
          setProducts(fallbackProducts);
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
  }, []);

  return (
    <div className="space-y-6 py-6 text-slate-100">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold tracking-tight text-white">Products</h2>
        <p className="text-xs text-slate-400">Loaded from GET /api/products/</p>
      </div>

      {isLoading && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 text-sm text-slate-400">
          Loading products...
        </div>
      )}

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {products.map((product) => (
          <article
            key={product.id || product.slug || product.name}
            className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900"
          >
            <img
              src={product.image || product.product_image || heroImage}
              alt={product.name || product.product_name}
              className="h-52 w-full object-cover"
            />
            <div className="space-y-4 p-5">
              <div>
                <h3 className="text-lg font-bold text-white">{product.name || product.product_name}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-400">{product.description}</p>
              </div>
              <button
                type="button"
                onClick={() => onViewDetails(product.slug || fallbackProducts[0].slug)}
                className="rounded-lg bg-teal-500 px-4 py-2 text-sm font-bold text-slate-950 transition hover:bg-teal-400"
              >
                View Details
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
