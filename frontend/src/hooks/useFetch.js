import { useState, useEffect, useCallback } from 'react';

export function useFetch(fetcher, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refetchCount, setRefetchCount] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;

    setLoading(true);
    setError(null);

    fetcher(controller.signal)
      .then((result) => {
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled && err.name !== 'AbortError') {
          setError(err.message || 'Error desconocido');
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, refetchCount]);

  const refetch = useCallback(() => setRefetchCount((c) => c + 1), []);

  return { data, loading, error, refetch };
}
