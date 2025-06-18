# Chat Application API and WebSocket Documentation

## WebSocket Endpoints

### 1. Chat WebSocket
- **URL**: `ws/chat/<channel_id>/`
- **Consumer**: `ChatConsumer`
- **Purpose**: Handles real-time chat messages and presence for a specific channel
- **Events**:
  - `chat.message`: Send/receive chat messages
  - `typing`: Send/receive typing indicators
  - `message.read`: Notify when messages are read
  - `user.join`: Notify when users join a channel
  - `user.leave`: Notify when users leave a channel

### 2. Presence WebSocket
- **URL**: `ws/presence/`
- **Consumer**: `PresenceConsumer`
- **Purpose**: Tracks user online/offline status and status updates
- **Events**:
  - `presence.update`: Broadcast user online/offline status
  - `online.users`: List of currently online users
  - `status.update`: Update user status (e.g., away, busy)

### 3. Typing Indicator WebSocket
- **URL**: `ws/typing/<channel_id>/`
- **Consumer**: `TypingConsumer`
- **Purpose**: Handles typing indicators in real-time
- **Events**:
  - `typing`: Send/receive typing status updates

## REST API Endpoints

### Channels
- **GET** `/api/chat/<tenant_slug>/channels/` - List all channels for the current user
- **POST** `/api/chat/<tenant_slug>/channels/` - Create a new channel
- **GET** `/api/chat/<tenant_slug>/channels/<uuid:pk>/` - Get channel details
- **GET** `/api/chat/<tenant_slug>/channels/<uuid:pk>/messages/` - Get messages for a channel
- **POST** `/api/chat/<tenant_slug>/channels/<uuid:pk>/send_message/` - Send a message to a channel
- **POST** `/api/chat/<tenant_slug>/channels/<uuid:pk>/mark_read/` - Mark all messages as read
- **POST** `/api/chat/<tenant_slug>/channels/<uuid:pk>/centralized/` - Get centralized chat view

## Data Models

### 1. ChatChannel
- `id`: UUID (primary key)
- `channel_type`: Enum (direct, group, contextual_object)
- `name`: String (optional for direct messages)
- `host_application_id`: String (for contextual chats)
- `context_object_type`: String (for contextual chats)
- `context_object_id`: String (for contextual chats)
- `participants`: ManyToMany to User through ChannelParticipant

### 2. ChannelParticipant
- `user`: ForeignKey to User
- `channel`: ForeignKey to ChatChannel
- `role`: Enum (admin, member, guest)
- `user_type`: Enum (internal, guest)

### 3. ChatMessage
- `id`: BigAutoField (primary key)
- `channel`: ForeignKey to ChatChannel
- `user`: ForeignKey to User (sender)
- `content`: Text
- `content_type`: String (default: 'text/plain')
- `file_url`: URL (optional)
- `parent`: Self-referential ForeignKey (for replies)
- `read_by`: ManyToMany to User through MessageReadStatus

### 4. MessageReadStatus
- `message`: ForeignKey to ChatMessage
- `user`: ForeignKey to User
- `read_at`: DateTime

### 5. UserChannelState
- `user`: ForeignKey to User
- `channel`: ForeignKey to ChatChannel
- `last_read_message_id`: BigInt (foreign key to ChatMessage)
- `is_muted`: Boolean

## Key Features

1. **Multi-tenant Architecture**: Supports multiple organizations with schema-per-tenant
2. **Real-time Updates**: WebSocket-based real-time messaging and presence
3. **Message Read Receipts**: Track when messages are read
4. **Typing Indicators**: Show when users are typing
5. **Multiple Channel Types**:
   - Direct messages (1:1)
   - Group chats
   - Contextual chats (tied to specific objects/contexts)
6. **Centralized Chat View**: Unified view of all conversations
7. **Presence Management**: Track user online/offline status
8. **Message History**: Retrieve message history with pagination

## Authentication & Authorization

- Uses Django's authentication system
- WebSocket connections require authentication
- Users can only access channels they are participants in
- Role-based access control (admin/member/guest)

## Error Handling

- Comprehensive error handling in WebSocket consumers
- REST API returns appropriate HTTP status codes
- Detailed error messages with error codes

## Performance Considerations

- Uses database indexes for common query patterns
- Pagination for message history
- Efficient WebSocket group management
- Asynchronous processing for I/O operations
