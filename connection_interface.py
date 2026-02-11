"""
Connection Interface - Generic Bot Communication Layer
"""
import requests
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from models_v2 import ConnectionConfig, ConnectionType

class ConnectionInterface(ABC):
    """Abstract base class for all bot connections"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def connect(self) -> bool:
        """Test connection to the service"""
        pass
    
    @abstractmethod
    def send_message(self, message: str, **kwargs) -> bool:
        """Send a message through the connection"""
        pass
    
    @abstractmethod
    def receive_messages(self, **kwargs) -> List[Dict[str, Any]]:
        """Receive messages from the connection"""
        pass
    
    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection status and info"""
        pass

class TelegramConnection(ConnectionInterface):
    """Telegram bot connection implementation"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.base_url = config.endpoint
        self.bot_token = config.credentials.get('bot_token')
        self.chat_id = config.credentials.get('chat_id')
        self.settings = config.settings
    
    def connect(self) -> bool:
        """Test Telegram bot connection"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Telegram connection test failed: {e}")
            return False
    
    def send_message(self, message: str, **kwargs) -> bool:
        """Send message to Telegram chat"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': self.settings.get('parse_mode', 'Markdown'),
                'disable_web_page_preview': self.settings.get('disable_web_page_preview', False)
            }
            
            response = requests.post(url, json=data, timeout=30)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def receive_messages(self, **kwargs) -> List[Dict[str, Any]]:
        """Receive messages from Telegram (optional)"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                'timeout': kwargs.get('timeout', 30),
                'limit': kwargs.get('limit', 100)
            }
            
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                updates = response.json().get('result', [])
                return self._format_updates(updates)
            return []
        except Exception as e:
            self.logger.error(f"Failed to receive Telegram messages: {e}")
            return []
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get Telegram connection info"""
        return {
            'type': 'telegram',
            'chat_id': self.chat_id,
            'connected': self.connect(),
            'settings': self.settings
        }
    
    def _format_updates(self, updates: List[Dict]) -> List[Dict[str, Any]]:
        """Format Telegram updates"""
        formatted = []
        for update in updates:
            if 'message' in update:
                message = update['message']
                formatted.append({
                    'id': update['update_id'],
                    'text': message.get('text', ''),
                    'from': message.get('from', {}),
                    'chat': message.get('chat', {}),
                    'date': message.get('date'),
                    'raw': message
                })
        return formatted

class WebhookConnection(ConnectionInterface):
    """Generic webhook connection implementation"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.endpoint = config.endpoint
        self.api_key = config.credentials.get('api_key')
        self.secret = config.credentials.get('secret')
        self.settings = config.settings
    
    def connect(self) -> bool:
        """Test webhook connection"""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.endpoint}/health", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Webhook connection test failed: {e}")
            return False
    
    def send_message(self, message: str, **kwargs) -> bool:
        """Send message via webhook"""
        try:
            headers = self._get_headers()
            data = {
                'message': message,
                'timestamp': kwargs.get('timestamp'),
                'metadata': kwargs.get('metadata', {})
            }
            
            response = requests.post(
                self.endpoint,
                json=data,
                headers=headers,
                timeout=self.settings.get('timeout', 30)
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to send webhook message: {e}")
            return False
    
    def receive_messages(self, **kwargs) -> List[Dict[str, Any]]:
        """Receive messages via webhook (polling)"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.endpoint}/messages",
                headers=headers,
                timeout=self.settings.get('timeout', 30)
            )
            
            if response.status_code == 200:
                return response.json().get('messages', [])
            return []
        except Exception as e:
            self.logger.error(f"Failed to receive webhook messages: {e}")
            return []
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get webhook connection info"""
        return {
            'type': 'webhook',
            'endpoint': self.endpoint,
            'connected': self.connect(),
            'settings': self.settings
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"
        if self.secret:
            headers['X-Secret'] = self.secret
        return headers

class ConnectionFactory:
    """Factory for creating connection instances"""
    
    @staticmethod
    def create_connection(config: ConnectionConfig) -> ConnectionInterface:
        """Create connection instance based on type"""
        if config.connection_type == ConnectionType.TELEGRAM:
            return TelegramConnection(config)
        elif config.connection_type == ConnectionType.WEBHOOK:
            return WebhookConnection(config)
        else:
            raise ValueError(f"Unsupported connection type: {config.connection_type}")
    
    @staticmethod
    def get_available_connections() -> List[Dict[str, Any]]:
        """Get list of available connection types"""
        return [
            {
                'type': 'telegram',
                'name': 'Telegram Bot',
                'description': 'Send messages to Telegram channels and groups',
                'required_credentials': ['bot_token', 'chat_id'],
                'optional_settings': ['parse_mode', 'disable_web_page_preview', 'max_message_length']
            },
            {
                'type': 'webhook',
                'name': 'Webhook',
                'description': 'Send messages to any webhook endpoint',
                'required_credentials': ['api_key'],
                'optional_settings': ['timeout', 'retry_attempts']
            }
        ]
