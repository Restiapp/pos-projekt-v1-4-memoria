/**
 * useDebounce - Custom hook for debouncing values
 *
 * Delays updating the returned value until the input value has stopped changing
 * for the specified delay period. This is useful for reducing API calls when
 * users are typing in search inputs.
 *
 * @param value - The value to debounce
 * @param delay - The delay in milliseconds (default: 300ms)
 * @returns The debounced value
 *
 * @example
 * ```tsx
 * const [searchQuery, setSearchQuery] = useState('');
 * const debouncedSearchQuery = useDebounce(searchQuery, 300);
 *
 * useEffect(() => {
 *   // This will only run 300ms after the user stops typing
 *   fetchResults(debouncedSearchQuery);
 * }, [debouncedSearchQuery]);
 * ```
 */

import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Set up the timeout to update the debounced value
    const timeoutId = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Cleanup function: cancel the timeout if value changes before delay expires
    return () => {
      clearTimeout(timeoutId);
    };
  }, [value, delay]);

  return debouncedValue;
}
