# Bot Manager API Documentation

## 🎯 Overview

The Bot Manager is a RESTful API service for managing Telegram bots. It provides endpoints for bot CRUD operations, status tracking, run management, and service integration.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ installed

### Running the Service

```bash
# Clone the repository
git clone <repository-url>
cd bot-manager

# Build and run with Docker Compose
docker-compose up -d --build

# Or run directly with Python
pip install -r requirements.txt
python3 app.py
```

The service will be available at `http://localhost:5002`

## 📡 API Endpoints

### Base URL

```
http://localhost:5002
```

### Authentication

No authentication required. All endpoints are publicly accessible.

### Response Format

All responses use JSON format:

```json
{
  "key": "value",
  "data": {...}
}
```

Error responses:

```json
{
  "error": "Error description"
}
```

## 🤖 Bot Management

### List All Bots

```http
GET /api/bots
```

**Response:**

```json
{
  "bots": [
    {
      "id": "bot-uuid",
      "config": {...},
      "status": "idle|running|error",
      "created_at": "2026-02-11T15:08:47",
      "last_run": "2026-02-11T14:30:00",
      "total_posts": 5,
      "error_message": null
    }
  ]
}
```

### Create New Bot

```http
POST /api/bots
Content-Type: application/json
```

**Request Body:**

```json
{
  "name": "My Bot",
  "city_name": "New York",
  "country_code": "US",
  "bot_token": "123456:ABC-DEF123456",
  "telegram_chat_id": "-1001234567890",
  "news_language": "en",
  "post_interval_minutes": 30,
  "max_posts_per_run": 5,
  "is_active": true
}
```

**Response:**

```json
{
  "id": "new-bot-uuid",
  "config": {...},
  "created_at": "2026-02-11T15:08:47",
  "status": "idle",
  "total_posts": 0,
  "error_message": null
}
```

### Get Bot Details

```http
GET /api/bots/{bot_id}
```

**Response:**

```json
{
  "id": "bot-uuid",
  "config": {...},
  "status": "idle|running|error",
  "created_at": "2026-02-11T15:08:47",
  "last_run": "2026-02-11T14:30:00",
  "total_posts": 5,
  "error_message": null
}
```

### Update Bot

```http
PUT /api/bots/{bot_id}
Content-Type: application/json
```

**Request Body:**

```json
{
  "name": "Updated Bot Name",
  "city_name": "Updated City",
  "country_code": "US",
  "bot_token": "123456:ABC-DEF123456",
  "telegram_chat_id": "-1001234567890",
  "news_language": "en",
  "post_interval_minutes": 60,
  "max_posts_per_run": 10,
  "is_active": false
}
```

**Response:**

```json
{
  "id": "bot-uuid",
  "config": {...},
  "status": "idle|running|error",
  "created_at": "2026-02-11T15:08:47",
  "last_run": "2026-02-11T14:30:00",
  "total_posts": 5,
  "error_message": null
}
```

### Delete Bot

```http
DELETE /api/bots/{bot_id}
```

**Response:**

```json
{
  "message": "Bot deleted successfully"
}
```

## 🏃 Bot Operations

### Trigger Bot Run

```http
POST /api/bots/{bot_id}/run
```

**Response:**

```json
{
  "message": "Bot run triggered",
  "bot_id": "bot-uuid",
  "config": {...}
}
```

### Get Bot Statistics

```http
GET /api/bots/{bot_id}/stats
```

**Response:**

```json
{
  "total_runs": 25,
  "successful_runs": 20,
  "success_rate": 0.8,
  "avg_duration": 3.2,
  "posts_per_run": 4.5,
  "recent_runs": [
    {
      "id": "run-uuid",
      "run_time": "2026-02-11T14:30:00",
      "processed": 5,
      "posted": 4,
      "duration": 3.8,
      "status": "success|error"
    }
  ]
}
```

### Get Bot Run History

```http
GET /api/bots/{bot_id}/runs
```

**Query Parameters:**

- `limit` (optional, default: 10) - Maximum number of runs to return

**Response:**

```json
[
  {
    "id": "run-uuid",
    "run_time": "2026-02-11T14:30:00",
    "processed": 5,
    "posted": 4,
    "duration": 3.8,
    "status": "success|error"
  }
]
```

### Update Bot Status

```http
PUT /api/bots/{bot_id}/status
```

**Request Body:**

```json
{
  "status": "running",
  "error_message": null
}
```

**Response:**

```json
{
  "message": "Status updated successfully"
}
```

## � Message Handling

### Send Message to Telegram

```http
POST /api/bots/{bot_id}/send_message
Content-Type: application/json
```

**Request Body:**

```json
{
  "message": "Hello, this is a test message!",
  "chat_id": "-1001234567890",
  "parse_mode": "Markdown"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Message sent successfully",
  "bot_id": "bot-uuid",
  "chat_id": "-1001234567890",
  "message_id": 12345,
  "sent_at": "2026-02-11T15:22:33.644126"
}
```

### Handle Incoming Telegram Messages (Webhook)

```http
POST /api/bots/{bot_id}/webhook
Content-Type: application/json
```

