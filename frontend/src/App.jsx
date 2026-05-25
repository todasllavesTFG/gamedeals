import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { WishlistProvider } from './context/WishlistContext';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Deals from './pages/Deals';
import FreeGames from './pages/FreeGames';
import Search from './pages/Search';
import GameDetail from './pages/GameDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Wishlist from './pages/Wishlist';
import Alerts from './pages/Alerts';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WishlistProvider>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<Home />} />
              <Route path="/deals" element={<Deals />} />
              <Route path="/free" element={<FreeGames />} />
              <Route path="/search" element={<Search />} />
              <Route path="/games/:id" element={<GameDetail />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route element={<ProtectedRoute />}>
                <Route path="/wishlist" element={<Wishlist />} />
                <Route path="/alerts" element={<Alerts />} />
              </Route>
            </Route>
          </Routes>
        </WishlistProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
