'use client';

import { Box, Typography, Button } from '@mui/material';
import { Upgrade as UpgradeIcon } from '@mui/icons-material';

/**
 * SidebarFooter component displays the upgrade section at the bottom of the sidebar
 * 
 * @returns Footer component for the sidebar
 */
const SidebarFooter: React.FC = () => {
  return (
    <Box sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
      <Box 
        sx={{ 
          bgcolor: 'primary.ultraLight', 
          p: 2, 
          borderRadius: 2, 
          textAlign: 'center' 
        }}
      >
        <Box 
          sx={{ 
            width: 48, 
            height: 48, 
            bgcolor: 'primary.light', 
            borderRadius: '50%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            mx: 'auto',
            mb: 1.5
          }}
        >
          <UpgradeIcon sx={{ color: 'primary.main' }} />
        </Box>
        <Typography 
          variant="subtitle2" 
          sx={{ 
            mb: 0.5, 
            color: 'text.primary', 
            fontWeight: 600,
            fontSize: '0.875rem'
          }}
        >
          Upgrade &amp; Unlock all features
        </Typography>
        <Button 
          variant="text" 
          color="primary"
          size="small"
          sx={{ 
            fontSize: '0.75rem', 
            fontWeight: 600,
            textTransform: 'none',
            '&:hover': {
              bgcolor: 'transparent',
              textDecoration: 'underline'
            }
          }}
        >
          Manage your plan →
        </Button>
      </Box>
    </Box>
  );
};

export default SidebarFooter;
