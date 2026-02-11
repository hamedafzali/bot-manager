"""
Bot Manager Service - Main Application
"""
import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from manager import BotManager
from models import BotConfig, BotStatus, RunStatus, BotRun

def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'bot-manager-secret-key')
    db_path = os.getenv('BOT_MANAGER_DB_PATH', 'bot_manager.db')
    
    manager = BotManager(db_path)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'bot-manager',
            'version': '1.0.0'
        })
    
    # Bot Management Endpoints
    @app.route('/api/bots', methods=['GET'])
    def list_bots():
        """List all bots"""
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        bots = manager.list_bots(active_only=active_only)
        return jsonify([bot.to_dict() for bot in bots])
    
    @app.route('/api/bots', methods=['POST'])
    def create_bot():
        """Create a new bot"""
        data = request.get_json()
        
        try:
            config = BotConfig(
                name=data['name'],
                city_name=data['city_name'],
                country_code=data['country_code'],
                bot_token=data['bot_token'],
                telegram_chat_id=data['telegram_chat_id'],
                news_language=data.get('news_language', 'en'),
                post_interval_minutes=data.get('post_interval_minutes', 30),
                max_posts_per_run=data.get('max_posts_per_run', 5),
                openai_api_key=data.get('openai_api_key'),
                google_translate_api_key=data.get('google_translate_api_key'),
                newsapi_key=data.get('newsapi_key'),
                is_active=data.get('is_active', True)
            )
            
            bot = manager.create_bot(config)
            
            return jsonify(bot.to_dict()), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/bots/<bot_id>', methods=['GET'])
    def get_bot(bot_id):
        """Get a specific bot"""
        bot = manager.get_bot(bot_id)
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        return jsonify(bot.to_dict())
    
    @app.route('/api/bots/<bot_id>', methods=['PUT'])
    def update_bot(bot_id):
        """Update a bot"""
        data = request.get_json()
        
        try:
            config = BotConfig(
                name=data['name'],
                city_name=data['city_name'],
                country_code=data['country_code'],
                bot_token=data['bot_token'],
                telegram_chat_id=data['telegram_chat_id'],
                news_language=data.get('news_language', 'en'),
                post_interval_minutes=data.get('post_interval_minutes', 30),
                max_posts_per_run=data.get('max_posts_per_run', 5),
                openai_api_key=data.get('openai_api_key'),
                google_translate_api_key=data.get('google_translate_api_key'),
                newsapi_key=data.get('newsapi_key'),
                is_active=data.get('is_active', True)
            )
            
            success = manager.update_bot(bot_id, config)
            if not success:
                return jsonify({'error': 'Bot not found'}), 404
            
            bot = manager.get_bot(bot_id)
            return jsonify(bot.to_dict())
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/bots/<bot_id>', methods=['DELETE'])
    def delete_bot(bot_id):
        """Delete a bot"""
        success = manager.delete_bot(bot_id)
        if not success:
            return jsonify({'error': 'Bot not found'}), 404
        return jsonify({'message': 'Bot deleted successfully'})
    
    @app.route('/api/bots/<bot_id>/status', methods=['PUT'])
    def update_bot_status(bot_id):
        """Update bot status"""
        data = request.get_json()
        
        try:
            status = BotStatus(data['status'])
            error_message = data.get('error_message')
            
            success = manager.update_bot_status(bot_id, status, error_message)
            if not success:
                return jsonify({'error': 'Bot not found'}), 404
            
            return jsonify({'message': 'Status updated successfully'})
            
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
        
    @app.route('/api/bots/<bot_id>/run', methods=['POST'])
    def trigger_bot_run(bot_id):
        """Trigger a bot run (for external services)"""
        bot = manager.get_bot(bot_id)
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # This would typically trigger an external service
        # For now, just update status
        manager.update_bot_status(bot_id, BotStatus.RUNNING)
        
        return jsonify({
            'message': 'Bot run triggered',
            'bot_id': bot_id,
            'config': bot.config.to_dict()
        })
    
    @app.route('/api/bots/<bot_id>/webhook', methods=['POST'])
    def telegram_webhook(bot_id):
        """Handle incoming Telegram messages via webhook"""
        bot = manager.get_bot(bot_id)
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        try:
            # Get incoming message from Telegram
            update = request.get_json()
            if not update:
                return jsonify({'error': 'No update data received'}), 400
            
            # Extract message information
            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
            user_info = message.get('from', {})
            
            if not chat_id or not text:
                return jsonify({'error': 'Invalid message format'}), 400
            
            # Log the incoming message
            app.logger.info(f"📨 Received message from Telegram for bot {bot_id}: {text}")
            
            # Process the message and get response
            response_text = process_incoming_message(bot, text, user_info)
            
            # Send response back to user if needed
            if response_text:
                try:
                    telegram_url = f"https://api.telegram.org/bot{bot.config.bot_token}/sendMessage"
                    telegram_data = {
                        'chat_id': chat_id,
                        'text': response_text,
                        'parse_mode': 'Markdown'
                    }
                    
                    response = requests.post(telegram_url, json=telegram_data, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('ok'):
                            app.logger.info(f"✅ Response sent to user: {response_text}")
                        else:
                            app.logger.error(f"❌ Failed to send response: {result.get('description')}")
                    else:
                        app.logger.error(f"❌ HTTP error sending response: {response.status_code}")
                except Exception as e:
                    app.logger.error(f"❌ Error sending response: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Webhook processed successfully',
                'bot_id': bot_id,
                'chat_id': chat_id
            })
            
        except Exception as e:
            app.logger.error(f"❌ Error processing webhook: {e}")
            return jsonify({'error': 'Failed to process webhook'}), 500
    
    def process_incoming_message(bot, text, user_info):
        """Process incoming message and return response if needed"""
        text_lower = text.lower()
        
        # Basic command handling
        if text_lower == '/start':
            return f"🤖 Welcome to {bot.config.name}!\n\nI'm ready to assist you. Type /help for available commands."
        
        elif text_lower == '/help':
            return """📋 Available Commands:
/start - Start the bot
/help - Show this help message
/status - Check bot status
/info - Get bot information"""
        
        elif text_lower == '/status':
            return f"📊 Bot Status: {bot.status}\n📍 City: {bot.config.city_name}\n🌐 Language: {bot.config.news_language}"
        
        elif text_lower == '/info':
            return f"ℹ️ Bot Information:\n🤖 Name: {bot.config.name}\n📍 City: {bot.config.city_name}\n🌐 Country: {bot.config.country_code}\n⏰ Interval: {bot.config.post_interval_minutes} minutes"
        
        elif text_lower.startswith('/'):
            return "❓ Unknown command. Type /help for available commands."
        
        # Handle regular messages
        elif text_lower == 'hello' or text_lower == 'hi':
            return f"👋 Hello! I'm {bot.config.name}. How can I help you today?"
        
        # For other messages, you can implement custom logic
        else:
            return None  # Don't respond to every message
    
    @app.route('/api/bots/<bot_id>/send_message', methods=['POST'])
    def send_message_to_telegram(bot_id):
        """Send a message to Telegram via bot"""
        bot = manager.get_bot(bot_id)
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No message data provided'}), 400
            
            message = data.get('message')
            parse_mode = data.get('parse_mode', 'Markdown')
            
            # Use bot's default chat ID, allow override if explicitly provided
            chat_id = data.get('chat_id') if data.get('chat_id') else bot.config.telegram_chat_id
            
            if not message:
                return jsonify({'error': 'Message content is required'}), 400
            
            if not chat_id:
                return jsonify({'error': 'Chat ID is required (not configured in bot)'}), 400
            
            # Send message to Telegram
            telegram_url = f"https://api.telegram.org/bot{bot.config.bot_token}/sendMessage"
            telegram_data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(telegram_url, json=telegram_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    message_id = result.get('result', {}).get('message_id')
                    app.logger.info(f"✅ Message sent successfully via bot {bot_id} (ID: {message_id})")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Message sent successfully',
                        'bot_id': bot_id,
                        'chat_id': chat_id,
                        'message_id': message_id,
                        'sent_at': datetime.utcnow().isoformat()
                    })
                else:
                    error_msg = result.get('description', 'Unknown error')
                    app.logger.error(f"❌ Telegram API error: {error_msg}")
                    return jsonify({'error': f'Telegram API error: {error_msg}'}), 400
            else:
                app.logger.error(f"❌ HTTP error sending message: {response.status_code}")
                return jsonify({'error': f'HTTP error: {response.status_code}'}), 500
                
        except Exception as e:
            app.logger.error(f"❌ Error sending message: {e}")
            return jsonify({'error': 'Failed to send message'}), 500
    
    @app.route('/api/bots/<bot_id>/set_webhook', methods=['POST'])
    def set_telegram_webhook(bot_id):
        """Set webhook for Telegram bot"""
        bot = manager.get_bot(bot_id)
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        try:
            data = request.get_json() or {}
            webhook_url = data.get('webhook_url')
            
            if not webhook_url:
                # Use default webhook URL
                webhook_url = f"http://localhost:5002/api/bots/{bot_id}/webhook"
            
            # Set webhook via Telegram API
            telegram_url = f"https://api.telegram.org/bot{bot.config.bot_token}/setWebhook"
            telegram_data = {
                'url': webhook_url,
                'allowed_updates': ['message', 'callback_query']
            }
            
            response = requests.post(telegram_url, json=telegram_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    app.logger.info(f"✅ Webhook set for bot {bot_id}: {webhook_url}")
                    return jsonify({
                        'success': True,
                        'message': 'Webhook set successfully',
                        'bot_id': bot_id,
                        'webhook_url': webhook_url
                    })
                else:
                    error_msg = result.get('description', 'Unknown error')
                    app.logger.error(f"❌ Failed to set webhook: {error_msg}")
                    return jsonify({'error': f'Failed to set webhook: {error_msg}'}), 400
            else:
                app.logger.error(f"❌ HTTP error setting webhook: {response.status_code}")
                return jsonify({'error': f'HTTP error: {response.status_code}'}), 500
                
        except Exception as e:
            app.logger.error(f"❌ Error setting webhook: {e}")
            return jsonify({'error': 'Failed to set webhook'}), 500
    
    @app.route('/api/bots/<bot_id>/stats', methods=['GET'])
    def get_bot_stats(bot_id):
        """Get bot statistics"""
        bot = manager.get_bot(bot_id)
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        runs = manager.get_bot_runs(bot_id, limit=50)
        total_runs = len(runs)
        successful_runs = len([r for r in runs if r.status == RunStatus.SUCCESS])
        avg_duration = sum(r.duration for r in runs) / total_runs if total_runs > 0 else 0
        
        return jsonify({
            'bot_id': bot_id,
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'success_rate': successful_runs / total_runs if total_runs > 0 else 0,
            'avg_duration': avg_duration,
            'total_posts': bot.total_posts,
            'recent_runs': [run.to_dict() for run in runs[:10]]
        })
    
    @app.route('/api/bots/<bot_id>/runs', methods=['GET'])
    def get_bot_runs(bot_id):
        """Get bot run history"""
        limit = request.args.get('limit', 10, type=int)
        runs = manager.get_bot_runs(bot_id, limit=limit)
        return jsonify([run.to_dict() for run in runs])
    
    @app.route('/api/bots/<bot_id>/runs', methods=['POST'])
    def record_bot_run(bot_id):
        """Record a bot run result"""
        data = request.get_json()
        
        try:
            import uuid
            
            run = BotRun(
                id=str(uuid.uuid4()),
                bot_id=bot_id,
                run_time=datetime.fromisoformat(data.get('run_time', datetime.utcnow().isoformat())),
                processed=data.get('processed', 0),
                posted=data.get('posted', 0),
                duration=data.get('duration', 0.0),
                status=RunStatus(data.get('status', 'success')),
                error_message=data.get('error_message'),
                metadata=data.get('metadata')
            )
            
            success = manager.record_bot_run(run)
            if not success:
                return jsonify({'error': 'Failed to record run'}), 500
            
            return jsonify(run.to_dict()), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    # Service Management Endpoints
    @app.route('/api/services', methods=['GET'])
    def list_services():
        """List registered services"""
        service_type = request.args.get('type')
        services = manager.get_services(service_type)
        return jsonify(services)
    
    @app.route('/api/services', methods=['POST'])
    def register_service():
        """Register a new service"""
        data = request.get_json()
        
        try:
            success = manager.register_service(
                service_id=data['id'],
                name=data['name'],
                service_type=data['service_type'],
                endpoint_url=data['endpoint_url'],
                api_key=data.get('api_key')
            )
            
            if not success:
                return jsonify({'error': 'Failed to register service'}), 500
            
            return jsonify({'message': 'Service registered successfully'}), 201
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/services/<service_id>/ping', methods=['POST'])
    def ping_service(service_id):
        """Update service ping time"""
        success = manager.update_service_ping(service_id)
        if not success:
            return jsonify({'error': 'Service not found'}), 404
        return jsonify({'message': 'Ping updated'})
    
    @app.route('/api/services/<service_id>', methods=['DELETE'])
    def delete_service(service_id):
        """Delete a service"""
        success = manager.delete_service(service_id)
        if not success:
            return jsonify({'error': 'Service not found'}), 404
        return jsonify({'message': 'Service deleted successfully'})
    
    # Dashboard Endpoints
    @app.route('/api/dashboard', methods=['GET'])
    def dashboard_stats():
        """Get dashboard statistics"""
        bots = manager.list_bots()
        services = manager.get_services()
        
        total_bots = len(bots)
        active_bots = len([b for b in bots if b.config.is_active])
        total_posts = sum(b.total_posts for b in bots)
        cities = len(set(b.config.city_name for b in bots))
        
        return jsonify({
            'total_bots': total_bots,
            'active_bots': active_bots,
            'total_posts': total_posts,
            'cities_covered': cities,
            'registered_services': len(services),
            'bots': [bot.to_dict() for bot in bots[:10]]  # Recent 10 bots
        })
    
    return app

if __name__ == '__main__':
    port = int(os.getenv('BOT_MANAGER_PORT', 5002))
    app = create_app()
    print(f"🤖 Bot Manager Service starting on port {port}")
    print(f"📊 Database: {os.getenv('BOT_MANAGER_DB_PATH', 'bot_manager.db')}")
    app.run(debug=True, host='0.0.0.0', port=port)
