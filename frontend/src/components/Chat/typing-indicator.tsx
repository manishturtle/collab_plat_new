import React from 'react';
import { Box, Typography, Avatar } from '@mui/material';
import { User } from '@/types/chat';
import { useTranslation } from 'react-i18next';

interface TypingIndicatorProps {
  typingUsers: User[];
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ typingUsers }) => {
  const { t } = useTranslation();
  
  if (!typingUsers.length) {
    return null;
  }
  
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        px: 2,
        py: 1,
        mb: 1
      }}
    >
      {typingUsers.length === 1 && (
        <Avatar
          alt={typingUsers[0].full_name}
          src={typingUsers[0].avatar_url || undefined}
          sx={{ width: 28, height: 28, mr: 1 }}
        />
      )}
      
      <Box sx={{ 
        borderRadius: 2,
        px: 2,
        py: 0.75,
        background: (theme) => 
          theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)',
        display: 'flex',
        alignItems: 'center'
      }}>
        <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
          {typingUsers.length === 1 
            ? `${typingUsers[0].full_name} ${t('is typing')}` 
            : `${typingUsers.length} ${t('people are typing')}`}
        </Typography>
        <Box sx={{ display: 'flex', ml: 1 }}>
          <Box
            component="span"
            sx={{
              width: 4,
              height: 4,
              borderRadius: '50%',
              backgroundColor: 'text.secondary',
              mx: 0.2,
              animation: 'dotPulse 1.5s infinite ease-in-out',
              '&:nth-of-type(1)': { animationDelay: '0s' },
              '&:nth-of-type(2)': { animationDelay: '0.2s' },
              '&:nth-of-type(3)': { animationDelay: '0.4s' },
              '@keyframes dotPulse': {
                '0%': { opacity: 0.4, transform: 'scale(1)' },
                '50%': { opacity: 1, transform: 'scale(1.3)' },
                '100%': { opacity: 0.4, transform: 'scale(1)' }
              }
            }}
          />
          <Box
            component="span"
            sx={{
              width: 4,
              height: 4,
              borderRadius: '50%',
              backgroundColor: 'text.secondary',
              mx: 0.2,
              animation: 'dotPulse 1.5s infinite ease-in-out',
              '&:nth-of-type(1)': { animationDelay: '0s' },
              '&:nth-of-type(2)': { animationDelay: '0.2s' },
              '&:nth-of-type(3)': { animationDelay: '0.4s' },
              '@keyframes dotPulse': {
                '0%': { opacity: 0.4, transform: 'scale(1)' },
                '50%': { opacity: 1, transform: 'scale(1.3)' },
                '100%': { opacity: 0.4, transform: 'scale(1)' }
              }
            }}
          />
          <Box
            component="span"
            sx={{
              width: 4,
              height: 4,
              borderRadius: '50%',
              backgroundColor: 'text.secondary',
              mx: 0.2,
              animation: 'dotPulse 1.5s infinite ease-in-out',
              '&:nth-of-type(1)': { animationDelay: '0s' },
              '&:nth-of-type(2)': { animationDelay: '0.2s' },
              '&:nth-of-type(3)': { animationDelay: '0.4s' },
              '@keyframes dotPulse': {
                '0%': { opacity: 0.4, transform: 'scale(1)' },
                '50%': { opacity: 1, transform: 'scale(1.3)' },
                '100%': { opacity: 0.4, transform: 'scale(1)' }
              }
            }}
          />
        </Box>
      </Box>
    </Box>
  );
};

export default TypingIndicator;
