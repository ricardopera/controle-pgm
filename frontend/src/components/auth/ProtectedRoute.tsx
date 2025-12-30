/**
 * Protected Route component.
 * Redirects to login if user is not authenticated.
 */

import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/lib/auth-context';
import { Header, Sidebar, MobileNav } from '@/components/layout';
import { ChangePasswordDialog } from './ChangePasswordDialog';

interface ProtectedRouteProps {
  /** Whether the route requires admin role */
  requireAdmin?: boolean;
}

export function ProtectedRoute({ requireAdmin = false }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, isAdmin, user } = useAuth();
  const location = useLocation();

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Redirect to home if admin required but user is not admin
  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  // Check if user needs to change password
  const mustChangePassword = user?.must_change_password ?? false;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 md:ml-64">
          <div className="container py-6 pb-20 md:pb-6">
            <Outlet />
          </div>
        </main>
      </div>
      <MobileNav />
      
      {/* Force password change dialog */}
      <ChangePasswordDialog open={mustChangePassword} />
    </div>
  );
}
