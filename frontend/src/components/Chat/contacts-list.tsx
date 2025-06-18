// In components/Chat/contacts-list.tsx
import React, { useState } from 'react';
import {
  Box, 
  Typography, 
  InputBase, 
  Divider,
  CircularProgress,
  Button,
  IconButton
} from '@mui/material';
import { 
  Search as SearchIcon, 
  Add as AddIcon,
  Person as PersonIcon,
  Group as GroupIcon 
} from '@mui/icons-material';
import ContactItem from './contact-item';
import { useTranslation } from 'react-i18next';
import { Channel, User } from '@/types/chat';
import CreateChannelModal from './create-channel-modal';
import { useChat } from '@/hooks/useChat';

interface ContactsListProps {
  channels: Channel[];
  users: User[]; // Make users optional with default value
  onSelect: (id: string | number, type: 'channel' | 'user', e?: React.MouseEvent) => void;
  selectedId?: string | number;
  isLoading?: boolean;
}

const ContactsList: React.FC<ContactsListProps> = ({ 
  channels = [],
  users = [], // Provide default empty array
  onSelect,
  selectedId,
  isLoading = false
}) => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const { startNewChat, currentUser } = useChat();

  
  // Filter channels based on channel type and search query
  const groupChannels = (channels || []).filter(channel => 
    channel?.channel_type === 'group' && // Only include group channels
    (channel?.name?.toLowerCase().includes(searchQuery.toLowerCase()) || false)
  );
  
  // Filter direct message channels
  const directMessageChannels = (channels || []).filter(channel => 
    channel?.channel_type === 'direct' && // Only include direct messages
    (channel?.name?.toLowerCase().includes(searchQuery.toLowerCase()) || false)
  );
  
  // Map direct message channels to their respective users for UI association
  const userDirectMessages = new Map<string | number, Channel>();
  
  if (directMessageChannels && directMessageChannels.length > 0) {
    directMessageChannels.forEach(channel => {
      if (channel.participations && channel.participations.length > 0) {
        // For each direct message channel, find the other participant that isn't the current user
        const otherParticipation = channel.participations.find(p => {
          return p.user && currentUser && p.user.id !== currentUser.id;
        });
        
        if (otherParticipation && otherParticipation.user && otherParticipation.user.id) {
          // Map the channel to the other user's ID for easy lookup
          userDirectMessages.set(otherParticipation.user.id.toString(), channel);
        }
      }
    });
  }


// Debug log to check users prop
console.log('ContactsList - users:', users);
  // Safely filter users
  const filteredUsers = (users || []).filter(user => {
    if (!user) return false;
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim().toLowerCase();
    return fullName.includes(searchQuery.toLowerCase());
  });
  

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );

  }

 

  return (
    <Box sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, mb: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" fontWeight="bold">Messages</Typography>
      </Box>
      
      {/* Create Channel Button */}
      <Box sx={{ px: 2, pb: 2 }}>
        <Button
          variant="contained"
          fullWidth
          startIcon={<AddIcon />}
          onClick={() => setCreateModalOpen(true)}
          sx={{
            borderRadius: 2,
            py: 1,
            textTransform: 'none',
            fontWeight: 600
          }}
        >
          {t('Create New Channel')}
        </Button>
      </Box>
      
      {/* Create Channel Modal */}
      <CreateChannelModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        users={users}
        isLoading={isLoading}
        onCreateChannel={async (name, participantIds) => {
          try {
            // Create a new group chat with the provided name
            const newChannel = await startNewChat(participantIds, name);
            if (newChannel) {
              // Select the newly created channel
              onSelect(newChannel.id, 'channel');
            }
            return Promise.resolve();
          } catch (error) {
            console.error('Failed to create channel:', error);
            return Promise.reject(error);
          }
        }}
      />

      <Box sx={{ p: 2, pt: 0 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.100',
            borderRadius: 2,
            px: 2,
            py: 1,
            mb: 2
          }}
        >
          <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
          <InputBase
            placeholder={t('Search...')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ flex: 1 }}
          />
        </Box>

        <Box sx={{ 
          p: 2, 
          flex: 1, 
          overflowY: 'auto',
          maxHeight: 'calc(100vh - 200px)', // Adjust based on your header/footer height
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
          },
        }}>
          {/* Users Section */}
          <Box sx={{ mb: 1, mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PersonIcon sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
              <Typography variant="subtitle2" color="text.secondary">
                {t('Users')}
              </Typography>
            </Box>
          </Box>

          {filteredUsers.map(user => {
            // Check if this user has an existing direct message channel
            const existingChannel = userDirectMessages.get(user.id.toString());
            const userName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'Unknown User';
            
            return (
              <ContactItem
                key={`user-${user.id}`}
                id={existingChannel ? existingChannel.id : user.id}
                name={userName}
                avatar={user.avatar_url || '/images/avatars/avatar-default.png'}
                isSelected={selectedId === user.id || selectedId === existingChannel?.id}
                onClick={(e) => onSelect(existingChannel ? existingChannel.id : user.id, existingChannel ? 'channel' : 'user', e)}
                isOnline={user.is_online === true} // Convert to boolean
                unreadCount={existingChannel?.unread_count || 0}
              />
            );
          })}
          
          {/* Groups Section */}
          <Box sx={{ 
            mt: 3, 
            mb: 1, 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center' 
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <GroupIcon sx={{ fontSize: 18, mr: 1, color: 'text.secondary' }} />
              <Typography variant="subtitle2" color="text.secondary">
                {t('Groups')}
              </Typography>
            </Box>
            
            {/* <IconButton 
              size="small" 
              sx={{ 
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.200',
                borderRadius: 1,
                '&:hover': {
                  bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.700' : 'grey.300',
                }
              }}
              onClick={() => console.log('Create new channel')}
              aria-label={t('Create new channel')}
            >
              <AddIcon fontSize="small" />
            </IconButton> */}
          </Box>

          {groupChannels.map(channel => (
            <ContactItem
              key={`channel-${channel.id}`}
              id={channel.id}
              name={channel.name}
              avatar={channel.avatar || '/images/avatars/group-default.png'}
              isSelected={selectedId === channel.id}
              onClick={(e) => onSelect(channel.id, 'channel', e)}
              isOnline={false}
              unreadCount={channel.unread_count}
            />
          ))}

          {/* No separate Direct Messages section - they're associated with users */}
        </Box>
      </Box>

      {/* Footer space */}
      <Box sx={{ 
        p: 2, 
        mt: 'auto', 
        borderTop: 1, 
        borderColor: 'divider',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <Typography variant="caption" color="text.secondary">
          {filteredUsers.length} {t('users')} • {groupChannels.length} {t('groups')}
        </Typography>
      </Box>
    </Box>
  );
};

export default ContactsList;