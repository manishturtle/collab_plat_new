'use client';

import { ChatProvider } from '@/context/chatContext';
import Header from '@/components/Header';

/**
 * DashboardLayout component provides the common layout structure for dashboard pages
 * including header and content area (sidebar removed as requested)
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ChatProvider>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <Header />
        
        {/* Main content area */}
        <main style={{
          flexGrow: 1,
          overflow: 'auto',
          padding: '20px'
        }}>
          {children}
        </main>
      </div>
    </ChatProvider>
  );
}
