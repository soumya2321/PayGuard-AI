/**
 * useHealth.ts - Hook to monitor backend and database operational status.
 */

import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { SystemHealthResponse } from '../types';

export function useHealth() {
  const [health, setHealth] = useState<SystemHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    apiService
      .getHealth()
      .then((data) => {
        if (mounted) {
          setHealth(data);
          setLoading(false);
        }
      })
      .catch((err: Error) => {
        if (mounted) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  return { health, loading, error };
}
