import React from 'react';
import { Box, Tooltip, AvatarGroup, Avatar } from '@mui/material';
import { ReadReceipt, User } from '@/types/chat';
import { useTranslation } from 'react-i18next';

interface ReadReceiptsProps {
  readReceipts: ReadReceipt[];
  users: User[];
  maxAvatars?: number;
}

const ReadReceipts: React.FC<ReadReceiptsProps> = ({
  readReceipts,
  users,
  maxAvatars = 3
}) => {
  const { t } = useTranslation();
  
  if (!readReceipts || readReceipts.length === 0) {
    return null;
  }
  
  // Find user info for each receipt
  const receiptsWithUsers = readReceipts.map(receipt => {
    const user = users.find(u => u.id === receipt.user_id);
    return {
      ...receipt,
      user
    };
  }).filter(receipt => receipt.user); // Only include receipts where we found the user
  
  if (receiptsWithUsers.length === 0) {
    return null;
  }
  
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'flex-end',
        mt: 0.5
      }}
    >
      <Tooltip
        title={
          <div>
            {t('Read by')}:
            <ul style={{ margin: '4px 0 0 0', paddingLeft: '16px' }}>
              {receiptsWithUsers.map(receipt => (
                <li key={receipt.user_id}>
                  {receipt.user?.full_name || t('Unknown user')}
                  {' • '}
                  {new Date(receipt.read_at).toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </li>
              ))}
            </ul>
          </div>
        }
        arrow
        placement="top"
      >
        <AvatarGroup
          max={maxAvatars}
          sx={{
            '& .MuiAvatar-root': {
              width: 16,
              height: 16,
              fontSize: '0.75rem',
              border: 'none',
              '&:last-child': {
                marginLeft: '-8px'
              }
            }
          }}
        >
          {receiptsWithUsers.map(receipt => (
            <Avatar
              key={receipt.user_id}
              alt={receipt.user?.full_name || t('Unknown user')}
              src={receipt.user?.avatar_url || undefined}
              sx={{
                backgroundColor: 'primary.main',
                fontSize: '0.6rem'
              }}
            >
              {(receipt.user?.first_name?.[0] || '') + (receipt.user?.last_name?.[0] || '')}
            </Avatar>
          ))}
        </AvatarGroup>
      </Tooltip>
    </Box>
  );
};

export default ReadReceipts;
