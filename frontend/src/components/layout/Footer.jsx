import { Gamepad2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-border mt-auto">
      <div className="container mx-auto px-4 py-6 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-text-muted text-sm">
          <Gamepad2 className="w-4 h-4 text-accent" />
          <span>© 2025 GameDeals — TFG DAM</span>
        </div>
        <nav className="flex items-center gap-4 text-sm text-text-muted">
          <Link to="/" className="hover:text-accent transition-colors">Home</Link>
          <Link to="/deals" className="hover:text-accent transition-colors">Deals</Link>
          <Link to="/free" className="hover:text-accent transition-colors">Free</Link>
        </nav>
      </div>
    </footer>
  );
}
