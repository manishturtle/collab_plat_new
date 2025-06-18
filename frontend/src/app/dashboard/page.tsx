'use client';

import { useState, useEffect } from 'react';
import { useMediaQuery } from '@mui/material';
import Chat from '@/components/Chat';
import ChatDetails from '@/components/Chat/chat-details';
import { useTranslation } from 'react-i18next';

/**
 * Dashboard page component that displays the main chat interface with details sidebar
 */
export default function DashboardPage() {
  const { t } = useTranslation();
  // Initialize state without immediately using the media query
  const [isDesktop, setIsDesktop] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Only run media query after component mounts
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Use media query only on client side
  const isDesktopQuery = useMediaQuery('(min-width:1200px)');
  
  // Update desktop state when query changes
  useEffect(() => {
    if (isMounted) {
      setIsDesktop(isDesktopQuery);
    }
  }, [isDesktopQuery, isMounted]);

  // Static styles
  const containerStyle = {
    height: '100%',
    display: 'flex',
    width: '100%',
    overflow: 'hidden'
  };

  const chatStyle = {
    flexGrow: 1,
    height: '100%',
    overflow: 'auto'
  };

  const chatDetailsStyle = {
    height: '100%',
    width: '320px',
    borderLeft: '1px solid #e0e0e0'
  };

  // Show loading state until we know the screen size
  if (!isMounted) {
    return <div>Loading...</div>;
  }

  return (
    <div style={containerStyle}>
      {/* Main Chat Interface */}
      <div style={chatStyle}>
        <Chat />
      </div>
      
      {/* Chat Details Sidebar - visible on desktop */}
      {isDesktop && (
        <div style={chatDetailsStyle}>
          <ChatDetails />
        </div>
      )}
    </div>
  );
}