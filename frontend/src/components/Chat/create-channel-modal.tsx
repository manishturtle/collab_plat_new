import React, { useState } from 'react';
import {
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  TextField,
  Typography,
  Avatar,
  CircularProgress,
  Chip
} from '@mui/material';
import { User } from '@/types/chat';
import { useTranslation } from 'react-i18next';

interface CreateChannelModalProps {
  open: boolean;
  onClose: () => void;
  users: User[];
  onCreateChannel: (name: string, participantIds: (string | number)[]) => Promise<void>;
  isLoading?: boolean;
}

const CreateChannelModal: React.FC<CreateChannelModalProps> = ({
  open,
  onClose,
  users,
  onCreateChannel,
  isLoading = false
}) => {
  const { t } = useTranslation();
  const [channelName, setChannelName] = useState('');
  const [selectedUsers, setSelectedUsers] = useState<(string | number)[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleToggleUser = (userId: string | number) => {
    setSelectedUsers(prev => 
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSubmit = async () => {
    setError(null);
    
    if (!channelName.trim()) {
      setError(t('Please enter a channel name'));
      return;
    }

    if (selectedUsers.length === 0) {
      setError(t('Please select at least one participant'));
      return;
    }

    try {
      await onCreateChannel(channelName.trim(), selectedUsers);
      handleReset();
      onClose();
    } catch (err: any) {
      setError(err.message || t('Failed to create channel'));
    }
  };

  const handleReset = () => {
    setChannelName('');
    setSelectedUsers([]);
    setError(null);
  };

  const getUserName = (user: User): string => {
    if (user.full_name) {
      return user.full_name;
    }
    return `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.email || 'Unknown User';
  };

  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  return (
    <Dialog 
      open={open} 
      onClose={!isLoading ? onClose : undefined}
      fullWidth
      maxWidth="sm"
    >
      <DialogTitle>{t('Create New Channel')}</DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <TextField
            label={t('Channel Name')}
            fullWidth
            value={channelName}
            onChange={(e) => setChannelName(e.target.value)}
            margin="normal"
            disabled={isLoading}
            autoFocus
          />
          
          {error && (
            <Typography color="error" variant="body2" sx={{ mt: 1 }}>
              {error}
            </Typography>
          )}

          <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
            {t('Selected Participants')}: {selectedUsers.length}
          </Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {selectedUsers.map(userId => {
              const user = users.find(u => u.id === userId);
              if (!user) return null;
              
              return (
                <Chip 
                  key={userId}
                  label={getUserName(user)}
                  onDelete={() => handleToggleUser(userId)}
                  disabled={isLoading}
                />
              );
            })}
          </Box>
        </Box>
        
        <Typography variant="subtitle1" sx={{ mt: 2 }}>
          {t('Select Participants')}
        </Typography>
        
        <List sx={{ 
          maxHeight: '300px', 
          overflow: 'auto',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
          mt: 1
        }}>
          {users.map(user => (
            <ListItem 
              key={user.id} 
              dense
              button
              onClick={() => handleToggleUser(user.id)}
              disabled={isLoading}
            >
              <FormControlLabel
                control={
                  <Checkbox 
                    checked={selectedUsers.includes(user.id)}
                    onChange={() => handleToggleUser(user.id)}
                    disabled={isLoading}
                  />
                }
                label=""
                sx={{ mr: 0 }}
              />
              <ListItemAvatar>
                <Avatar>
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt={getUserName(user)} />
                  ) : (
                    getInitials(getUserName(user))
                  )}
                </Avatar>
              </ListItemAvatar>
              <ListItemText 
                primary={getUserName(user)}
                secondary={user.email || ''}
              />
            </ListItem>
          ))}
        </List>
      </DialogContent>

      <DialogActions>
        <Button 
          onClick={() => {
            handleReset();
            onClose();
          }}
          disabled={isLoading}
        >
          {t('Cancel')}
        </Button>
        <Button 
          onClick={handleSubmit}
          variant="contained"
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={20} /> : null}
        >
          {isLoading ? t('Creating...') : t('Create Channel')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateChannelModal;
