"""
Bot Manager UI - Simple Web Interface
"""
import os
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'bot-manager-ui-secret'

BOT_MANAGER_URL = os.getenv('BOT_MANAGER_URL', 'http://bot-manager:5002')

@app.route('/')
def dashboard():
    """Main dashboard"""
    try:
        # Get bots
        response = requests.get(f"{BOT_MANAGER_URL}/api/bots")
        bots = response.json() if response.status_code == 200 else []
        
        # Get dashboard stats
        stats_response = requests.get(f"{BOT_MANAGER_URL}/api/dashboard")
        stats = stats_response.json() if stats_response.status_code == 200 else {}
        
        return render_template('dashboard.html', bots=bots, stats=stats)
    except Exception as e:
        flash(f'Error loading data: {e}', 'error')
        return render_template('dashboard.html', bots=[], stats={})

@app.route('/add_bot', methods=['GET', 'POST'])
def add_bot():
    """Add new bot"""
    if request.method == 'POST':
        # Get form data based on new template
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'city_name': 'Default',  # Required by API but not in new template
            'country_code': 'US',   # Required by API but not in new template
            'bot_token': request.form.get('telegram_bot_token'),
            'telegram_chat_id': request.form.get('telegram_chat_id'),
            'news_language': 'en',  # Default value
            'post_interval_minutes': 30,  # Default value
            'max_posts_per_run': 5,  # Default value
            'openai_api_key': None,
            'google_translate_api_key': None,
            'newsapi_key': None,
            'is_active': request.form.get('is_active') == 'on'
        }
        
        try:
            response = requests.post(f"{BOT_MANAGER_URL}/api/bots", json=data)
            if response.status_code == 201:
                flash('Bot created successfully! 🎉', 'success')
                return redirect(url_for('dashboard'))
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                flash(f'Error creating bot: {error_msg}', 'error')
        except Exception as e:
            flash(f'Error: {e}', 'error')
    
    return render_template('add_bot.html')

