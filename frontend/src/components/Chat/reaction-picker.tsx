import React, { useState } from 'react';
import { Box, Popover, IconButton, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

// Common emoji reactions
const COMMON_REACTIONS = ['👍', '❤️', '😊', '🎉', '👏', '🙌', '🔥', '✅'];

interface ReactionPickerProps {
  messageId: number;
  onAddReaction: (messageId: number, reaction: string) => void;
}

const ReactionPicker: React.FC<ReactionPickerProps> = ({ 
  messageId, 
  onAddReaction 
}) => {
  const { t } = useTranslation();
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleReactionSelect = (reaction: string) => {
    onAddReaction(messageId, reaction);
    handleClose();
  };

  const open = Boolean(anchorEl);
  const id = open ? 'reaction-popover' : undefined;

  return (
    <>
      <IconButton 
        size="small" 
        onClick={handleClick}
        sx={{ 
          fontSize: '1rem',
          opacity: 0.6,
          '&:hover': { opacity: 1 },
          color: 'text.secondary'
        }}
      >
        😊
      </IconButton>
      
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          p: 1, 
          bgcolor: 'background.paper',
          borderRadius: 1,
          boxShadow: 3
        }}>
          {COMMON_REACTIONS.map((emoji) => (
            <Box 
              key={emoji}
              component="button"
              onClick={() => handleReactionSelect(emoji)}
              sx={{
                cursor: 'pointer',
                border: 'none',
                bgcolor: 'transparent',
                fontSize: '1.5rem',
                p: 0.5,
                borderRadius: '50%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                '&:hover': {
                  bgcolor: 'action.hover',
                },
                transition: 'all 0.2s ease'
              }}
            >
              {emoji}
            </Box>
          ))}
        </Box>
      </Popover>
    </>
  );
};

export default ReactionPicker;
