
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface TenantContextType {
  tenantSlug: string | null;
  apiBaseUrl: string;
  isLoading: boolean;
  error: Error | null;
}

const DEFAULT_TENANT_SLUG = process.env.NEXT_PUBLIC_DEFAULT_TENANT_SLUG || 'default';
const DEFAULT_API_URL = typeof window !== 'undefined' ? window.location.origin : '';

const TenantContext = createContext<TenantContextType>({
  tenantSlug: null,
  apiBaseUrl: DEFAULT_API_URL,
  isLoading: true,
  error: null,
});

export const useTenant = () => useContext(TenantContext);

interface TenantProviderProps {
  children: ReactNode;
}

export const TenantProvider = ({ children }: TenantProviderProps) => {
  const [tenantSlug, setTenantSlug] = useState<string | null>(null);
  const [apiBaseUrl, setApiBaseUrl] = useState<string>(DEFAULT_API_URL);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    try {
      const slug = 
        (typeof window !== 'undefined' && localStorage.getItem('tenant_slug')) ||
        (process.env.NODE_ENV === 'development' ? DEFAULT_TENANT_SLUG : null);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_URL;

      setTenantSlug(slug);
      setApiBaseUrl(apiUrl);
    } catch (err) {
      console.error('Error initializing tenant context:', err);
      setError(err instanceof Error ? err : new Error('Failed to initialize tenant context'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  if (isLoading) {
    return null; // or a loading spinner
  }

  return (
    <TenantContext.Provider 
      value={{ 
        tenantSlug, 
        apiBaseUrl, 
        isLoading,
        error 
      }}
    >
      {children}
    </TenantContext.Provider>
  );
};