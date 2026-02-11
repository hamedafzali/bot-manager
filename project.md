# Bot Manager Service

Centralized bot configuration and management microservice. Handles bot CRUD operations, status tracking, and service registration.

## 🎯 Project Overview

Centralized bot configuration and management microservice. Handles bot CRUD operations, status tracking, and service registration.

## 🏗️ Architecture

- **Type**: REST API Microservice
- **Port**: 5002
- **Database**: SQLite (bot_manager.db)
- **Framework**: Flask

## 📁 Project Structure

```
bot-manager/
├── project.md          # This file
├── requirements.txt    # Python dependencies
├── app.py             # Main Flask application
├── models.py          # Data models (Bot, BotRun, etc.)
├── manager.py         # Core business logic
├── Dockerfile         # Container configuration
└── templates/         # HTML templates
    ├── bot_details.html
    ├── edit_bot.html
    └── dashboard.html
```

## 🚀 Quick Start

```bash
cd bot-manager
pip install -r requirements.txt
python3 app.py
```

Service starts on http://localhost:5002

## 📡 API Endpoints

### Bot Management

- `GET /api/bots` - List all bots
- `POST /api/bots` - Create new bot
- `GET /api/bots/{id}` - Get specific bot
- `PUT /api/bots/{id}` - Update bot
- `DELETE /api/bots/{id}` - Delete bot

### Bot Operations

- `POST /api/bots/{id}/run` - Trigger bot run
- `GET /api/bots/{id}/stats` - Get bot statistics
- `GET /api/bots/{id}/runs` - Get bot run history
- `PUT /api/bots/{id}/status` - Update bot status

### Service Management

- `GET /api/services` - List registered services
- `POST /api/services` - Register new service
- `POST /api/services/{id}/ping` - Update service ping

### System

- `GET /health` - Service health check
- `GET /api/dashboard` - Dashboard statistics

## � Documentation

- **API Documentation**: `README.md` - Complete endpoint reference
- **Project Documentation**: `project.md` - Detailed project overview
- **Database Schema**: Defined in `models.py`
- **Configuration**: Environment variables in `app.py`

## �🔧 Configuration

Environment Variables:

- `BOT_MANAGER_DB_PATH` - Database file path (default: bot_manager.db)
- `BOT_MANAGER_PORT` - Service port (default: 5002)
- `SECRET_KEY` - Flask secret key

## 📊 Database Schema

SQLite database with tables:

- `bots` - Bot configurations and metadata
- `bot_runs` - Run history and performance data
- `services` - Registered external services

## 🐳 Docker Deployment

```bash
docker build -t bot-manager .
docker run -p 5002:5002 -v $(pwd)/data:/app/data bot-manager
```

## 🔄 External Dependencies

- **News Feed Service** - Registers for bot processing
- **Bot UI Service** - Consumes bot management APIs

## 📈 Key Features

- ✅ Bot CRUD operations
- ✅ Status tracking and monitoring
- ✅ Run history and statistics
- ✅ Service registration and discovery
- ✅ RESTful API design
- ✅ Health checks and monitoring

## 🎯 Responsibilities

1. **Bot Configuration Management** - Store and manage bot settings
2. **Status Tracking** - Monitor bot states and health
3. **Service Registry** - Register and track external services
4. **Run History** - Log all bot operations and results
5. **API Gateway** - Provide centralized API for bot operations

## 🔍 Monitoring

- Health check endpoint: `/health`
- Service registration tracking
- Bot status monitoring
- Performance metrics collection

## 📝 Notes

- Stateless service design
- SQLite for simplicity (can be upgraded to PostgreSQL)
- Automatic service registration
- RESTful API following best practices

## 🎨 UI Features

- ✅ **Modern Bot Management Interface** - Clean, responsive design
- ✅ **Stylish Action Buttons** - Gradients, hover effects, animations
- ✅ **Real-time Status Updates** - Live bot status monitoring
- ✅ **Interactive Bot Controls** - Run, stop, test, edit, delete
- ✅ **Statistics Dashboard** - Performance metrics and run history
- ✅ **Service Integration** - External service registration and management

## 🚀 Recent Changes (Latest)

### ✅ **Clean Architecture Implementation** (Feb 11, 2026)

- **Removed all internal news processing** - No more mock data or workers
- **Pure bot management focus** - System now only manages bot configurations
- **External service integration** - Clean API endpoints for third-party services
- **Simplified codebase** - Removed complex news worker dependencies

### ✅ **Enhanced User Interface** (Feb 11, 2026)

- **Modern button styling** - Gradients, shadows, hover animations
- **Improved user experience** - Better visual feedback and interactions
- **Streamlined bot controls** - Test message, run, stop, edit, delete buttons

### ✅ **API Improvements** (Feb 11, 2026)

- **Added `/api/bots/{id}/send` endpoint** - For external news sending
- **Enhanced error handling** - Better JSON parsing and validation
- **Comprehensive bot management** - Full CRUD operations with status tracking

### ✅ **System Architecture** (Feb 11, 2026)

- **Microservice design** - Stateless, RESTful API structure
- **Database optimization** - Efficient SQLite schema with proper indexing
- **Container-based deployment** - Docker for consistent environments
- **Health monitoring** - Comprehensive service health checks

## 🎯 Current Status

- **State**: Production Ready
- **Core Features**: Bot management, status tracking, external service integration
- **UI**: Modern, responsive interface with stylish controls
- **API**: RESTful endpoints for all operations
- **Deployment**: Docker containers with health monitoring

The bot manager is now a **clean, focused bot management system** ready for production use!
