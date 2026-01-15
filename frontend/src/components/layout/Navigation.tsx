import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  Users,
  Search,
  Hash,
  BarChart3,
  Network,
  Settings,
} from 'lucide-react';
import { cn } from '../../lib/utils';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/books', icon: BookOpen, label: 'Torah' },
  { to: '/names', icon: Users, label: 'Names' },
  { to: '/search', icon: Search, label: 'Search' },
  { to: '/gematria', icon: Hash, label: 'Gematria' },
  { to: '/stats', icon: BarChart3, label: 'Statistics' },
  { to: '/graph', icon: Network, label: 'Graph' },
  { to: '/admin', icon: Settings, label: 'Admin' },
];

export function Navigation() {
  return (
    <nav className="space-y-1">
      {navItems.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg',
              'text-sm font-medium transition-all duration-200',
              isActive
                ? 'bg-gold-700/20 text-gold-400 border-l-2 border-gold-500'
                : 'text-parchment-200/70 hover:text-parchment-100 hover:bg-ink-lighter/50'
            )
          }
        >
          <Icon className="w-5 h-5" />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
