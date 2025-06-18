'use client';

import { Box, Typography, IconButton, Avatar, AvatarGroup, Chip, Tooltip } from '@mui/material';
import { Phone, Videocam, MoreHoriz, Group } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface ChatHeaderProps {
  avatar: string;
  name: string;
  memberCount?: number;
}

/**
 * ChatHeader component displays the current chat conversation header
 * with participant info and action buttons
 * 
 * @param props - Component properties
 * @returns A styled header component for chat interface
 */
const ChatHeader: React.FC<ChatHeaderProps> = ({ 
  avatar, 
  name, 
  memberCount 
}) => {
  const { t } = useTranslation();
  
  // Generate a background color based on the name (for consistent avatar colors per channel)
  const getStringColor = (str: string) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = Math.abs(hash) % 360;
    return `hsl(${hue}, 70%, 60%)`; // Bright, saturated color
  };
  
  // Use the first letter or first letters of words
  const getInitials = (name: string) => {
    const words = name.trim().split(/\s+/);
    if (words.length > 1) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };
  
  return (
    <Box 
      sx={{
        p: 2,
        borderBottom: 1,
        borderColor: 'divider',
        bgcolor: (theme) => theme.palette.mode === 'dark' ? 'background.paper' : '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
        position: 'sticky',
        top: 0,
        zIndex: 10,
        height: '72px',
        minHeight: '72px',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)'
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 2,
        flex: 1,
        minWidth: 0, // Prevents overflow
      }}>
        <Box sx={{ 
          position: 'relative',
          '&:after': {
            content: '""',
            position: 'absolute',
            bottom: 0,
            right: 0,
            width: 12,
            height: 12,
            bgcolor: 'success.main',
            borderRadius: '50%',
            border: '2px solid',
            borderColor: (theme) => theme.palette.mode === 'dark' ? 'background.paper' : '#fff',
            display: memberCount === undefined ? 'block' : 'none'
          }
        }}>
          <Avatar 
            src={avatar} 
            alt={name} 
            sx={{ 
              width: 48, 
              height: 48,
              bgcolor: avatar ? undefined : getStringColor(name),
              color: 'white',
              fontWeight: 'bold',
              fontSize: '1.3rem',
              boxShadow: (theme) => theme.shadows[2]
            }}
          >
            {getInitials(name)}
          </Avatar>
        </Box>
        <Box sx={{ 
          minWidth: 0, // Allows text truncation
          '& > *': {
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }
        }}>
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 700,
              color: 'text.primary',
              fontSize: '1.15rem',
              lineHeight: 1.3,
              m: 0
            }}
          >
            {name}
          </Typography>
          {memberCount !== undefined && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 0.75,
              mt: 0.25
            }}>
              <Group sx={{ 
                fontSize: 16, 
                color: 'text.secondary',
                opacity: 0.8 
              }} />
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'text.secondary',
                  fontSize: '0.8rem',
                  fontWeight: 500,
                  letterSpacing: '0.01em'
                }}
              >
                {t('{{count}} members', { count: memberCount })}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
      
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center',
        gap: 0.5,
        ml: 1,
        '& > button': {
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'translateY(-1px)',
            bgcolor: 'action.hover',
          },
          '&:active': {
            transform: 'translateY(0)',
          }
        }
      }}>
        <Tooltip title={t('Start audio call')}>
          <IconButton 
            size="medium"
            sx={{ 
              color: 'text.secondary',
              bgcolor: 'transparent',
              '&:hover': { 
                bgcolor: 'action.hover',
                color: 'primary.main',
                boxShadow: 1
              }
            }}
          >
            <Phone fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Tooltip title={t('Start video call')}>
          <IconButton 
            size="medium"
            sx={{ 
              color: 'text.secondary',
              bgcolor: 'transparent',
              '&:hover': { 
                bgcolor: 'action.hover',
                color: 'primary.main',
                boxShadow: 1
              }
            }}
          >
            <Videocam fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Tooltip title={t('More options')}>
          <IconButton 
            size="medium"
            sx={{ 
              color: 'text.secondary',
              bgcolor: 'transparent',
              '&:hover': { 
                bgcolor: 'action.hover',
                color: 'primary.main',
                boxShadow: 1
              }
            }}
          >
            <MoreHoriz fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default ChatHeader;
