export const formatPrice = (n) => {
  if (n == null) return '—';
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
};

export const formatDiscount = (p) => `-${Math.round(p)}%`;
