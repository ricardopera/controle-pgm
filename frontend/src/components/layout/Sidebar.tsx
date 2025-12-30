/**
 * Sidebar navigation component.
 * Displays navigation links based on user role.
 */

import { NavLink } from 'react-router-dom';
import { 
  FileText, 
  History, 
  Home, 
  Settings, 
  Users 
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { cn } from '@/lib/utils';

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  {
    title: 'Início',
    href: '/',
    icon: Home,
  },
  {
    title: 'Histórico',
    href: '/historico',
    icon: History,
  },
  {
    title: 'Tipos de Documento',
    href: '/tipos-documento',
    icon: FileText,
    adminOnly: true,
  },
  {
    title: 'Usuários',
    href: '/usuarios',
    icon: Users,
    adminOnly: true,
  },
  {
    title: 'Configurações',
    href: '/configuracoes',
    icon: Settings,
    adminOnly: true,
  },
];

export function Sidebar() {
  const { isAdmin } = useAuth();

  const filteredNavItems = navItems.filter(
    (item) => !item.adminOnly || isAdmin
  );

  return (
    <aside className="fixed left-0 top-14 z-30 hidden h-[calc(100vh-3.5rem)] w-64 shrink-0 border-r md:block">
      <nav className="h-full overflow-y-auto py-6 pr-6 pl-4">
        <ul className="space-y-1">
          {filteredNavItems.map((item) => (
            <li key={item.href}>
              <NavLink
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                    isActive
                      ? 'bg-secondary text-secondary-foreground'
                      : 'text-muted-foreground hover:bg-secondary/50 hover:text-secondary-foreground'
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.title}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}

/**
 * Mobile navigation component.
 * Shows navigation links in a horizontal scrollable bar on mobile.
 */
export function MobileNav() {
  const { isAdmin } = useAuth();

  const filteredNavItems = navItems.filter(
    (item) => !item.adminOnly || isAdmin
  );

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background md:hidden">
      <ul className="flex items-center justify-around py-2">
        {filteredNavItems.slice(0, 5).map((item) => (
          <li key={item.href}>
            <NavLink
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex flex-col items-center gap-1 px-2 py-1 text-xs transition-colors',
                  isActive
                    ? 'text-primary'
                    : 'text-muted-foreground hover:text-primary'
                )
              }
            >
              <item.icon className="h-5 w-5" />
              <span className="sr-only md:not-sr-only">{item.title}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
