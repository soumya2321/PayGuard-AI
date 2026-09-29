/**
 * ProtectedRoute.tsx - Route guard restricting access to authenticated users.
 * Redirects unauthenticated requests to /login while preserving origin path for post-login return.
 */

import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../features/auth/hooks/useAuth';
import { LoadingSpinner } from '../components/LoadingSpinner';

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-3">
        <LoadingSpinner />
        <span className="text-xs text-slate-400 font-mono">Verifying authentication session...</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to /login with original location stored in state
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};
