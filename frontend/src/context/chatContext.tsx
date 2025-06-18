'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { Channel, Message, User, ChatState } from '@/types/chat';
import { chatService } from '@/services/chatService';
import { webSocketService } from '@/services/websocketService';

// Define a generic paginated response interface to handle API responses
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}


/**
 *   State Management:
    Created a ChatContext to manage chat state
    Implemented actions for sending messages, loading channels, etc.
    Added WebSocket integration for real-time updates

 * 
 */

    interface ChatContextType extends ChatState {
      sendMessage: (content: string) => Promise<boolean>;
      selectChannel: (channelId: string | number) => Promise<void>;
      loadMoreMessages: (channelId: string | number) => Promise<void>;
      markMessagesAsRead: (messageIds: (string | number)[]) => Promise<void>;
      startNewChat: (userIds: (string | number)[]) => Promise<Channel | null>;
      setTyping: (isTyping: boolean) => void;
      getUsers: () => Promise<User[]>;
      // New methods for enhanced features
      addReaction: (messageId: string | number, reaction: string) => Promise<boolean>;
      removeReaction: (messageId: string | number, reaction: string) => Promise<boolean>;
      markAsRead: (messageId: string | number) => Promise<boolean>;
    }

    interface ChatState {
      channels: Channel[];
      users: User[]; // Add users to the state
      currentChannel: Channel | null;
      currentUser: User | null; // Add currentUser to the state
      messages: { [channelId: string]: Message[] };
      isLoading: boolean;
      error: string | null;
      onlineUsers: Set<string | number>;
      typingUsers: { [channelId: string]: { [userId: string]: boolean } };
      // Track who is currently typing in each channel
      reactionsLoading: { [messageId: string]: boolean }; // Track loading state for reactions
      readReceiptsLoading: { [messageId: string]: boolean }; // Track loading state for read receipts
    }
    

const initialState: ChatState = {
  channels: [],
  currentChannel: null,
  currentUser: null,
  messages: {},
  users: [],
  typingUsers: {},
  reactionsLoading: {},
  readReceiptsLoading: {},
  isLoading: false,
  error: null,
  onlineUsers: new Set(),
};


