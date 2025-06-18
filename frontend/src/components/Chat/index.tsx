'use client';

import React, { useState, useEffect } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useChat } from '@/hooks/useChat';
import { Channel, User } from '@/types/chat';
import ContactsList from './contacts-list';
import ChatHeader from './chat-header';
import MessageList from './message-list';
import ChatInput from './chat-input';
import { useTranslation } from 'react-i18next';

// Define types for our data
type Contact = User & {
  lastMessage?: string;
  timestamp?: string;
  isUnread?: boolean;
};

type Message = {
  id: string | number;
  sender: {
    id: string | number;
    name: string;
    avatar: string;
    isOnline?: boolean;
  };
  content: string;
  timestamp: string;
  isTyping?: boolean;
  isCurrentUser?: boolean;
  read_by?: Array<{ id: string | number }>;
};

type Conversation = Channel & {
  participant: Contact;
  messages: Message[];
  unreadCount?: number;
}



/**
 * Main Chat component that combines ContactsList, ChatHeader, MessageList,
 * and ChatInput to create a complete chat interface
 * 
 * @returns A fully functional chat interface component
 */
const Chat = () => {
  const { t } = useTranslation();
  const [selectedId, setSelectedId] = useState<string | number | undefined>(undefined);
  const [selectedType, setSelectedType] = useState<'channel' | 'user'>('channel');
  const [isLoading, setIsLoading] = useState(true);
  
  const {
    channels,
    users,
    currentChannel,
    messages,
    selectChannel,
    sendMessage,
    startNewChat,
    isLoading: isChatLoading,
    error,
  } = useChat();

  // Debug logging
  useEffect(() => {
    console.log('Current channel:', currentChannel);
    console.log('All messages in context:', messages);
    if (currentChannel?.id) {
      const channelMessages = messages[String(currentChannel.id)];
      console.log('Messages for current channel:', {
        channelId: currentChannel.id,
        channelMessages,
        messagesCount: channelMessages?.length || 0,
        firstMessage: channelMessages?.[0],
        lastMessage: channelMessages?.[channelMessages.length - 1]
      });
    }
  }, [currentChannel, messages]);
  
  // Format messages for the UI
  const formatMessages = (rawMessages: any[]) => {
    if (!rawMessages || !Array.isArray(rawMessages)) {
      console.warn('Invalid messages format:', rawMessages);
      return [];
    }
    
    console.log('[formatMessages] Raw message sample:', rawMessages.length > 0 ? rawMessages[0] : 'No messages');
    
    return rawMessages.map(msg => {
      // Create a compatible message object that matches the Message interface expected by MessageList
      const formattedMessage = {
        id: msg.id,
        content: msg.content,
        timestamp: msg.created_at || new Date().toISOString(),
        created_at: msg.created_at || new Date().toISOString(),
        updated_at: msg.updated_at,
        is_own: msg.is_own || false,
        isCurrentUser: msg.is_own || false, // For compatibility
        channel_id: msg.channel_id,
        user_id: msg.user_id,
        read_by: msg.read_by || [],
        content_type: msg.content_type || 'text/plain',
        file_url: msg.file_url,
        parent_id: msg.parent_id,
        user: msg.user || {
          id: msg.user_id,
          email: '',
          first_name: '',
          last_name: '',
          full_name: 'Unknown User',
          is_online: false
        },
        // For backward compatibility with components expecting sender property
        sender: {
          id: msg.user?.id || msg.user_id || 'unknown',
          name: msg.user?.full_name || 'Unknown User',
          avatar: msg.user?.avatar_url || '',
          isOnline: msg.user?.is_online || false
        },
        reactions: msg.reactions || [],
        read_receipts: msg.read_receipts || [],
        is_read: msg.is_read || false,
      };
      
      return formattedMessage;
    });
  };
  
  // Get messages for the current channel with enhanced debugging
  const currentMessages = React.useMemo(() => {
    if (!currentChannel?.id) {
      console.log('[Chat] No current channel selected');
      return [];
    }
    
    const channelId = String(currentChannel.id);
    const channelMessages = messages[channelId];
    
    // Debug log the current state
    console.log('[Chat] Current channel messages state:', {
      channelId,
      hasChannelMessages: !!channelMessages,
      messagesCount: channelMessages?.length || 0,
      allChannelsWithMessages: Object.keys(messages),
      currentChannel: currentChannel
    });
    
    if (!channelMessages) {
      console.log(`[Chat] No messages found for channel ${channelId}`);
      return [];
    }
    
    if (!Array.isArray(channelMessages)) {
      console.error('[Chat] Channel messages is not an array:', channelMessages);
      return [];
    }
    
    // Force an explicit created_at timestamp on any messages that might be missing it
    const messagesWithTimestamps = channelMessages.map(msg => {
      if (!msg.created_at) {
        return {
          ...msg,
          created_at: new Date().toISOString() // Add timestamp if missing
        };
      }
      return msg;
    });
    
    // Ensure messages are sorted by created_at in ascending order (oldest first)
    const sortedMessages = [...messagesWithTimestamps].sort((a, b) => {
      const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
      const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
      return dateA - dateB; // Ascending order (oldest first, newest last)
    });
    
    console.log(`[Chat] Returning ${sortedMessages.length} messages for channel ${channelId}`);
    return formatMessages(sortedMessages);
  }, [currentChannel, messages]);

  useEffect(() => {
    // Load initial data
    const loadData = async () => {
      try {
        setIsLoading(true);
        // The useChat hook should handle loading channels and users
      } catch (err) {
        console.error('Error loading chat data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  // Handle chat selection
  const handleSelect = (id: string | number, type: 'channel' | 'user') => {
    setSelectedId(id);
    setSelectedType(type);
    
    console.log(`Selected ${type} with id ${id}`);
    
    // Call API to load channel or user data
    if (type === 'channel') {
      selectChannel(id.toString());
    } else if (type === 'user') {
      // For direct messages, we need to either find the existing DM channel or create a new one
      const existingDM = channels.find(c => 
        c.channel_type === 'direct' && 
        c.participants?.some(p => p.id === id)
      );
      
      if (existingDM) {
        selectChannel(existingDM.id.toString());
      } else {
        // Create a new DM channel with this user
        console.log(`Creating new DM with user ${id}`);
        startNewChat([id]).then(channel => {
          if (channel) {
            console.log('Created new DM channel:', channel);
            selectChannel(channel.id.toString());
          }
        }).catch(error => {
          console.error('Failed to create DM channel:', error);
        });
      }
    }
  };
  
  // Handle sending a message
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) {
      return; // Don't send empty messages
    }
    
    if (selectedType === 'user' && !currentChannel) {
      // For direct messaging to a user without an existing channel
      try {
        console.log(`Creating a direct message channel with user ${selectedId}`);
        const newChannel = await startNewChat([selectedId]);
        if (newChannel) {
          await selectChannel(newChannel.id.toString());
          // Wait a moment for the channel to be selected
          setTimeout(() => {
            sendMessage(content);
          }, 300);
        }
      } catch (error) {
        console.error('Failed to create direct message channel:', error);
      }
    } else if (currentChannel) {
      // For existing channels or after channel created
      sendMessage(content);
    } else {
      console.error('Cannot send message: No channel selected');
    }
  };

  if (isLoading || isChatLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ 
      display: 'flex', 
      height: 'calc(100vh - 65px)', // Subtract header height if there's a global header
      maxHeight: '100vh', 
      overflow: 'hidden', // Prevent whole page scrolling
      position: 'relative', // For absolute positioning of children if needed
      bgcolor: (theme) => theme.palette.mode === 'dark' ? 'background.default' : '#f5f7fb',
      p: 1.5
    }}>
      {/* Left Panel - Contacts List */}
      <Box sx={{ 
        width: 320, 
        borderRadius: 2,
        overflow: 'hidden',
        bgcolor: 'background.paper',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: (theme) => theme.palette.mode === 'dark' ? 'none' : '0 0 20px rgba(0,0,0,0.05)',
        mr: 2
      }}>
        <ContactsList
          channels={channels}
          users={users}
          onSelect={handleSelect}
          selectedId={selectedId}
          isLoading={isChatLoading}
        />
      </Box>

      {/* Center/Right - Chat Area */}
      <Box sx={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        overflow: 'hidden', // Prevent outer container from scrolling
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: (theme) => theme.palette.mode === 'dark' ? 'none' : '0 0 20px rgba(0,0,0,0.05)',
      }}>
        {selectedId !== undefined ? (
          <>
            <ChatHeader
              name={
                selectedType === 'channel'
                  ? channels.find(c => c.id === selectedId)?.name || 'Channel'
                  : (() => {
                      const user = users.find(u => u.id === selectedId);
                      return user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() : 'User';
                    })()
              }
              avatar={
                selectedType === 'user'
                  ? users.find(u => u.id === selectedId)?.avatar_url || ''
                  : channels.find(c => c.id === selectedId)?.avatar_url || ''
              }
              memberCount={
                selectedType === 'channel'
                  ? (channels.find(c => c.id === selectedId) as any)?.member_count || 0
                  : undefined
              }
            />
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <Box sx={{ 
                flex: 1, 
                display: 'flex', 
                flexDirection: 'column', 
                minHeight: 0,
                overflow: 'hidden',
                position: 'relative'
              }}>
                <MessageList
                  messages={currentMessages}
                  key={`message-list-${currentChannel?.id || 'no-channel'}`}
                />
              </Box>
            </Box>
            <ChatInput onSendMessage={handleSendMessage} />
          </>
        ) : (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
              color: 'text.secondary',
              p: 4,
              textAlign: 'center'
            }}
          >
            <Box
              component="img"
              src="/images/empty-chat.svg"
              alt="Empty chat"
              sx={{ width: 200, height: 200, opacity: 0.6, mb: 3 }}
              onError={(e) => {
                // If image fails to load, use a fallback icon or hide the image
                e.currentTarget.style.display = 'none';
              }}
            />
            <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold' }}>
              {t('Select a conversation')}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400 }}>
              {t('Choose a user or group from the list to start messaging')}
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
export default Chat;
