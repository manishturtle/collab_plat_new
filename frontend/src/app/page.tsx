'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

/**
 * Home page component that redirects to the dashboard
 * Shows a loading spinner while redirecting
 */
export default function Home() {
  const router = useRouter();
  const { t } = useTranslation();

  useEffect(() => {
    // Redirect to dashboard after a short delay
    const redirectTimer = setTimeout(() => {
      router.push('/dashboard');
    }, 1500); // 1.5 second delay for smooth transition

    return () => clearTimeout(redirectTimer);
  }, [router]);

  return (
    <Box 
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#f5f5f5'
      }}
    >
      <Typography 
        variant="h4" 
        component="h1" 
        style={{ marginBottom: '24px' }}
      >
        {t('home.loading')}
      </Typography>
      <CircularProgress size={60} />
    </Box>
  );
}
