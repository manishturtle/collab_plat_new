# WebSocket and Redis Architecture Documentation


### 4. Real-time Monitoring Commands

```bash
# Monitor all Redis commands in real-time
redis-cli monitor


#### Basic Redis CLI
```bash
# Connect to Redis
redis-cli

# Test connection
PING  # Should return "PONG"

# Get detailed server information
INFO

# Monitor all commands in real-time
MONITOR



### 2. Web-Based Interfaces

#### Option 1: Redis Commander
A lightweight web-based management tool.

```bash
# Install globally
npm install -g redis-commander

# Start Redis Commander
redis-commander

## System Overview

The collaborative platform implements a real-time messaging system using Django Channels with Redis as the backing store. This document outlines the current implementation, architecture, and key components of the WebSocket and Redis infrastructure.

## Architecture Components

### 1. Multi-Tenant Architecture

The system is built on a schema-per-tenant PostgreSQL architecture, where:

- Each tenant has a dedicated database schema
- Authentication is JWT-based with tenant context embedded in tokens
- WebSocket connections maintain tenant context throughout the connection lifecycle

### 2. Key Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | Django 4.2 | Core application framework |
| API | Django REST Framework | RESTful API endpoints |
| WebSockets | Django Channels | Real-time bidirectional communication |
| Channel Layer | Redis | Message broker & pub/sub system |
| Task Queue | Celery with Redis | Asynchronous task processing |
| Authentication | JWT (SimpleJWT) | Secure authentication with tenant context |

### 3. Server Infrastructure

- **Daphne**: ASGI server that handles both HTTP and WebSocket protocols
- **Redis**: Runs as a separate service for message distribution
- **PostgreSQL**: Multi-tenant database with schema isolation

## WebSocket Implementation

### Connection Flow

1. **Connection Initialization**:
   - Client attempts WebSocket connection with JWT token in query parameters
   - Connection is routed through `WebSocketJWTMiddleware`
   - Token is validated, tenant is identified, and connection context is set
   - If validation fails, connection is closed with error code 4000

2. **Channel Assignment**:
   - Upon successful authentication, user is assigned to a specific chat channel
   - Channel group subscriptions are managed using Redis
   - Connection is established and initial channel data is sent to the client

3. **Disconnection Handling**:
   - Clean disconnections are tracked and user presence is updated
   - Group memberships are removed from Redis
   - Resources are properly cleaned up

### Message Flow

1. **Client to Server**:
   - Client sends JSON message with defined type and payload
   - Message is received by consumer's `receive_json` method
   - Message is validated and routed to appropriate handler method

2. **Message Processing**:
   - Messages are persisted to the PostgreSQL database
   - Message read status is tracked for each user
   - Messages are formatted through serializers for consistent output

3. **Server to Clients**:
   - Messages are broadcast to all subscribed clients via Redis channel layer
   - Special handling exists for typing indicators and presence updates
   - Error responses provide feedback on message processing failures

## Redis Implementation

### Current Redis Functionality

In the current implementation, Redis is primarily used as a Django Channels backing store with the following active functionality:

1. **Channel Group Management**: 
   - Redis stores which channel names (WebSocket connections) belong to which groups
   - This enables real-time communication between multiple clients connected to the same chat channel
   - When a client disconnects, their channel is automatically removed from the groups

2. **Message Routing**:
   - Redis temporarily stores and routes messages to the appropriate consumers
   - Handles fan-out of messages to all clients subscribed to a particular chat channel
   - The actual message content is kept briefly in Redis during the distribution process

### Redis Operations Currently Used

1. **Group Operations** - Actively used:
   ```python
   # When a user connects to a channel
   await self.channel_layer.group_add(
       self.room_group_name,  # e.g. "chat_fba1f391-1919-4cec-86e1-7f2c6671a0cc"
       self.channel_name      # Auto-generated unique channel name
   )
   
   # When a user disconnects
   await self.channel_layer.group_discard(
       self.room_group_name,
       self.channel_name
   )
   ```

2. **Broadcasting Messages** - Actively used:
   ```python
   # Broadcasting a message to all clients in the channel
   await self.channel_layer.group_send(
       self.room_group_name,
       {
           "type": "chat.message",  # Event handler method name
           "message": serialized_message_data
       }
   )
   ```

### Redis Data Structures in Use

| Structure Type | Current Usage | Example Keys |
|---------------|---------|------------|
| Sets | Stores channel group membership | `asgi:group:chat_fba1f391-1919-4cec-86e1-7f2c6671a0cc` |
| Hashes | Temporary message payload storage | `asgi:message:abcdef123456` |

### Redis Configuration

The Redis connection is configured in `settings.py` with the following settings:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}
```

### Features Not Yet Implemented

These Redis-based features are not currently implemented but planned for future development:

1. **Presence Management**: User online status tracking
2. **Typing Indicators**: Persistent typing status with TTL
3. **Message Read Status**: Real-time read receipt synchronization
4. **Caching**: Caching of frequently accessed channel and message data

## Authentication and Security

### JWT Authentication Flow

1. User logs in through REST API and receives JWT token pair (access + refresh tokens)
2. Access token includes user ID, tenant ID, and schema name
3. WebSocket connections include token in the URL query parameter
4. `WebSocketJWTMiddleware` validates token and establishes tenant context
5. Failed authentication results in connection rejection with error code 4000

### Security Measures

- **Tenant Isolation**: Each WebSocket connection operates within its tenant context
- **Per-Channel Authorization**: Users can only access channels they are members of
- **Token Expiration**: JWT tokens have enforced expiration times
- **Secure Error Handling**: Limited error information exposed to clients

## Current Message Types

| Message Type | Direction | Purpose |
|-------------|-----------|---------|
| `chat.message` | Bidirectional | Send/receive text messages |
| `typing` | Bidirectional | Indicate when a user is typing |
| `message.read` | Bidirectional | Mark messages as read |
| `user.join` | Server → Client | Notify when a user joins a channel |
| `user.leave` | Server → Client | Notify when a user leaves a channel |

## Data Models

### Key Models

1. **ChatChannel**:
   - Represents a conversation channel
   - Has multiple participants
   - Contains messages

2. **ChatMessage**:
   - Individual messages within a channel
   - Linked to sender and channel
   - Tracks read status

3. **MessageReadStatus**:
   - Tracks which users have read which messages
   - Many-to-many relationship between users and messages

## Serializers

Serializers handle data transformation for WebSocket messages:

1. **UserStatusSerializer**: User presence and profile information
2. **ChatChannelSerializer**: Channel details including participants and unread counts
3. **ChatMessageSerializer**: Message content, sender info, and read status
4. **MessageReadStatusSerializer**: Message read receipt information

## Future Considerations

1. **Scaling**: 
   - Redis Cluster for horizontal scaling
   - Multiple Daphne instances behind load balancer

2. **Performance Optimizations**:
   - Message pagination
   - Rate limiting
   - Connection pooling

3. **Enhanced Features**:
   - End-to-end encryption
   - Media file sharing
   - Message reactions

## Troubleshooting

Common issues and their resolution:

1. **Connection failures**:
   - Check JWT token validity
   - Verify Redis is running
   - Confirm channel routing is correct

2. **Message delivery failures**:
   - Check Redis connection
   - Verify group membership
   - Ensure correct message format

3. **Performance issues**:
   - Monitor Redis memory usage
   - Check database query performance
   - Analyze websocket connection count
