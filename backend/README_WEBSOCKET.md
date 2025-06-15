# WebSocket Chat Application

This document provides instructions for setting up and running the WebSocket-based chat application.

## Prerequisites

- Python 3.8+
- Redis server (for channel layer)
- PostgreSQL (for database)
- Node.js and npm (for frontend assets)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgres://user:password@localhost:5432/your_database
   REDIS_URL=redis://localhost:6379/0
   ```

## Running the Development Server

1. **Start Redis**
   ```bash
   # Using the management command
   python manage.py start_redis
   
   # Or start Redis manually
   # redis-server
   ```

2. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run the development server**
   ```bash
   # Using the custom __main__.py
   python -m . runserver
   
   # Or using manage.py directly
   # python manage.py runserver
   ```

5. **Access the application**
   - Web interface: http://localhost:8000/
   - Admin interface: http://localhost:8000/admin/

## WebSocket Endpoints

The following WebSocket endpoints are available:

- **Chat Messages**: `ws://localhost:8000/ws/chat/<channel_id>/?token=<jwt_token>`
- **User Presence**: `ws://localhost:8000/ws/presence/?token=<jwt_token>`
- **Typing Indicators**: `ws://localhost:8000/ws/typing/<channel_id>/?token=<jwt_token>`

## Testing

To run the test suite:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest

# Run tests with coverage
coverage run -m pytest
coverage report
```

## Production Deployment

For production deployment, consider the following:

1. Set `DEBUG=False` in your environment variables
2. Configure a production database (e.g., PostgreSQL on RDS)
3. Use a production-ready ASGI server like Daphne or Uvicorn
4. Set up a production Redis instance
5. Configure a reverse proxy (Nginx/Apache) with WebSocket support

Example with Daphne:
```bash
pip install daphne

# Run the ASGI application
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Troubleshooting

### WebSocket Connection Issues
- Ensure Redis is running and accessible
- Check the browser console for WebSocket connection errors
- Verify CORS settings if connecting from a different domain

### Authentication Issues
- Ensure the JWT token is valid and not expired
- Check that the token is included in the WebSocket URL
- Verify that the user exists and is active

### Performance Issues
- Monitor Redis memory usage
- Consider scaling the number of worker processes
- Use a connection pool for database connections

## License

[Your License Here]