export const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider = ({ children }: ChatProviderProps) => {
  const [state, setState] = useState<ChatState>(initialState);
  
  // Track temporary message IDs to help prevent duplicates
  const [tempMessageIds, setTempMessageIds] = useState<Set<string | number>>(new Set());

  // Set up WebSocket event listeners for reactions and read receipts
  useEffect(() => {
    // Listen for read receipt events
    const unsubscribeReadReceipt = webSocketService.on('message_read', (data) => {
      const { messageId, userId, channelId } = data;

      setState(prevState => {
        // Find the message and update its read_receipts
        if (prevState.messages[channelId]) {
          const updatedMessages = prevState.messages[channelId].map(message => {
            if (message.id === messageId) {
              // Create or update read receipts
              const existingReadReceipts = message.read_receipts || [];
              const newReadReceipt = {
                user_id: userId,
                read_at: data.readAt
              };

              // Check if we already have a read receipt from this user
              const existingIndex = existingReadReceipts.findIndex(r => r.user_id === userId);
              let updatedReadReceipts;

              if (existingIndex >= 0) {
                // Update existing receipt
                updatedReadReceipts = [
                  ...existingReadReceipts.slice(0, existingIndex),
                  newReadReceipt,
                  ...existingReadReceipts.slice(existingIndex + 1)
                ];
              } else {
                // Add new receipt
                updatedReadReceipts = [...existingReadReceipts, newReadReceipt];
              }

              return {
                ...message,
                read_receipts: updatedReadReceipts
              };
            }
            return message;
          });

          return {
            ...prevState,
            messages: {
              ...prevState.messages,
              [channelId]: updatedMessages
            },
            readReceiptsLoading: {
              ...prevState.readReceiptsLoading,
              [messageId]: false
            }
          };
        }
        return prevState;
      });
    });

    // Listen for reaction events
    const unsubscribeReaction = webSocketService.on('reaction', (data) => {
      const { messageId, userId, reaction, action, channelId } = data;

      setState(prevState => {
        // Find the message and update its reactions
        if (prevState.messages[channelId]) {
          const updatedMessages = prevState.messages[channelId].map(message => {
            if (message.id === messageId) {
              const existingReactions = message.reactions || [];

              if (action === 'add') {
                // Add reaction if it doesn't exist already
                const newReaction = {
                  id: Date.now(), // Temporary ID until server syncs
                  message_id: messageId,
                  user_id: userId,
                  reaction,
                  created_at: data.timestamp
                };

                // Check if user already reacted with this emoji
                const existingIndex = existingReactions.findIndex(
                  r => r.user_id === userId && r.reaction === reaction
                );

                if (existingIndex === -1) {
                  return {
                    ...message,
                    reactions: [...existingReactions, newReaction]
                  };
                }
              } else if (action === 'remove') {
                // Remove the reaction
                const filteredReactions = existingReactions.filter(
                  r => !(r.user_id === userId && r.reaction === reaction)
                );

                return {
                  ...message,
                  reactions: filteredReactions
                };
              }
            }
            return message;
          });

          return {
            ...prevState,
            messages: {
              ...prevState.messages,
              [channelId]: updatedMessages
            },
            reactionsLoading: {
              ...prevState.reactionsLoading,
              [messageId]: false
            }
          };
        }
        return prevState;
      });
    });

    return () => {
      unsubscribeReadReceipt();
      unsubscribeReaction();
    };
  }, []);

  // Define selectChannel first to avoid reference issues
  const selectChannel = useCallback(async (channelId: string | number): Promise<void> => {
    try {
      const channelIdStr = String(channelId);

      
      // First update to mark loading and find channel from the most current state
      setState(prev => {
        // Find channel within the setState callback to ensure latest data
        const channel = prev.channels.find(c => String(c.id) === channelIdStr) || null;
        
        return {
          ...prev,
          currentChannel: channel,
          isLoading: true
        };
      });
      
      // Get the latest state after the update
      const currentState = await new Promise<ChatState>(resolve => {
        setState(prevState => {
          resolve(prevState);
          return prevState;
        });
      });
      
      // Only fetch messages if we found a channel
      if (currentState.currentChannel) {
        const messages = await chatService.getChannelMessages(channelId);
        
        // Make sure messages are sorted chronologically (oldest to newest)
        const messageArray = Array.isArray(messages) ? messages : (messages as PaginatedResponse<Message>)?.results || [];
        
        // Sort messages by created_at timestamp to ensure they appear in chronological order
        const sortedMessages = [...messageArray].sort((a, b) => {
          const dateA = new Date(a.created_at).getTime();
          const dateB = new Date(b.created_at).getTime();
          return dateA - dateB; // Ascending order (oldest first, newest last)
        });
        
        setState(prev => ({
          ...prev,
          messages: {
            ...prev.messages,
            [channelIdStr]: sortedMessages
          },
          isLoading: false
        }));
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false
        }));
      }
    } catch (error) {
      console.error('Error selecting channel:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to load channel',
        isLoading: false
      }));
    }
  }, []); // No dependencies to avoid re-creation

  // Load initial data
  useEffect(() => {
    let isMounted = true;
    
    const loadInitialData = async () => {
      try {
        setState(prev => ({ ...prev, isLoading: true }));
        
        // Load channels and users in parallel
        const [channelsResponse, usersResponse] = await Promise.all([
          chatService.getChannels(),
          chatService.getUsers(),
        ]);

        if (!isMounted) return;

        // Log the responses to debug
        console.log('Channels response:', channelsResponse);
        console.log('Users response:', usersResponse);

        // Define paginated response type to fix the TypeScript error
        interface PaginatedResponse<T> {
          results?: T[];
          users?: T[];
          count?: number;
          next?: string | null;
          previous?: string | null;
        }
        
        // Handle both array and paginated responses for channels
        let channels: Channel[] = [];
        if (Array.isArray(channelsResponse)) {
          channels = channelsResponse;
        } else {
          // Type assertion to handle paginated response
          const typedResponse = channelsResponse as PaginatedResponse<Channel>;
          if (typedResponse?.results && Array.isArray(typedResponse.results)) {
            channels = typedResponse.results;
          }
        }
        
        // Handle both array and paginated responses for users
        let usersList: User[] = [];
        if (Array.isArray(usersResponse)) {
          usersList = usersResponse;
        } else {
          // Type assertion to handle paginated response
          const typedResponse = usersResponse as PaginatedResponse<User>;
          if (typedResponse?.results && Array.isArray(typedResponse.results)) {
            usersList = typedResponse.results;
          } else if (typedResponse?.users && Array.isArray(typedResponse.users)) {
            usersList = typedResponse.users;
          }
        }

        // Update state with loaded data
        setState(prev => ({
          ...prev,
          channels,
          users: usersList,
          isLoading: false,
        }));

        // Select the first channel if available
        if (channels.length > 0 && !state.currentChannel) {
          const firstChannelId = String(channels[0].id);
          // Use the local selectChannel function instead of the one from the state
          await selectChannel(firstChannelId);
        }
      } catch (error) {
        if (!isMounted) return;
        console.error('Error loading initial chat data:', error);
        setState(prev => ({
          ...prev,
          error: 'Failed to load chat data',
          isLoading: false,
        }));
      }
    };

    loadInitialData();

    return () => {
      isMounted = false;
    };
  }, [selectChannel]); // Remove state.currentChannel dependency to prevent infinite reloading

  const loadMoreMessages = useCallback(async (): Promise<void> => {
    if (!state.currentChannel?.id || state.isLoading) return;

    try {
      setState(prev => ({ ...prev, isLoading: true }));
      
      // Get the oldest message ID to fetch messages older than that
      const channelId = String(state.currentChannel.id);
      const currentMessages = state.messages[channelId] || [];
      const oldestMessage = currentMessages.length > 0 ? currentMessages[currentMessages.length - 1] : null;
      const oldestMessageId = oldestMessage?.id;
      
      // Fetch older messages
      const response = await chatService.getChannelMessages(
        channelId,
        oldestMessageId ? { before: String(oldestMessageId) } : undefined
      );
      
      // Handle both array and paginated responses
      // Define paginated response type to fix the TypeScript error
      interface PaginatedResponse<T> {
        results?: T[];
        count?: number;
        next?: string | null;
        previous?: string | null;
      }
      
      let olderMessages: Message[] = [];
      if (Array.isArray(response)) {
        olderMessages = response;
      } else {
        // Type assertion to handle paginated response
        const typedResponse = response as PaginatedResponse<Message>;
        if (typedResponse?.results && Array.isArray(typedResponse.results)) {
          olderMessages = typedResponse.results;
        }
      }
      
      if (olderMessages.length > 0) {
        setState(prev => {
          const updatedMessages = { ...prev.messages };
          const existingMessages = updatedMessages[channelId] || [];
          
          // Filter out any duplicates that might come from the API
          const newMessages = olderMessages.filter(
            (newMsg: Message) => !existingMessages.some(existing => String(existing.id) === String(newMsg.id))
          );
          
          return {
            ...prev,
            messages: {
              ...updatedMessages,
              // Older messages should be added at the beginning of the array
              [channelId]: [
                ...newMessages,  // Older messages first
                ...existingMessages  // Existing messages after
              ]
            },
            isLoading: false
          };
        });
      } else {
        setState(prev => ({ ...prev, isLoading: false }));
      }
    } catch (error) {
      console.error('Error loading more messages:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to load more messages',
        isLoading: false,
      }));
    }
  }, [state.currentChannel?.id]);

  // Handle WebSocket messages
  useEffect(() => {
    if (!state.currentChannel) return;
    const currentChannelId = String(state.currentChannel.id);
    console.log('Setting up WebSocket for channel:', currentChannelId);

    const handleNewMessage = (data: any) => {
      console.log('Received WebSocket message:', data);
      
      // Check if data is a string (error message) and handle it gracefully
      if (typeof data === 'string') {
        console.error('Received string message instead of object:', data);
        
        // Create a system message to display the error
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          content: `System: ${data}`,
          user_id: 'system',
          user: { id: 'system', full_name: 'System', username: 'System' },
          channel_id: state.currentChannel?.id || '',
          created_at: new Date().toISOString(),
          is_read: true,
          is_own: false,
          updated_at: new Date().toISOString(),
          content_type: 'system'
        };
        
        // Add the error message to the state
        setState(prev => {
          const channelId = String(state.currentChannel?.id);
          const updatedMessages = { ...prev.messages };
          const currentMessages = updatedMessages[channelId] || [];
          updatedMessages[channelId] = [...currentMessages, errorMessage];
          return { ...prev, messages: updatedMessages };
        });
        
        return;
      }
      
      // Handle different message formats
      let message: Message;
      
      if (data && data.message && typeof data.message === 'object') {
        message = data.message;
        // Ensure timestamp exists
        if (!message.created_at) {
          message.created_at = new Date().toISOString();
        }
        
        // Find and attach the full user object if only user_id is available
        if (message.user_id && !message.user && state.users.length > 0) {
          const matchingUser = state.users.find(u => String(u.id) === String(message.user_id));
          if (matchingUser) {
            message.user = matchingUser;
          }
        }
      } else if (data && data.type === 'chat.message' && data.content) {
        // Extract user information from incoming message
        const userId = data.user_id || (data.sender ? data.sender.id : null) || 'unknown';
        
        // First check if we have this user in our existing users array
        let userObject = null;
        
        if (state.users.length > 0) {
          // Try to find matching user by ID
          userObject = state.users.find(u => String(u.id) === String(userId));
        }
        
        // If user not found in local state but message contains user data, use that
        if (!userObject) {
          if (data.user && typeof data.user === 'object') {
            userObject = data.user;
          } else if (data.sender && typeof data.sender === 'object') {
            // Convert sender to user format if possible
            userObject = {
              ...data.sender,
              full_name: data.sender.full_name || data.sender.username || 'User ' + userId.substring(0, 4)
            };
          }
        }
        
        // Create fallback user object if we still don't have user info
        const fallbackUser = {
          id: userId,
          full_name: `User ${userId.substring(0, 4)}`,
          username: `user_${userId.substring(0, 4)}`
        };
        
        // Get current user info for ownership determination
        const currentUserId = state.currentUser?.id;
        
        // Properly determine if this message is from the current user
        // Check multiple possible fields where the sender ID could be found
        const messageUserId = userId || data.sender_id || data.user_id || (data.user && data.user.id);
        const isOwnMessage = Boolean(currentUserId && messageUserId && 
          (String(currentUserId) === String(messageUserId)));
        
        console.log('Message ownership check:', {
          currentUserId,
          messageUserId,
          isOwnMessage
        });
        
        // Format the message if it comes in a different structure
        message = {
          id: data.id || `temp-${Date.now()}`,
          content: data.content,
          user_id: userId,
          sender: data.sender || userObject || fallbackUser,
          channel_id: data.channel_id || currentChannelId,
          created_at: data.timestamp || new Date().toISOString(),
          is_read: false,
          // Enhanced ownership check
          is_own: isOwnMessage,
          user: userObject || fallbackUser,
          read_by: [],
          updated_at: data.timestamp || new Date().toISOString(),
          content_type: 'text'
        } as unknown as Message;
        
        // Log the processed message info
        console.log('Processed WebSocket message with user:', { 
          userId, 
          userName: message.user?.full_name || message.user?.username,
          source: userObject ? 'found in users' : (data.user ? 'from message data' : 'fallback')
        });
      } else {
        // If we can't parse it as a message, just log it
        console.log('Unhandled WebSocket message format:', data);
        return;
      }
      
      const channelId = String(message.channel_id || currentChannelId);
      
      setState(prev => {
        const updatedMessages = { ...prev.messages };
        const currentMessages = updatedMessages[channelId] || [];
        
        // Check if the exact message ID already exists in our messages
        const exactIdMatch = currentMessages.some(
          msg => String(msg.id) === String(message.id)
        );
        
        // For WebSocket messages, check more extensively for temporary messages 
        // that have now been confirmed by the server
        const potentialDuplicates = currentMessages.filter(msg => {
          // Check various ID formats (temp IDs or any format)
          const isTempId = typeof msg.id === 'string' && 
            (String(msg.id).startsWith('temp-') || msg.id.includes('temp'));
          const isTimestampId = typeof msg.id === 'number' || 
            (typeof msg.id === 'string' && !isNaN(Number(msg.id)) && String(msg.id).length > 8);
          const hasMatchingUserId = msg.user_id === message.user_id || 
            msg.sender_id === message.sender_id;
            
          // Check content matches (exact match or substring)
          const contentExactMatch = msg.content === message.content;
          
          // Check timestamps are close (use a larger window of 10 seconds)
          const msgDate = new Date(msg.created_at || msg.timestamp).getTime();
          const newMsgDate = new Date(message.created_at || message.timestamp).getTime();
          const timeClose = Math.abs(msgDate - newMsgDate) < 10000; // 10 seconds
          
          // Consider a match if we have a temp ID with matching content and timestamp,
          // or if the sender and content match closely in time
          return (isTempId || isTimestampId) && contentExactMatch && timeClose || 
                (hasMatchingUserId && contentExactMatch && timeClose);
        });
        
        // Log debugging info for message matching
        console.log('Message deduplication check:', {
          exactIdMatch,
          potentialDuplicates,
          incomingMessage: message
        });
        
        const messageExists = exactIdMatch || potentialDuplicates.length > 0;
        
        if (potentialDuplicates.length > 0) {
          // Instead of ignoring, replace the temporary message with the confirmed one
          const updatedChannelMessages = currentMessages.map(msg => {
            // Find the first potential duplicate to replace
            const isDuplicate = potentialDuplicates.some(dup => dup.id === msg.id);
            if (isDuplicate) {
              console.log('Replacing temporary message with confirmed one:', {
                old: msg,
                new: message
              });
              return {
                ...message,
                // Keep any client-side properties we need
                _replaced: true,
                _original_temp_id: msg.id
              };
            }
            return msg;
          });
          
          updatedMessages[channelId] = updatedChannelMessages;
          console.log('Replaced temporary message with confirmed one');
          return { ...prev, messages: updatedMessages };
        } else if (!messageExists) {
          // Only add if the message doesn't exist in any form
          updatedMessages[channelId] = [...currentMessages, message];
          console.log('Added new message to state');
          return { ...prev, messages: updatedMessages };
        }
        
        return prev;
      });
    };

    const handleUserTyping = (data: any) => {
      console.log('Received typing indicator:', data);
      
      // Extract user ID and typing status from various possible formats
      let userId: string | number = data.user_id || data.userId;
      let isTyping = data.is_typing || data.isTyping;
      
      if (!userId || isTyping === undefined) {
        console.log('Invalid typing data format:', data);
        return;
      }
      
      const channelId = String(state.currentChannel?.id);
      if (!channelId) return;
      
      setState(prev => {
        return {
          ...prev,
          typingUsers: {
            ...prev.typingUsers || {},
            [channelId]: {
              ...prev.typingUsers?.[channelId] || {},
              [String(userId)]: Boolean(isTyping)
            }
          }
        };
      });
    };

    const handleUserOnline = (data: any) => {
      console.log('User came online:', data);
      const userId = data.userId || data.user_id;
      
      if (!userId) return;
      
      setState(prev => ({
        ...prev,
        onlineUsers: new Set(prev.onlineUsers).add(String(userId)),
      }));
    };

    const handleUserOffline = (data: any) => {
      console.log('User went offline:', data);
      const userId = data.userId || data.user_id;
      
      if (!userId) return;
      
      const newOnlineUsers = new Set(state.onlineUsers);
      newOnlineUsers.delete(String(userId));
      setState(prev => ({
        ...prev,
        onlineUsers: newOnlineUsers,
      }));
    };
    
    const handleWebSocketError = (data: any) => {
      console.error('WebSocket error:', data);
      setState(prev => ({
        ...prev,
        error: data.error || 'WebSocket connection error'
      }));
    };
    
    const handleWebSocketConnected = (data: any) => {
      console.log('WebSocket connected:', data);
      setState(prev => ({
        ...prev,
        error: null
      }));
    };

    // Only connect WebSocket if we have a current channel
    if (state.currentChannel?.id) {
      console.log('Connecting to WebSocket for channel:', currentChannelId);
      webSocketService.connect(currentChannelId);

      // Subscribe to WebSocket events
      const unsubMessage = webSocketService.on('message', handleNewMessage);
      const unsubTyping = webSocketService.on('typing', handleUserTyping);
      const unsubOnline = webSocketService.on('user_online', handleUserOnline);
      const unsubOffline = webSocketService.on('user_offline', handleUserOffline);
      const unsubError = webSocketService.on('error', handleWebSocketError);
      const unsubConnected = webSocketService.on('connected', handleWebSocketConnected);

      // Clean up subscriptions
      return () => {
        console.log('Cleaning up WebSocket subscriptions');
        unsubMessage();
        unsubTyping();
        unsubOnline();
        unsubOffline();
        unsubError();
        unsubConnected();
        webSocketService.disconnect();
      };
    }
  }, [state.currentChannel?.id]);
  const startNewChat = useCallback(async (userIds: (string | number)[], channelName?: string): Promise<Channel | null> => {
    try {
      if (!userIds.length) {
        throw new Error('At least one user ID is required to start a chat');
      }
      
      // Set loading state
      setState(prev => ({
        ...prev,
        isLoading: true,
        error: null
      }));
      
      // Determine if this is a direct or group chat
      const isGroup = userIds.length > 1;
      
      let newChannel: Channel;
      
      if (isGroup) {
        // For group chats, use createChannel with the provided name or generate one
        if (!channelName) {
          // Generate a default group name if not provided
          const userNames = await Promise.all(
            userIds.map(async (userId) => {
              const user = state.users.find(u => String(u.id) === String(userId));
              return user ? user.full_name || user.username : `User ${userId}`;
            })
          );
          channelName = `Group: ${userNames.join(', ')}`;
          // Truncate if too long
          if (channelName.length > 50) {
            channelName = channelName.substring(0, 47) + '...';
          }
        }
        
        console.log(`Creating group chat with participants:`, userIds);
        
        // Create a group channel
        newChannel = await chatService.createChannel(
          'group',
          userIds,
          channelName
        );
      } else {
        // For direct messages, use the new startDirectMessage method
        const otherUserId = userIds[0];
        console.log(`Starting direct message with user:`, otherUserId);
        
        newChannel = await chatService.startDirectMessage(otherUserId);
        
        // Check if we already have this channel in our list
        const existingChannel = state.channels.find(c => c.id === newChannel.id);
        if (existingChannel) {
          // If we already have this channel, just select it
          await selectChannel(existingChannel.id);
          return existingChannel;
        }
      }
      
      console.log('Channel created/retrieved:', newChannel);
      
      // Add the new channel to the channels list if it's not already there
      setState(prev => ({
        ...prev,
        channels: [newChannel, ...prev.channels.filter(c => c.id !== newChannel.id)],
        isLoading: false
      }));
      
      // Select the new channel
      await selectChannel(newChannel.id);
      
      return newChannel;
    } catch (error) {
      console.error('Error starting new chat:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to start new chat',
      }));
      throw error;
    }
  }, [selectChannel]);

  const getUsers = useCallback(async (): Promise<User[]> => {
    try {
      const response = await chatService.getUsers();
      let usersList: User[] = [];
      
      if (Array.isArray(response)) {
        usersList = response;
      } else if (response && 'results' in response && Array.isArray(response.results)) {
        usersList = response.results;
      } else if (response && 'users' in response && Array.isArray(response.users)) {
        usersList = response.users;
      }
      
      setState(prev => ({
        ...prev,
        users: usersList
      }));
      
      return usersList;
    } catch (error) {
      console.error('Error fetching users:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to load users'
      }));
      throw error;
    }
  }, []);

  // Add missing setTyping function
  const setTyping = useCallback((isTyping: boolean): void => {
    if (!state.currentChannel?.id) return;
    
    // Use the sendTypingIndicator method from WebSocketService
    webSocketService.sendTypingIndicator(isTyping);
    
    // Update local state to reflect typing status
    if (isTyping) {
      // Could update local typing state if needed
    }
  }, [state.currentChannel?.id]);

  // Send message function that uses both WebSocket and REST API
  const sendMessage = useCallback(async (content: string): Promise<boolean> => {
    if (!state.currentChannel?.id || !content.trim()) {
      console.error('Cannot send message: No channel selected or empty message');
      return false;
    }
    const channelId = state.currentChannel.id;
    try {
      // Send via WebSocket first (primary method)
      const wsSuccess = webSocketService.sendMessage(content.trim());
      
      // Get a temporary message from chat service
      const tempMessage = await chatService.sendMessage(String(channelId), content.trim());
      
      // Always ensure temp message has a timestamp
      if (tempMessage && !tempMessage.created_at) {
        tempMessage.created_at = new Date().toISOString();
      }
      
      // Mark this as a temporary message with a special flag to help with deduplication
      if (tempMessage) {
        // Add a special flag for client-generated messages
        tempMessage._client_generated = true;
        tempMessage._temp_timestamp = Date.now();
        
        // If ID isn't already prefixed, make it clearly a temp ID
        if (tempMessage.id && typeof tempMessage.id === 'string' && !tempMessage.id.startsWith('temp-')) {
          tempMessage._original_id = tempMessage.id;
          tempMessage.id = `temp-${tempMessage.id}-${Date.now()}`;
        }
        
        // Track the temporary message ID to help with deduplication
        setTempMessageIds(prev => new Set([...prev, tempMessage.id]));
      }
      
      // Add the temporary message immediately to the UI for instant feedback
      if (tempMessage) {
        console.log('Adding temp message to state:', tempMessage);
        
        setState(prev => {
          const updatedMessages = { ...prev.messages };
          const channelIdStr = String(channelId);
          const existingMessages = updatedMessages[channelIdStr] || [];
          
          // Add the message at the end for chronological order
          return {
            ...prev,
            messages: {
              ...updatedMessages,
              [channelIdStr]: [...existingMessages, tempMessage]
            }
          };
        });
        
        // Scroll to the bottom to show the new message
        setTimeout(() => {
          const messagesEndElement = document.getElementById('messages-end');
          if (messagesEndElement) {
            messagesEndElement.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
        
        return true;
      }
      
      return wsSuccess;
    } catch (error) {
      console.error('Error sending message:', error);
      return false;
    }
  }, [state.currentChannel?.id]);

  // Add missing markMessagesAsRead function
  const markMessagesAsRead = useCallback(async (messageIds: (string | number)[]): Promise<void> => {
    if (!state.currentChannel) return;
    
    try {
      const channelId = String(state.currentChannel.id);
      console.log(`Marking messages as read for channel ${channelId}:`, messageIds);
      
      // In a real implementation, you would call an API to mark messages as read
      // For now, we'll just update the local state
      setState(prev => {
        const updatedMessages = { ...prev.messages };
        const channelMessages = updatedMessages[channelId] || [];
        
        updatedMessages[channelId] = channelMessages.map(msg => 
          messageIds.includes(msg.id)
            ? { 
                ...msg, 
                read_by: [
                  ...(msg.read_by || []), 
                  { 
                    id: 0, // This should be the current user's ID
                    email: 'current-user@example.com',
                    first_name: 'Current',
                    last_name: 'User',
                    full_name: 'Current User',
                    is_online: true
                  }
                ] 
              }
            : msg
        );
        
        return { ...prev, messages: updatedMessages };
      });
    } catch (error) {
      console.error('Error marking messages as read:', error);
    }
  }, [state.currentChannel]);

  // Define a current user (this should come from your authentication system)
  // For now, we'll use a placeholder value
  const currentUserId = 0; // Replace with actual user ID from auth context
  
  // Initialize the current user with a mock user object
  useEffect(() => {
    // Create a mock user that matches the currentUserId for development purposes
    const mockCurrentUser: User = {
      id: currentUserId,
      email: 'current-user@example.com',
      first_name: 'Current',
      last_name: 'User',
      full_name: 'Current User',
      is_online: true
    };
    
    // Update the state with the mock current user
    setState(prev => ({
      ...prev,
      currentUser: mockCurrentUser
    }));
    
    // In a real implementation, you would fetch the current user from an API
    // or retrieve it from your authentication context
  }, []);

  // Add reaction to a message
  const addReaction = useCallback(async (messageId: string | number, reaction: string): Promise<boolean> => {
    if (!state.currentChannel) {
      console.error('Cannot add reaction: No channel selected');
      return false;
    }

    try {
      // Set loading state for this message/reaction
      setState(prev => ({
        ...prev,
        reactionsLoading: {
          ...prev.reactionsLoading,
          [messageId]: true
        }
      }));

      const channelId = String(state.currentChannel.id);
      
      // In a real implementation, you would call an API endpoint to add the reaction
      // await chatService.addReaction(channelId, messageId, reaction);
      
      // Send WebSocket event to notify others about the reaction using the dedicated method
      webSocketService.sendReaction(
        messageId,
        currentUserId,
        reaction,
        'add',
        channelId
      );
      
      // Optimistically update the state with the new reaction
      setState(prev => {
        const updatedMessages = { ...prev.messages };
        const channelMessages = updatedMessages[channelId] || [];
        
        updatedMessages[channelId] = channelMessages.map(msg => 
          msg.id === messageId
            ? {
                ...msg,
                reactions: [
                  ...(msg.reactions || []),
                  {
                    id: Date.now(), // Using number for ID to match MessageReaction interface
                    message_id: Number(messageId),
                    reaction,
                    user_id: currentUserId,
                    created_at: new Date().toISOString()
                  }
                ]
              }
            : msg
        );
        
        return { 
          ...prev, 
          messages: updatedMessages,
          reactionsLoading: {
            ...prev.reactionsLoading,
            [messageId]: false
          }
        };
      });
      
      return true;
    } catch (error) {
      console.error('Error adding reaction:', error);
      setState(prev => ({
        ...prev,
        reactionsLoading: {
          ...prev.reactionsLoading,
          [messageId]: false
        }
      }));
      return false;
    }
  }, [state.currentChannel]);

  // Remove reaction from a message
  const removeReaction = useCallback(async (messageId: string | number, reaction: string): Promise<boolean> => {
    if (!state.currentChannel) {
      console.error('Cannot remove reaction: No channel selected');
      return false;
    }

    try {
      // Set loading state for this message/reaction
      setState(prev => ({
        ...prev,
        reactionsLoading: {
          ...prev.reactionsLoading,
          [messageId]: true
        }
      }));

      const channelId = String(state.currentChannel.id);
      
      // In a real implementation, call an API endpoint to remove the reaction
      // await chatService.removeReaction(channelId, messageId, reaction);
      
      // Send WebSocket event to notify others about the reaction removal
      webSocketService.sendReaction(
        messageId,
        currentUserId,
        reaction,
        'remove',
        channelId
      );
      
      // Optimistically update the UI by removing the reaction
      setState(prev => {
        const updatedMessages = { ...prev.messages };
        const channelMessages = updatedMessages[channelId] || [];
        
        updatedMessages[channelId] = channelMessages.map(msg => {
          if (msg.id === messageId) {
            const updatedReactions = (msg.reactions || []).filter(
              r => !(r.reaction === reaction && r.user_id === currentUserId)
            );
            
            return {
              ...msg,
              reactions: updatedReactions
            };
          }
          return msg;
        });
        
        return { 
          ...prev, 
          messages: updatedMessages,
          reactionsLoading: {
            ...prev.reactionsLoading,
            [messageId]: false
          }
        };
      });
      
      return true;
    } catch (error) {
      console.error('Error removing reaction:', error);
      setState(prev => ({
        ...prev,
        reactionsLoading: {
          ...prev.reactionsLoading,
          [messageId]: false
        }
      }));
      return false;
    }
  }, [state.currentChannel]);

  // Mark a single message as read
  const markAsRead = useCallback(async (messageId: string | number): Promise<boolean> => {
    if (!state.currentChannel) {
      console.error('Cannot mark message as read: No channel selected');
      return false;
    }

    try {
      // Set loading state for this message
      setState(prev => ({
        ...prev,
        readReceiptsLoading: {
          ...prev.readReceiptsLoading,
          [messageId]: true
        }
      }));

      const channelId = String(state.currentChannel.id);
      
      // In a real implementation, call an API endpoint 
      // await chatService.markAsRead(channelId, messageId);
      
      // Send WebSocket event to notify others this message was read
      webSocketService.sendReadReceipt(
        messageId,
        currentUserId,
        channelId
      );
      
      // Update local state
      setState(prev => {
        const updatedMessages = { ...prev.messages };
        const channelMessages = updatedMessages[channelId] || [];
        
        updatedMessages[channelId] = channelMessages.map(msg => 
          msg.id === messageId
            ? { 
                ...msg,
                is_read: true,
                read_receipts: [
                  ...(msg.read_receipts || []),
                  {
                    user_id: currentUserId,
                    read_at: new Date().toISOString()
                  }
                ]
              }
            : msg
        );
        
        return { 
          ...prev, 
          messages: updatedMessages,
          readReceiptsLoading: {
            ...prev.readReceiptsLoading,
            [messageId]: false
          }
        };
      });
      
      return true;
    } catch (error) {
      console.error('Error marking message as read:', error);
      setState(prev => ({
        ...prev,
        readReceiptsLoading: {
          ...prev.readReceiptsLoading,
          [messageId]: false
        }
      }));
      return false;
    }
  }, [state.currentChannel, webSocketService]);

  // Create the context value object with all state and methods
  const contextValue: ChatContextType = {
    channels: state.channels,
    users: state.users,
    currentChannel: state.currentChannel,
    currentUser: state.currentUser,
    messages: state.messages,
    typingUsers: state.typingUsers,
    onlineUsers: state.onlineUsers,
    isLoading: state.isLoading,
    reactionsLoading: state.reactionsLoading,
    readReceiptsLoading: state.readReceiptsLoading,
    error: state.error,

    // Methods
    sendMessage,
    selectChannel,
    loadMoreMessages,
    markAsRead,
    markMessagesAsRead,
    startNewChat,
    setTyping,
    getUsers,
    addReaction,
    removeReaction
  };

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  );
};

// Hook for easy context usage
export const useChatContext = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};
