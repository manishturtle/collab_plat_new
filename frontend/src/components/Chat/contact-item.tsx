'use client';

import { Box, Typography, Avatar, Badge } from '@mui/material';

interface ContactItemProps {
  id: string | number;
  name: string;
  avatar: string; // URL to the avatar image
  isSelected?: boolean;
  isOnline?: boolean;
  unreadCount?: number;
  onClick: () => void;
}

/**
 * ContactItem component renders an individual contact or chat conversation
 * in the contacts/chats sidebar list
 * 
 * @param props - Component properties
 * @returns A styled contact list item component
 */

const ContactItem: React.FC<ContactItemProps> = ({
  id,
  name,
  avatar,
  isSelected = false,
  isOnline = false,
  unreadCount = 0,
  onClick,
}) => {
  return (
    <Box
      onClick={onClick}
      sx={{
        display: 'flex',
        alignItems: 'center',
        p: 1.5,
        px: 2,
        cursor: 'pointer',
        borderRadius: 1.5,
        mb: 0.5,
        transition: 'all 0.2s ease',
        bgcolor: isSelected ? (theme) => theme.palette.mode === 'dark' ? 'rgba(99, 102, 241, 0.15)' : 'rgba(99, 102, 241, 0.08)' : 'transparent',
        '&:hover': {
          bgcolor: (theme) => !isSelected && (theme.palette.mode === 'dark' ? 'action.hover' : 'rgba(0, 0, 0, 0.04)'),
        },
        ...(isSelected && {
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
        })
      }}
    >
      <Box position="relative">
        <Avatar
          src={avatar}
          alt={name}
          sx={{
            width: 42,
            height: 42,
            mr: 2,
            fontSize: '1.1rem',
            fontWeight: 'bold',
            bgcolor: avatar ? undefined : (theme) => theme.palette.mode === 'dark' ? 'primary.dark' : 'primary.light',
          }}
        >
          {!avatar && name.charAt(0).toUpperCase()}
        </Avatar>
        {isOnline && (
          <Box
            sx={{
              position: 'absolute',
              width: 12,
              height: 12,
              bgcolor: 'success.main',
              borderRadius: '50%',
              border: '2px solid',
              borderColor: (theme) => theme.palette.mode === 'dark' ? 'background.paper' : '#fff',
              bottom: 0,
              right: 8,
            }}
          />
        )}
      </Box>
      <Box sx={{ 
        flex: 1,
        minWidth: 0 // Needed for text truncation
      }}>
        <Typography 
          variant="subtitle2" 
          sx={{ 
            fontWeight: isSelected ? 600 : 500,
            color: isSelected ? 'primary.main' : 'text.primary',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}
        >
          {name}
        </Typography>
      </Box>
      {unreadCount > 0 && (
        <Box
          sx={{
            bgcolor: 'primary.main',
            color: 'white',
            borderRadius: '50%',
            minWidth: 20,
            height: 20,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.7rem',
            fontWeight: 'bold',
            px: 1
          }}
        >
          {unreadCount > 99 ? '99+' : unreadCount}
        </Box>
      )}
    </Box>
  );
};

export default ContactItem;
