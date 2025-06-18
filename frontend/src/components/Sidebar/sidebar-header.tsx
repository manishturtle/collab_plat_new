'use client';

import { Box, Typography } from '@mui/material';
import Image from 'next/image';

/**
 * SidebarHeader component displays the logo and app name in the sidebar
 * 
 * @returns Header component for the sidebar
 */
const SidebarHeader: React.FC = () => {
  return (
    <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
      <Box 
        sx={{ 
          width: 32, 
          height: 32, 
          position: 'relative',
          flexShrink: 0
        }}
      >
        <Image
          src="/images/logo.png"
          alt="MantaUI Logo"
          layout="fill"
          objectFit="contain"
        />
      </Box>
      <Typography 
        variant="h5" 
        component="span" 
        sx={{ 
          fontWeight: 700,
          color: 'text.primary'
        }}
      >
        MantaUI
      </Typography>
    </Box>
  );
};

export default SidebarHeader;
