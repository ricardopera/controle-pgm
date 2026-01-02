/**
 * Auth Context tests.
 * 
 * Note: These are basic smoke tests. Full integration tests
 * require a proper mock server setup.
 */

import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { AuthProvider, useAuth } from './auth-context';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a wrapper with all required providers
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>{children}</AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    );
  };
}

describe('AuthContext', () => {
  it('provides initial state', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    // Initially loading state should be true
    expect(result.current.isLoading).toBe(true);
    // User should be null until loaded
    expect(result.current.user).toBe(null);
    // Functions should be defined
    expect(typeof result.current.login).toBe('function');
    expect(typeof result.current.logout).toBe('function');
  });

  it('throws error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within an AuthProvider');

    consoleSpy.mockRestore();
  });
});

// Import vi for the spy
import { vi } from 'vitest';
