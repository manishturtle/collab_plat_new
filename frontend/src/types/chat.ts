// Types for chat functionality

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  username?: string; // Adding username property to fix TypeScript error
  is_online: boolean;
  avatar_url?: string | null;
  last_seen?: string | null;
  status?: string | null;
  status_emoji?: string | null;
}

// Message reaction interface
export interface MessageReaction {
  id: number;
  message_id: number;
  user_id: number;
  user?: User;
  reaction: string;
  created_at: string;
}

// Read receipt interface
export interface ReadReceipt {
  user_id: number;
  user?: User;
  read_at: string;
}

export interface Message {
  id: number;
  content: string;
  user: User;
  is_own: boolean;
  created_at: string;
  updated_at?: string;
  channel_id: number;
  read_by: Array<string | User>; // Can be either user IDs or user objects
  content_type: string;
  file_url: string | null;
  parent_id: number | null;
  user_id: number;
  // Enhanced features
  reactions?: MessageReaction[];
  read_receipts?: ReadReceipt[];
  is_read?: boolean; // Whether the current user has read this message
}

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Participation {
  id: number;
  user: User;
  role: string;
  created_at: string;
  user_id: number;
  channel_id: string;
}


export interface Channel {
  id: string;
  name: string;
  channel_type: 'direct' | 'group' | 'contextual_object';
  participations: Participation[];
  last_message: Message | null;
  unread_count: number;
  created_at: string;
  updated_at: string;
  host_application_id: string;
  context_object_type: string;
  context_object_id: string;
  created_by: number;
  updated_by: number;
  company_id: number;
  client_id: number;
}
export interface ChatState {
  channels: Channel[];
  currentChannel: Channel | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onlineUsers: Set<string | number>;
}

export interface SendMessagePayload {
  content: string;
  content_type?: string;
  file_url?: string;
  parent_id?: string | number;
}

export interface MarkAsReadPayload {
  message_ids: (string | number)[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
