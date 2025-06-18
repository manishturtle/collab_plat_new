'use client';

import { useState, useEffect } from 'react';
import { Box, InputBase, IconButton, useTheme, CircularProgress } from '@mui/material';
import { 
  AddCircle as AddCircleIcon, 
  SentimentSatisfiedAlt as EmojiIcon,
  Mic as MicIcon,
  Send as SendIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useChat } from '@/hooks/useChat';

interface ChatInputProps {
  onSendMessage?: (message: string) => void; // Optional now since we can use context
  placeholder?: string;
  disabled?: boolean;
}

/**
 * ChatInput component provides the input field for sending messages
 * 
 * @param props - Component properties
 * @returns A styled chat input component with action buttons
 */
const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage,
  placeholder = 'Aa',
  disabled = false
}) => {
  const [message, setMessage] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);
  const theme = useTheme();
  const { t } = useTranslation();
  const { sendMessage, currentChannel } = useChat();

  const handleSendMessage = async (): Promise<void> => {
    if (!message.trim() || disabled || isSending) return;
    
    try {
      setIsSending(true);
      
      // Use either the prop function or context function
      if (onSendMessage) {
        onSendMessage(message);
      } else {
        const success = await sendMessage(message);
        if (!success) {
          console.error('Failed to send message');
        }
      }
      
      setMessage('');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent): void => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box 
      sx={{ 
        p: 2, 
        borderTop: 1, 
        borderColor: 'divider',
        bgcolor: (theme) => theme.palette.mode === 'dark' ? 'background.paper' : '#fff',
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        position: 'relative',
        zIndex: 5
      }}
    >
      <IconButton 
        color="inherit" 
        sx={{ 
          color: 'text.secondary',
          '&:hover': { bgcolor: 'action.hover' }
        }}
      >
        <AddCircleIcon />
      </IconButton>

      <InputBase
        fullWidth
        placeholder={t(placeholder)}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyPress}
        multiline
        maxRows={4}
        sx={{
          px: 2,
          py: 1.25,
          bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100',
          borderRadius: 4,
          fontSize: '0.875rem',
          '&:focus-within': {
            boxShadow: (theme) => `0 0 0 2px ${theme.palette.primary.light}`
          }
        }}
      />

      <IconButton 
        color="inherit" 
        sx={{ 
          color: 'text.secondary',
          '&:hover': { bgcolor: 'action.hover' }
        }}
      >
        <EmojiIcon />
      </IconButton>

      <IconButton 
        color="inherit" 
        sx={{ 
          color: 'text.secondary',
          '&:hover': { bgcolor: 'action.hover' }
        }}
      >
        <MicIcon />
      </IconButton>

      <IconButton 
        onClick={handleSendMessage}
        disabled={!message.trim() || disabled || isSending || !currentChannel}
        color="primary" 
        sx={{ 
          bgcolor: message.trim() && !isSending && currentChannel ? 'primary.main' : 'action.disabledBackground',
          color: message.trim() && !isSending && currentChannel ? 'common.white' : 'text.disabled',
          '&:hover': { 
            bgcolor: message.trim() && !isSending && currentChannel ? 'primary.dark' : 'action.disabledBackground' 
          },
          width: 40,
          height: 40,
        }}
        aria-label={t('Send message')}
      >
        {isSending ? (
          <CircularProgress size={20} color="inherit" />
        ) : (
          <SendIcon fontSize="small" />
        )}
      </IconButton>
    </Box>
  );
};

export default ChatInput;
