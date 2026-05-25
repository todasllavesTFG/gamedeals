import { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Gamepad2, LogOut, Heart, Bell, Menu, X } from 'lucide-react';
import SearchBar from './SearchBar';
import { useAuth } from '../../context/AuthContext';
import { useWishlist } from '../../context/WishlistContext';

const NAV_LINKS = [
  { to: '/', label: 'Home' },
  { to: '/deals', label: 'Deals' },
  { to: '/free', label: 'Free' },
];

export default function Navbar() {
  const { user, loading, isAuthenticated, logout } = useAuth();
  const { count } = useWishlist();
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  return (
    <header className='sticky top-0 z-50 bg-bg/80 backdrop-blur border-b border-border'>
      <div className='container mx-auto px-4 h-16 flex items-center gap-3 sm:gap-4'>
        <NavLink to='/' className='flex items-center gap-2 flex-shrink-0' onClick={closeMenu}>
          <Gamepad2 className='w-6 h-6 text-accent' />
          <span className='font-display text-accent font-semibold text-lg tracking-wide hidden sm:inline'>
            GameDeals
          </span>
        </NavLink>

        <div className='flex-1 flex justify-center min-w-0'>
          <SearchBar />
        </div>

        <nav className='hidden md:flex items-center gap-1 flex-shrink-0'>
          {NAV_LINKS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-accent/10 text-accent'
                    : 'text-text-muted hover:text-text hover:bg-surface-2'
                }`
              }
            >
              {label}
            </NavLink>
          ))}

          {!loading && (
            isAuthenticated ? (
              <div className='flex items-center gap-2 ml-2'>
                <Link to='/wishlist'
                  className='relative p-2 rounded-lg transition-colors'
                  style={{ color: 'var(--color-text-muted)' }}
                  title='Mi wishlist'
                >
                  <Heart className='w-5 h-5' />
                  {count > 0 && (
                    <span
                      className='absolute -top-1 -right-1 text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center'
                      style={{ background: 'var(--color-accent)', color: 'var(--color-bg)' }}
                    >
                      {count > 9 ? '9+' : count}
                    </span>
                  )}
                </Link>
                <Link to='/alerts'
                  className='relative p-2 rounded-lg transition-colors'
                  style={{ color: 'var(--color-text-muted)' }}
                  title='Mis alertas de precio'
                >
                  <Bell className='w-5 h-5' />
                </Link>
                <div
                  className='flex items-center gap-2 px-3 py-1.5 rounded-lg'
                  style={{ background: 'var(--color-surface-2)' }}
                >
                  <span
                    className='inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold'
                    style={{
                      background: 'color-mix(in srgb, var(--color-accent) 20%, transparent)',
                      color: 'var(--color-accent)',
                    }}
                  >
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                  <span className='text-sm font-medium hidden lg:block' style={{ color: 'var(--color-text)' }}>
                    {user?.username}
                  </span>
                </div>
                <button onClick={logout}
                  className='flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors'
                  style={{ color: 'var(--color-text-muted)' }}
                  title='Cerrar sesion'
                >
                  <LogOut className='w-4 h-4' />
                  <span className='hidden lg:inline'>Salir</span>
                </button>
              </div>
            ) : (
              <div className='flex items-center gap-1 ml-2'>
                <NavLink to='/login'
                  className='px-3 py-1.5 rounded-lg text-sm font-medium text-text-muted hover:text-text hover:bg-surface-2 transition-colors'
                >Login</NavLink>
                <NavLink to='/register'
                  className='px-3 py-1.5 rounded-lg text-sm font-semibold bg-accent text-bg hover:brightness-110 transition-all'
                >Registrarse</NavLink>
              </div>
            )
          )}
        </nav>
        <button
          onClick={() => setMenuOpen((v) => !v)}
          className='md:hidden flex-shrink-0 p-2 rounded-lg text-text-muted hover:text-text hover:bg-surface-2 transition-colors'
          aria-label='Abrir menu'
        >
          {menuOpen ? <X className='w-5 h-5' /> : <Menu className='w-5 h-5' />}
        </button>
      </div>

      {menuOpen && (
        <div className='md:hidden border-t border-border bg-bg/95 backdrop-blur'>
          <nav className='container mx-auto px-4 py-3 flex flex-col gap-1'>
            {NAV_LINKS.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                onClick={closeMenu}
                className={({ isActive }) =>
                  `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-accent/10 text-accent'
                      : 'text-text-muted hover:text-text hover:bg-surface-2'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
            {!loading && (
              isAuthenticated ? (
                <>
                  <NavLink
                    to='/wishlist'
                    onClick={closeMenu}
                    className='flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-text-muted hover:text-text hover:bg-surface-2 transition-colors'
                  >
                    <Heart className='w-4 h-4' />
                    Wishlist
                    {count > 0 && (
                      <span
                        className='text-[10px] font-bold rounded-full px-1.5'
                        style={{ background: 'var(--color-accent)', color: 'var(--color-bg)' }}
                      >
                        {count > 9 ? '9+' : count}
                      </span>
                    )}
                  </NavLink>
                  <NavLink
                    to='/alerts'
                    onClick={closeMenu}
                    className='flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-text-muted hover:text-text hover:bg-surface-2 transition-colors'
                  >
                    <Bell className='w-4 h-4' />
                    Alertas
                  </NavLink>
                  <div className='flex items-center justify-between px-3 py-2 mt-1 border-t border-border'>
                    <span className='text-sm font-medium' style={{ color: 'var(--color-text)' }}>
                      {user?.username}
                    </span>
                    <button
                      onClick={() => { closeMenu(); logout(); }}
                      className='flex items-center gap-1 text-sm font-medium text-text-muted hover:text-text'
                    >
                      <LogOut className='w-4 h-4' />
                      Salir
                    </button>
                  </div>
                </>
              ) : (
                <div className='flex flex-col gap-1 mt-1 pt-1 border-t border-border'>
                  <NavLink to='/login' onClick={closeMenu}
                    className='px-3 py-2 rounded-lg text-sm font-medium text-text-muted hover:text-text hover:bg-surface-2 transition-colors'
                  >Login</NavLink>
                  <NavLink to='/register' onClick={closeMenu}
                    className='px-3 py-2 rounded-lg text-sm font-semibold text-center bg-accent text-bg hover:brightness-110 transition-all'
                  >Registrarse</NavLink>
                </div>
              )
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
