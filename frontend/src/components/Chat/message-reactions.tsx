import React from 'react';
import { Box, Tooltip, Typography } from '@mui/material';
import { MessageReaction } from '@/types/chat';
import { useTranslation } from 'react-i18next';

interface MessageReactionsProps {
  reactions: MessageReaction[];
  onAddReaction?: (reaction: string) => void;
  onRemoveReaction?: (reaction: string) => void;
  currentUserId: number;
}

interface GroupedReactions {
  [key: string]: {
    count: number;
    users: number[];
  };
}

const MessageReactions: React.FC<MessageReactionsProps> = ({
  reactions,
  onAddReaction,
  onRemoveReaction,
  currentUserId
}) => {
  const { t } = useTranslation();
  
  // Group reactions by emoji
  const groupedReactions: GroupedReactions = reactions.reduce((grouped, reaction) => {
    const emoji = reaction.reaction;
    
    if (!grouped[emoji]) {
      grouped[emoji] = {
        count: 0,
        users: []
      };
    }
    
    grouped[emoji].count++;
    grouped[emoji].users.push(reaction.user_id);
    
    return grouped;
  }, {} as GroupedReactions);
  
  // Convert to array for rendering
  const reactionItems = Object.entries(groupedReactions).map(([emoji, details]) => {
    const isReactedByCurrentUser = details.users.includes(currentUserId);
    
    return {
      emoji,
      count: details.count,
      isReactedByCurrentUser,
      userIds: details.users
    };
  });
  
  if (reactionItems.length === 0) {
    return null;
  }
  
  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 0.5,
        mt: 0.5
      }}
    >
      {reactionItems.map((item) => (
        <Tooltip
          key={item.emoji}
          title={`${item.count} ${item.count === 1 ? t('reaction') : t('reactions')}`}
          arrow
        >
          <Box
            onClick={() => {
              if (item.isReactedByCurrentUser) {
                onRemoveReaction?.(item.emoji);
              } else {
                onAddReaction?.(item.emoji);
              }
            }}
            sx={{
              display: 'flex',
              alignItems: 'center',
              borderRadius: '12px',
              pl: 0.5,
              pr: 0.5,
              py: 0.25,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              backgroundColor: (theme) => 
                item.isReactedByCurrentUser 
                  ? (theme.palette.mode === 'dark' ? 'rgba(144, 202, 249, 0.16)' : 'rgba(33, 150, 243, 0.08)')
                  : (theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'),
              '&:hover': {
                backgroundColor: (theme) => 
                  theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
              }
            }}
          >
            <Typography sx={{ fontSize: '0.85rem', mr: 0.25 }}>{item.emoji}</Typography>
            <Typography 
              variant="caption"
              sx={{ 
                fontWeight: item.isReactedByCurrentUser ? 600 : 400,
                fontSize: '0.7rem'
              }}
            >
              {item.count}
            </Typography>
          </Box>
        </Tooltip>
      ))}
    </Box>
  );
};

export default MessageReactions;
