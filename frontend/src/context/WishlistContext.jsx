import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { getWishlist, addToWishlist, removeFromWishlist } from '../lib/api';

const WishlistContext = createContext(null);
export const useWishlist = () => {
  const ctx = useContext(WishlistContext);
  if (!ctx) throw new Error('useWishlist must be used inside WishlistProvider');
  return ctx;
};

export function WishlistProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [ids, setIds] = useState(new Set());
  const [items, setItems] = useState([]);

  const refresh = useCallback(async () => {
    try {
      const data = await getWishlist();
      setItems(data);
      setIds(new Set(data.map(i => i.game_id)));
    } catch {}
  }, []);

  useEffect(() => {
    if (isAuthenticated) { refresh(); }
    else { setIds(new Set()); setItems([]); }
  }, [isAuthenticated, refresh]);

  const isInWishlist = useCallback((gameId) => ids.has(Number(gameId)), [ids]);

  const toggle = useCallback(async (gameId) => {
    const id = Number(gameId);
    const wasIn = ids.has(id);
    const next = new Set(ids);
    wasIn ? next.delete(id) : next.add(id);
    setIds(next);
    try {
      if (wasIn) await removeFromWishlist(id);
      else await addToWishlist(id);
      await refresh();
    } catch (err) {
      setIds(ids);
      console.error(err);
    }
  }, [ids, refresh]);

  return (
    <WishlistContext.Provider value={{ isInWishlist, toggle, items, count: ids.size }}>
      {children}
    </WishlistContext.Provider>
  );
}