@app.route('/bot/<bot_id>')
def bot_details(bot_id):
    """Bot details page"""
    try:
        # Get bot details
        response = requests.get(f"{BOT_MANAGER_URL}/api/bots/{bot_id}")
        bot = response.json() if response.status_code == 200 else None
        
        # Get bot stats
        stats_response = requests.get(f"{BOT_MANAGER_URL}/api/bots/{bot_id}/stats")
        stats = stats_response.json() if stats_response.status_code == 200 else {}
        
        if not bot:
            flash('Bot not found', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('bot_details.html', bot=bot, stats=stats)
    except Exception as e:
        flash(f'Error loading bot: {e}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/bot/<bot_id>/edit', methods=['GET', 'POST'])
def edit_bot(bot_id):
    """Edit bot"""
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'city_name': 'Default',  # Required by API but not in new template
            'country_code': 'US',   # Required by API but not in new template
            'bot_token': request.form.get('telegram_bot_token'),  # Map new template field
            'telegram_chat_id': request.form.get('telegram_chat_id'),
            'news_language': 'en',  # Default value
            'post_interval_minutes': 30,  # Default value
            'max_posts_per_run': 5,  # Default value
            'openai_api_key': None,
            'google_translate_api_key': None,
            'newsapi_key': None,
            'is_active': request.form.get('is_active') == 'on'
        }
        
        try:
            response = requests.put(f"{BOT_MANAGER_URL}/api/bots/{bot_id}", json=data)
            if response.status_code == 200:
                flash('Bot updated successfully! ✅', 'success')
                return redirect(url_for('bot_details', bot_id=bot_id))
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                flash(f'Error updating bot: {error_msg}', 'error')
        except Exception as e:
            flash(f'Error: {e}', 'error')
    
    # GET request - load current bot data
    try:
        response = requests.get(f"{BOT_MANAGER_URL}/api/bots/{bot_id}")
        bot = response.json() if response.status_code == 200 else None
        
        if not bot:
            flash('Bot not found', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('edit_bot.html', bot=bot)
    except Exception as e:
        flash(f'Error loading bot: {e}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/bot/<bot_id>/test', methods=['POST'])
def test_bot(bot_id):
    """Test bot connection by sending a message"""
    try:
        # Get bot details
        response = requests.get(f"{BOT_MANAGER_URL}/api/bots/{bot_id}")
        bot = response.json() if response.status_code == 200 else None
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Test connection
        test_data = request.get_json()
        message = test_data.get('message', 'Test message from Bot Manager')
        
        # Create test message using bot's connection
        if bot['config'].get('bot_token') and bot['config'].get('telegram_chat_id'):
            # Test Telegram connection
            bot_token = bot['config']['bot_token']
            chat_id = bot['config']['telegram_chat_id']
            
            try:
                # Use Telegram Bot API directly
                telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                telegram_data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(telegram_url, json=telegram_data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        return jsonify({
                            'success': True,
                            'message': '✅ Test message sent successfully via Telegram',
                            'connection_type': 'telegram',
                            'message_id': result.get('result', {}).get('message_id')
                        })
                    else:
                        return jsonify({'error': f"Telegram API error: {result.get('description', 'Unknown error')}"}), 400
                else:
                    return jsonify({'error': f"HTTP {response.status_code}: {response.text}"}), 400
                    
            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'Connection error: {str(e)}'}), 400
            except Exception as e:
                return jsonify({'error': f'Telegram error: {str(e)}'}), 400
        
        return jsonify({'error': 'No valid Telegram connection configured'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/bot/<bot_id>/stop', methods=['POST'])
def stop_bot(bot_id):
    """Emergency stop bot operations"""
    try:
        # Get bot details
        response = requests.get(f"{BOT_MANAGER_URL}/api/bots/{bot_id}")
        bot = response.json() if response.status_code == 200 else None
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Update bot status to disabled/stopped using the status endpoint
        update_data = {
            'status': 'disabled',
            'error_message': 'Bot manually stopped via UI'
        }
        
        response = requests.put(f"{BOT_MANAGER_URL}/api/bots/{bot_id}/status", json=update_data)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Bot stopped successfully',
                'bot_id': bot_id,
                'status': 'disabled'
            })
        else:
            return jsonify({'error': 'Failed to stop bot'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/bot/<bot_id>/restart', methods=['POST'])
def restart_bot(bot_id):
    """Restart bot operations"""
    try:
        # Get bot details
        response = requests.get(f"{BOT_MANAGER_URL}/api/bots/{bot_id}")
        bot = response.json() if response.status_code == 200 else None
        
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        # Update bot status to idle/active
        update_data = {
            'status': 'idle',
            'error_message': None
        }
        
        response = requests.put(f"{BOT_MANAGER_URL}/api/bots/{bot_id}", json=update_data)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Bot restarted successfully',
                'bot_id': bot_id,
                'status': 'idle'
            })
        else:
            return jsonify({'error': 'Failed to restart bot'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/bot/<bot_id>/delete', methods=['POST'])
def delete_bot(bot_id):
    """Delete bot"""
    try:
        response = requests.delete(f"{BOT_MANAGER_URL}/api/bots/{bot_id}")
        if response.status_code == 200:
            flash('Bot deleted successfully! 🗑️', 'success')
        else:
            flash('Error deleting bot', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'bot-manager-ui',
        'version': '1.0.0'
    })

@app.route('/bot/<bot_id>/run')
def run_bot(bot_id):
    """Run bot manually"""
    try:
        response = requests.post(f"{BOT_MANAGER_URL}/api/bots/{bot_id}/run")
        if response.status_code == 200:
            flash('Bot run triggered! 🚀', 'success')
        else:
            flash('Error triggering bot run', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('bot_details', bot_id=bot_id))

@app.route('/bots')
def list_bots_page():
    """List all bots page"""
    try:
        response = requests.get(f"{BOT_MANAGER_URL}/api/bots")
        bots = response.json() if response.status_code == 200 else []
        return render_template('bots_list.html', bots=bots)
    except Exception as e:
        flash(f'Error loading bots: {e}', 'error')
        return render_template('bots_list.html', bots=[])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
