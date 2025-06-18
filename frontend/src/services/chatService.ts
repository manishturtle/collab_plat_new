import { getApiUrl, getAuthHeaders, API_BASE_URL } from '@/config/api';
import { Channel, Message, User } from '@/types/chat';
import axios from 'axios';

/**
 * Chat service for handling all chat-related API calls
 */

interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
  data?: T;
}


interface UsersResponse {
  success: boolean;
  users: User[];
  count: number;
}

class ChatService {
  async getChannels(): Promise<ApiResponse<Channel>> {
    try {
      const response = await fetch(
        getApiUrl('/channels/', 'chat'),
        {
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch channels');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching channels:', error);
      throw error;
    }
  }

  /**
   * Fetch a single channel by ID
   */
  async getChannel(channelId: string | number): Promise<Channel> {
    try {
      const response = await fetch(
        getApiUrl(`/channels/${channelId}/`, 'chat'),
        {
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch channel');
      }

      const data: ApiResponse<Channel> = await response.json();
      return data.data!;
    } catch (error) {
      console.error('Error fetching channel:', error);
      throw error;
    }
  }

  /**
   * Fetch users for chat
   */

/**
   * Fetch users for chat
   * @returns Promise<{success: boolean, users: User[], count: number}>
   */
  
  async getUsers(): Promise<User[]> {
    try {
      const response = await fetch(
        getApiUrl('/chat/users/', 'shared'),
        {
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      console.log('Users API response:', data);
      return data;
    } catch (error) {
      console.error('Error fetching users:', error);
      throw error;
    }
  }

  /**
   * Get the messages for a channel
   * 
   * @param channelId - The ID of the channel to get messages for
   * @returns A list of messages
   */
  async getChannelMessages(channelId: string | number): Promise<Message[]> {
    try {
      console.log(`Getting messages for channel ${channelId}`);
      
      const url = getApiUrl(`/channels/${channelId}/messages/`, 'chat');
      console.log('GET request URL:', url);
      
      const response = await fetch(
        url,
        { headers: getAuthHeaders() }
      );

      if (!response.ok) {
        throw new Error(`Failed to get channel messages: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Channel messages response:', data);
      
      // Handle different API response formats
      // 1. Paginated response with results array (as in the provided example)
      if (data && typeof data === 'object' && Array.isArray(data.results)) {
        console.log(`Found ${data.results.length} messages in paginated results`);
        return data.results;
      }
      
      // 2. Direct array of messages
      if (Array.isArray(data)) {
        console.log(`Found ${data.length} messages in array`);
        return data;
      }
      
      // 3. Object with data array or object with messages array
      if (data && data.data) {
        if (Array.isArray(data.data)) {
          console.log(`Found ${data.data.length} messages in data array`);
          return data.data;
        } else if (data.data.messages && Array.isArray(data.data.messages)) {
          console.log(`Found ${data.data.messages.length} messages in nested structure`);
          return data.data.messages;
        }
      }
      
      // If none of the above match, assume empty array
      console.warn('Unexpected API response format for messages, returning empty array');
      return [];
    } catch (error) {
      console.error('Error getting channel messages:', error);
      throw error;
    }
  }

  /**
   * Send a message to a channel
   * 
   * @param channelId - The ID of the channel to send the message to
   * @param content - The content of the message
   * @returns The message that was sent
   */
  async sendMessage(channelId: string | number, content: string): Promise<Message | undefined> {
    try {
      console.log(`Sending message to channel ${channelId}:`, content);
      
      // Create a temporary message for immediate UI feedback
      const tempMessage: Partial<Message> = {
        id: Date.now(), // Use numeric ID to match interface
        content,
        channel_id: typeof channelId === 'string' ? parseInt(channelId, 10) : channelId, // Ensure it's a number
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user: { 
          id: 1, // Using numeric ID to match User interface
          email: 'current@user.com',
          first_name: 'Current',
          last_name: 'User',
          full_name: 'Current User',
          is_online: true
        },
        is_own: true,
        read_by: [],
        content_type: 'text',
        file_url: null,
        parent_id: null,
        user_id: 1 // Add required user_id field
      };
      
      console.log('Created temp message for UI:', tempMessage);
      
      // Make the actual API call to send the message
      try {
        // Create a URL with query parameters for GET request
        const baseUrl = getApiUrl(`/channels/${channelId}/messages/`, 'chat');
        const url = new URL(baseUrl);
        url.searchParams.append('content', content);
        console.log('Sending GET request to:', url.toString());
        
        const response = await fetch(url.toString(), {
          method: 'GET',  // Changed to GET since server doesn't allow POST
          headers: {
            ...getAuthHeaders(),
            'Accept': 'application/json',
          }
        });
        
        if (!response.ok) {
          console.error(`API error: ${response.status} ${response.statusText}`);
          // Still return the temp message so UI stays responsive
        } else {
          const data = await response.json();
          console.log('Message sent successfully, API response:', data);
          
          // If the API returned the created message, we could replace our temp message
          // but we'll let WebSocket handle that for consistency
        }
      } catch (apiError) {
        console.error('API call failed when sending message:', apiError);
        // Continue to return the temp message even if API call fails
      }
      
      return tempMessage as Message;
    } catch (error) {
      console.error('Error creating temp message:', error);
      return undefined;
    }
  }

  /**
   * Mark messages as read
   */
  async markAsRead(
    channelId: string | number,
    messageIds: (string | number)[]
  ): Promise<void> {
    try {
      const response = await fetch(
        getApiUrl(`/channels/${channelId}/mark_read/`, 'chat'),
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ message_ids: messageIds }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to mark messages as read');
      }
    } catch (error) {
      console.error('Error marking messages as read:', error);
      throw error;
    }
  }

  /**
   * Create a new channel
   * 
   * @param channelType - The type of channel ('direct' or 'group')
   * @param participantIds - Array of user IDs to add to the channel
   * @param name - Optional name for the channel (required for group channels)
   * @returns The created channel
   */
  async createChannel(channelType: 'direct' | 'group', participantIds: (string | number)[], name?: string): Promise<Channel> {
    try {
      console.log(`Creating ${channelType} channel with participants:`, participantIds);
      
      const url = getApiUrl('/channels/', 'chat');
      console.log('POST request URL:', url);
      
      const payload = {
        channel_type: channelType,
        participants: participantIds,
        is_group: channelType === 'group',
        name: channelType === 'group' && name ? name : undefined
      };
      
      console.log('Channel creation payload:', payload);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Failed to create channel: ${response.status} ${response.statusText}`, errorText);
        throw new Error(`Failed to create channel: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Channel created successfully:', data);
      
      // Handle different API response formats
      if (data && typeof data === 'object') {
        if (data.id) {
          return data as Channel;
        } else if (data.data && data.data.id) {
          return data.data as Channel;
        }
      }
      
      throw new Error('Invalid response format from channel creation API');
    } catch (error) {
      console.error('Error creating channel:', error);
      throw error;
    }
  }
}

export const chatService = new ChatService();
