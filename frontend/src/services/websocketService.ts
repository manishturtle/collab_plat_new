import { getWsUrl, getAuthHeaders } from '@/config/api';
import { Message, User } from '@/types/chat';

type WebSocketEvent = 'message' | 'typing' | 'user_online' | 'user_offline' | 'error' | 'connected' | 'disconnected' | 'message_read' | 'reaction';

type WebSocketCallback = (data: any) => void;

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

/**
 * WebSocket service for handling real-time chat functionality
 * Enhanced version based on websocket_test.html implementation
 */
class WebSocketService {
  private socket: WebSocket | null = null;
  private channelId: string | number | null = null;
  private eventCallbacks: Map<WebSocketEvent, WebSocketCallback[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000; // 3 seconds
  private isConnecting = false;
  private connectionStatus: 'connecting' | 'connected' | 'disconnected' = 'disconnected';
  private heartbeatInterval: NodeJS.Timeout | null = null;

  /**
   * Connect to the WebSocket server
   */
  connect(channelId: string | number): void {
    if (this.socket && this.channelId === channelId && this.connectionStatus === 'connected') {
      console.log('WebSocket already connected to this channel');
      return; // Already connected to this channel
    }

    // Get the auth token from the headers
    const authHeader = getAuthHeaders().Authorization;
    const token = authHeader.replace('Bearer ', '');

    this.channelId = channelId;
    this.disconnect(); // Close any existing connection

    try {
      // Directly construct the WebSocket URL to match the exact format from websocket_test.html
      // instead of using getWsUrl which adds an extra 'chat' segment
      const port = '8002'; // Use the same port as in websocket_test.html
      const wsUrl = `ws://localhost:${port}/ws/chat/${channelId}/?token=${encodeURIComponent(token)}`;
      console.log('Connecting to WebSocket:', wsUrl);
      
      this.socket = new WebSocket(wsUrl);
      this.connectionStatus = 'connecting';
      this.isConnecting = true;

      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.connectionStatus = 'disconnected';
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    console.log('WebSocket connected successfully');
    this.connectionStatus = 'connected';
    this.reconnectAttempts = 0;
    this.isConnecting = false;
    
    // Set up heartbeat to keep connection alive
    this.startHeartbeat();
    
    // Let subscribers know we're connected
    this.emit('connected', { channelId: this.channelId });
  }

  /**
   * Handle WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      
      // Handle different message types
      switch (data.type) {
        case 'chat.message':
          this.emit('message', data);
          break;
        case 'typing.status':
          this.emit('typing', data);
          break;
        case 'user.join':
          this.emit('user_online', { userId: data.user_id, username: data.username });
          break;
        case 'user.leave':
          this.emit('user_offline', { userId: data.user_id, username: data.username });
          break;
        case 'message.read':
          this.emit('message_read', {
            messageId: data.message_id,
            userId: data.user_id,
            username: data.username,
            readAt: data.timestamp || new Date().toISOString(),
            channelId: data.channel_id
          });
          break;
        case 'message.reaction':
          this.emit('reaction', {
            messageId: data.message_id,
            userId: data.user_id,
            username: data.username,
            reaction: data.reaction,
            action: data.action, // 'add' or 'remove'
            timestamp: data.timestamp || new Date().toISOString(),
            channelId: data.channel_id
          });
          break;
        default:
          // For any other message types, just pass them through
          this.emit('message', data);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      this.emit('error', { error: 'Failed to parse message' });
    }
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(event: CloseEvent): void {
    console.log(`WebSocket disconnected. Code: ${event.code}, Reason: ${event.reason}`);
    this.connectionStatus = 'disconnected';
    this.stopHeartbeat();
    this.emit('disconnected', { code: event.code, reason: event.reason });
    
    // Only attempt to reconnect if it wasn't a clean close
    if (event.code !== 1000) {
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket error
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.emit('error', { error: 'WebSocket connection error' });
  }
  
  /**
   * Send a message to the current channel
   * @param content The message content to send
   * @returns Boolean indicating success
   */
  sendMessage(content: string): boolean {
    if (!this.socket || this.connectionStatus !== 'connected') {
      console.error('Cannot send message: WebSocket not connected');
      return false;
    }

    try {
      const message = {
        type: 'chat.message',
        content,
        timestamp: new Date().toISOString(), // Add explicit timestamp
        channel_id: this.channelId
      };

      this.socket.send(JSON.stringify(message));
      console.log('WebSocket message sent:', message);
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  
  /**
   * Send a typing indicator through the WebSocket connection
   * @param isTyping Whether the user is typing (true) or has stopped (false)
   * @returns boolean indicating if indicator was sent
   */
  sendTypingIndicator(isTyping: boolean): boolean {
    if (!this.socket || this.connectionStatus !== 'connected') {
      console.error('Cannot send typing indicator: WebSocket not connected');
      return false;
    }

    try {
      const message = {
        type: 'typing.status',
        content: isTyping ? 'typing' : 'stopped_typing',
        timestamp: new Date().toISOString(),
        channel_id: this.channelId
      };

      this.socket.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Error sending typing indicator:', error);
      return false;
    }
  }

  /**
   * Send a message read receipt through the WebSocket connection
   * @param messageId The ID of the message that was read
   * @param userId The ID of the user who read the message
   * @param channelId The channel ID where the message is located
   * @returns boolean indicating if the receipt was sent
   */
  sendReadReceipt(messageId: string | number, userId: string | number, channelId?: string | number): boolean {
    if (!this.socket || this.connectionStatus !== 'connected') {
      console.error('Cannot send read receipt: WebSocket not connected');
      return false;
    }

    try {
      const message = {
        type: 'message.read',
        message_id: messageId,
        user_id: userId,
        channel_id: channelId || this.channelId,
        timestamp: new Date().toISOString()
      };

      this.socket.send(JSON.stringify(message));
      console.log('WebSocket read receipt sent:', message);
      return true;
    } catch (error) {
      console.error('Error sending read receipt:', error);
      return false;
    }
  }

  /**
   * Send a message reaction through the WebSocket connection
   * @param messageId The ID of the message to react to
   * @param userId The ID of the user adding the reaction
   * @param reaction The reaction emoji/code
   * @param action Whether to 'add' or 'remove' the reaction
   * @param channelId The channel ID where the message is located
   * @returns boolean indicating if the reaction was sent
   */
  sendReaction(messageId: string | number, userId: string | number, reaction: string, action: 'add' | 'remove', channelId?: string | number): boolean {
    if (!this.socket || this.connectionStatus !== 'connected') {
      console.error('Cannot send reaction: WebSocket not connected');
      return false;
    }

    try {
      const message = {
        type: 'message.reaction',
        message_id: messageId,
        user_id: userId,
        reaction: reaction,
        action: action,
        channel_id: channelId || this.channelId,
        timestamp: new Date().toISOString()
      };

      this.socket.send(JSON.stringify(message));
      console.log('WebSocket reaction sent:', message);
      return true;
    } catch (error) {
      console.error('Error sending reaction:', error);
      return false;
    }
  }

  /**
   * Start heartbeat to keep the connection alive
   */
  private startHeartbeat(): void {
    this.stopHeartbeat(); // Clear any existing interval
    
    this.heartbeatInterval = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  /**
   * Stop the heartbeat interval
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    this.stopHeartbeat();
    
    if (this.socket) {
      // Only try to close if it's not already closing or closed
      if (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING) {
        this.socket.close(1000, 'Client disconnected');
      }
      this.socket = null;
      this.channelId = null;
      this.connectionStatus = 'disconnected';
    }
  }

  /**
   * Get the connection status
   */
  getStatus(): 'connecting' | 'connected' | 'disconnected' {
    return this.connectionStatus;
  }

  /**
   * Check if connected to a specific channel
   */
  isConnectedTo(channelId: string | number): boolean {
    return this.connectionStatus === 'connected' && 
           this.channelId !== null && 
           String(this.channelId) === String(channelId);
  }
  
  /**
   * Send a typing indicator
   * @param isTyping Whether the user is typing
   */
  sendTyping(isTyping: boolean): void {
    this.sendTypingIndicator(isTyping);
  }
  
  /**
   * Subscribe to WebSocket events
   */
  on(event: WebSocketEvent, callback: WebSocketCallback): () => void {
    if (!this.eventCallbacks.has(event)) {
      this.eventCallbacks.set(event, []);
    }
    const callbacks = this.eventCallbacks.get(event)!;
    callbacks.push(callback);

    // Return unsubscribe function
    return () => {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    };
  }

  /**
   * Emit an event to all subscribers
   */
  private emit(event: WebSocketEvent, data: any): void {
    const callbacks = this.eventCallbacks.get(event) || [];
    callbacks.forEach((callback) => callback(data));
  }

  /**
   * Attempt to reconnect to the WebSocket server
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts || !this.channelId) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    setTimeout(() => {
      if (this.channelId) {
        this.connect(this.channelId);
      }
    }, this.reconnectDelay * this.reconnectAttempts);
  }
}

export const webSocketService = new WebSocketService();