**Request Body (Telegram Update):**

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 123,
    "from": {
      "id": 987654321,
      "is_bot": false,
      "first_name": "John",
      "username": "john_doe"
    },
    "chat": {
      "id": -1001234567890,
      "title": "Test Group",
      "type": "supergroup"
    },
    "date": 1644567890,
    "text": "/start"
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Webhook processed successfully",
  "bot_id": "bot-uuid",
  "chat_id": -1001234567890
}
```

### Set Telegram Webhook

```http
POST /api/bots/{bot_id}/set_webhook
Content-Type: application/json
```

**Request Body:**

```json
{
  "webhook_url": "https://your-domain.com/api/bots/{bot_id}/webhook"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Webhook set successfully",
  "bot_id": "bot-uuid",
  "webhook_url": "https://your-domain.com/api/bots/{bot_id}/webhook"
}
```

## � Service Management

### List Registered Services

```http
GET /api/services
```

**Response:**

```json
{
  "services": [
    {
      "id": "service-uuid",
      "name": "News Feed Service",
      "url": "http://news-service:8000",
      "status": "active",
      "last_ping": "2026-02-11T14:30:00",
      "created_at": "2026-02-11T15:08:47"
    }
  ]
}
```

### Register New Service

```http
POST /api/services
Content-Type: application/json
```

**Request Body:**

```json
{
  "name": "My News Service",
  "url": "http://my-service:8000",
  "description": "Custom news processing service"
}
```

**Response:**

```json
{
  "id": "new-service-uuid",
  "name": "My News Service",
  "url": "http://my-service:8000",
  "description": "Custom news processing service",
  "created_at": "2026-02-11T15:08:47",
  "status": "active"
}
```

### Update Service Ping

```http
POST /api/services/{service_id}/ping
```

**Request Body:**

```json
{
  "status": "active"
}
```

**Response:**

```json
{
  "message": "Service ping updated"
}
```

## 🔍 System

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T15:08:47",
  "service": "bot-manager",
  "version": "1.0.0"
}
```

### Dashboard Statistics

```http
GET /api/dashboard
```

**Response:**

```json
{
  "total_bots": 5,
  "active_bots": 3,
  "total_runs": 150,
  "successful_runs": 120,
  "avg_success_rate": 0.8
  "services_count": 2
}
```

## 📝 Error Codes

| Status Code | Description           |
| ----------- | --------------------- |
| 200         | Success               |
| 201         | Created               |
| 400         | Bad Request           |
| 404         | Not Found             |
| 500         | Internal Server Error |

## 🔨 Data Models

### Bot Configuration

```json
{
  "id": "uuid",
  "name": "string",
  "city_name": "string",
  "country_code": "string",
  "bot_token": "string",
  "telegram_chat_id": "string",
  "news_language": "string",
  "post_interval_minutes": "integer",
  "max_posts_per_run": "integer",
  "is_active": "boolean",
  "openai_api_key": "string|null",
  "google_translate_api_key": "string|null",
  "newsapi_key": "string|null"
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Bot Status

- `idle` - Bot is not currently running
- `running` - Bot is currently processing
- `error` - Bot encountered an error

### Run Status

- `success` - Run completed successfully
- `error` - Run failed with errors

## 🚨 Usage Examples

### Python Client

```python
import requests

# Create a bot
response = requests.post('http://localhost:5002/api/bots', json={
    'name': 'My Bot',
    'city_name': 'New York',
    'bot_token': '123456:ABC-DEF123456',
    'telegram_chat_id': '-1001234567890'
})

bot = response.json()
print(f"Created bot with ID: {bot['id']}")
```

### JavaScript Client

```javascript
// Create a bot
const response = await fetch("http://localhost:5002/api/bots", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    name: "My Bot",
    city_name: "New York",
    bot_token: "123456:ABC-DEF123456",
    telegram_chat_id: "-1001234567890",
  }),
});

const bot = await response.json();
console.log(`Created bot with ID: ${bot.id}`);
```

### cURL Examples

```bash
# List all bots
curl -X GET http://localhost:5002/api/bots

# Create a new bot
curl -X POST http://localhost:5002/api/bots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Bot",
    "city_name": "New York",
    "bot_token": "123456:ABC-DEF123456",
    "telegram_chat_id": "-1001234567890"
  }'

# Trigger a bot run
curl -X POST http://localhost:5002/api/bots/{bot-id}/run

# Get bot statistics
curl -X GET http://localhost:5002/api/bots/{bot-id}/stats

# Send a message to Telegram
curl -X POST http://localhost:5002/api/bots/{bot-id}/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from Bot Manager API!",
    "chat_id": "-1001234567890"
  }'

# Set webhook for Telegram bot
curl -X POST http://localhost:5002/api/bots/{bot-id}/set_webhook \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://your-domain.com/api/bots/{bot-id}/webhook"
  }'
```

## 🔐 Security Notes

- All endpoints are publicly accessible
- No authentication required
- Use HTTPS in production
- Validate and sanitize all input data
- Rate limiting may be implemented for production use
- Store sensitive data (tokens, API keys) securely

## 📚 Additional Resources

- **Project Documentation**: `project.md` - Detailed project overview
- **API Documentation**: This file - Complete endpoint reference
- **Database Schema**: Defined in `models.py`
- **Configuration**: Environment variables in `app.py`

For more information, visit the project repository or contact the development team.
