/**
 * Format cents to dollars with proper currency formatting
 * @param cents - Amount in cents (integer)
 * @returns Formatted currency string (e.g., "$12.34")
 */
export const formatCurrency = (cents: number): string => {
  if (typeof cents !== 'number' || isNaN(cents)) {
    return '$0.00';
  }
  
  const dollars = cents / 100;
  return `$${dollars.toFixed(2)}`;
};

/**
 * Parse dollar amount string to cents
 * @param amount - Dollar amount string (e.g., "12.34")
 * @returns Amount in cents (integer)
 */
export const parseCurrencyToCents = (amount: string): number => {
  if (!amount || typeof amount !== 'string') {
    return 0;
  }
  
  const cleanAmount = amount.replace(/[$,]/g, '');
  const parsed = parseFloat(cleanAmount);
  
  if (isNaN(parsed)) {
    return 0;
  }
  
  return Math.round(parsed * 100);
};
