'use client';

import React, { useRef, useEffect, useContext } from 'react';
import { Box, Typography, Avatar } from '@mui/material';
import { Message, User } from '@/types/chat';
import { useTranslation } from 'react-i18next';
import { useTheme } from '@mui/material/styles';
import MessageReactions from './message-reactions';
import ReactionPicker from './reaction-picker';
import ReadReceipts from './read-receipts';
import TypingIndicator from './typing-indicator';
import { ChatContext } from '@/context/chatContext';

interface MessageListProps {
  messages: Message[];
  dateSeparators?: { [key: string]: boolean };
  typingUsers?: User[];
  unreadIndex?: number;
}

/**
 * MessageList component displays a list of chat messages with appropriate styling
 * and date separators.
 * 
 * @param props - Component properties
 * @returns The message list component with all messages styled according to sender
 */
const MessageList = ({
  messages,
  dateSeparators = {},
  unreadIndex,
  typingUsers = [],
}: MessageListProps) => {
  // Use chat context for current user, reactions and read receipts
  const { 
    addReaction, 
    removeReaction, 
    markAsRead,
    users,
    currentUser,
  } = useContext(ChatContext);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();
  const { t } = useTranslation();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length]);

  // Format timestamp to readable time
  const formatTime = (timestamp: string) => {
    if (!timestamp) return '';
    
    try {
      const date = new Date(timestamp);
      
      if (isNaN(date.getTime())) {
        console.error(`Invalid date: ${timestamp}`);
        return '';
      }
      
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
      console.error(`Error formatting date: ${timestamp}`, error);
      return timestamp;
    }
  };

  // Get formatted date for separators
  const getFormattedDate = (timestamp: string): string => {
    if (!timestamp) return '';
    
    try {
      const messageDate = new Date(timestamp);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      
      if (messageDate.toDateString() === today.toDateString()) {
        return t('Today');
      } else if (messageDate.toDateString() === yesterday.toDateString()) {
        return t('Yesterday');
      } else {
        return messageDate.toLocaleDateString(undefined, {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      }
    } catch (error) {
      console.error(`Error formatting date separator: ${timestamp}`, error);
      return '';
    }
  };
  
  // Group messages by date for separators
  const getMessageGroups = () => {
    if (!messages.length) return [];
    
    const groups: { date: string, messages: Message[] }[] = [];
    let currentDate = '';
    let currentGroup: Message[] = [];
    
    messages.forEach((message) => {
      if (!message.created_at) return;
      
      const messageDate = new Date(message.created_at).toDateString();
      
      if (currentDate !== messageDate) {
        if (currentGroup.length > 0) {
          groups.push({
            date: getFormattedDate(currentGroup[0].created_at),
            messages: [...currentGroup]
          });
          currentGroup = [];
        }
        currentDate = messageDate;
      }
      
      currentGroup.push(message);
    });
    
    if (currentGroup.length > 0) {
      groups.push({
        date: getFormattedDate(currentGroup[0].created_at),
        messages: [...currentGroup]
      });
    }
    
    return groups;
  };
  
  const messageGroups = getMessageGroups();

  return (
    <Box 
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 195px)',
        position: 'relative',
        width: '100%',
      }}
    >
      <Box
        ref={scrollContainerRef}
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          overflowY: 'auto',
          overflowX: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          padding: 3,
          paddingTop: 6,
          paddingBottom: 3,
          '&::-webkit-scrollbar': {
            width: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent'
          },
          '&::-webkit-scrollbar-thumb': {
            background: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
            borderRadius: '6px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
          },
        }}
      >
        {messageGroups.length > 0 ? (
          messageGroups.map((group, groupIndex) => (
            <React.Fragment key={`group-${groupIndex}`}>
              {/* Date separator */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  my: 2,
                  position: 'relative',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: '50%',
                    left: 0,
                    right: 0,
                    height: '1px',
                    backgroundColor: theme => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                    zIndex: 0
                  }
                }}
              >
                <Typography 
                  variant="caption" 
                  sx={{
                    backgroundColor: theme => theme.palette.background.default,
                    px: 2,
                    py: 0.5,
                    borderRadius: 4,
                    border: theme => `1px solid ${theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    fontWeight: 500,
                    color: 'text.secondary',
                    position: 'relative',
                    zIndex: 1
                  }}
                >
                  {group.date}
                </Typography>
              </Box>
              
              {/* Messages in this group */}
              {group.messages.map((message, index) => (
                <Box
                  key={`${message.id}-${index}`}
                  sx={{
                    display: 'flex',
                    flexDirection: message.is_own ? 'row-reverse' : 'row',
                    mb: 2,
                    alignItems: 'flex-end',
                  }}
                >
                  {!message.is_own && (
                    <Avatar
                      src={message.user?.avatar_url || ''}
                      sx={{ width: 36, height: 36, mr: 1 }}
                    >
                      {(() => {
                        // Try to get the avatar initial from different potential sources
                        if (message.user?.full_name) {
                          return message.user.full_name.charAt(0);
                        } 
                        // Try to find user by user_id
                        else if (message.user_id && users.length > 0) {
                          const matchingUser = users.find(u => String(u.id) === String(message.user_id));
                          return matchingUser?.full_name?.charAt(0) || matchingUser?.username?.charAt(0) || '?';
                        }
                        // Try the sender object
                        else if (message.sender?.username) {
                          return message.sender.username.charAt(0);
                        }
                        return '?';
                      })()}
                    </Avatar>
                  )}
                  
                  <Box sx={{ position: 'relative', maxWidth: '70%', '&:hover .reaction-picker': { opacity: 1 } }}>
                    {/* Reaction picker that shows on hover */}
                    <Box
                      className="reaction-picker"
                      sx={{
                        position: 'absolute',
                        right: message.is_own ? 'auto' : -12,
                        left: message.is_own ? -12 : 'auto',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        opacity: 0,
                        transition: 'opacity 0.2s ease',
                        zIndex: 10,
                        backgroundColor: theme => theme.palette.background.paper,
                        borderRadius: '50%',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                        padding: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '28px',
                        height: '28px',
                        cursor: 'pointer',
                        '&:hover': {
                          backgroundColor: theme => theme.palette.action.hover,
                          transform: 'translateY(-50%) scale(1.1)'
                        }
                      }}
                    >
                      <ReactionPicker 
                        messageId={message.id} 
                        onAddReaction={(messageId, reaction) => addReaction(messageId, reaction)} 
                      />
                    </Box>
                    
                    <Box
                      className="message-container"
                      sx={{
                        position: 'relative',
                        px: 2.5,
                        py: 1.5,
                        borderRadius: 3,
                        boxShadow: '0 1px 2px rgba(0,0,0,0.07)',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          boxShadow: '0 3px 8px rgba(0,0,0,0.05)',
                        },
                        ...(message.is_own
                          ? {
                              ml: 1,
                              background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                              color: 'white',
                              borderBottomRightRadius: 0.5,
                            }
                          : {
                              mr: 1,
                              bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.800' : 'grey.50',
                              borderBottomLeftRadius: 0.5,
                            }),
                      }}
                      onMouseEnter={() => {
                        // When user hovers on an unread message, mark it as read
                        if (!message.is_own && !message.is_read) {
                          markAsRead(message.id);
                        }
                      }}
                    >
                      {!message.is_own && (
                        <Typography variant="caption" color="textSecondary" fontWeight="bold">
                          {(() => {
                            // Try to find user name from multiple potential sources
                            if (message.user?.full_name) {
                              return message.user.full_name;
                            } 
                            // Try to find user by user_id from the users array
                            else if (message.user_id && users.length > 0) {
                              const matchingUser = users.find(u => String(u.id) === String(message.user_id));
                              return matchingUser?.full_name || matchingUser?.username || 'Unknown';
                            }
                            // Try the sender object as a fallback
                            else if (message.sender?.username) {
                              return message.sender.username;
                            }
                            return 'Unknown';
                          })()}
                        </Typography>
                      )}
                      
                      <Typography 
                        variant="body1"
                        sx={{ 
                          fontWeight: 400,
                          lineHeight: 1.6,
                          letterSpacing: '0.01em',
                        }}
                      >
                        {message.content}
                      </Typography>
                      
                      <Box sx={{ 
                        display: 'flex', 
                        justifyContent: message.is_own ? 'space-between' : 'flex-start',
                        alignItems: 'center',
                        mt: 0.5,
                        flexWrap: 'wrap'
                      }}>
                        <Typography
                          variant="caption"
                          sx={{
                            opacity: message.is_own ? 0.8 : 0.6,
                            fontSize: '0.65rem',
                            fontWeight: 500,
                          }}
                        >
                          {formatTime(message.created_at || '')}
                        </Typography>
                        
                        {message.is_own && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            {message.is_read && (
                              <Typography 
                                variant="caption" 
                                sx={{ 
                                  fontSize: '0.65rem',
                                  fontWeight: 500,
                                  opacity: 0.8,
                                  display: 'flex',
                                  alignItems: 'center'
                                }}
                              >
                                {t('read')}
                              </Typography>
                            )}
                          </Box>
                        )}
                      </Box>
                      
                      {/* Show message reactions if any */}
                      {message.reactions && message.reactions.length > 0 && (
                        <MessageReactions 
                          reactions={message.reactions} 
                          onAddReaction={(reaction) => addReaction(message.id, reaction)}
                          onRemoveReaction={(reaction) => removeReaction(message.id, reaction)}
                          currentUserId={currentUser?.id || 0}
                        />
                      )}
                    </Box>
                    
                    {/* Show read receipts for own messages */}
                    {message.is_own && message.read_receipts && message.read_receipts.length > 0 && (
                      <ReadReceipts 
                        readReceipts={message.read_receipts}
                        users={users || []}
                      />
                    )}
                  </Box>
                </Box>
              ))}
            </React.Fragment>
          ))
        ) : (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
              textAlign: 'center',
            }}
          >
            <Typography variant="body1" color="text.secondary" gutterBottom>
              {t('No messages yet')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('Send a message to start the conversation')}
            </Typography>
          </Box>
        )}
        
        {/* Show typing indicator */}
        {typingUsers && typingUsers.length > 0 && (
          <TypingIndicator typingUsers={typingUsers} />
        )}
        
        {/* Invisible element to scroll to */}
        <div ref={messagesEndRef} />
      </Box>
    </Box>
  );
};

export default MessageList;

