"""
Real-time Bot - Immediate Message Processing
"""
import uuid
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from models_realtime import Bot, BotConfig, ConnectionConfig, BotMessage, BotStatus
from connection_interface import ConnectionFactory

class RealtimeBot:
    """Real-time bot that processes messages immediately"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.connection = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize connection based on bot config"""
        if self.bot.config.connection:
            self.connection = ConnectionFactory.create_connection(self.bot.config.connection)
    
    def receive_message(self, message_data: Dict[str, Any]) -> BotMessage:
        """Receive and immediately process message"""
        # Create message record
        message = BotMessage(
            id=str(uuid.uuid4()),
            bot_id=self.bot.id,
            received_at=datetime.utcnow(),
            message_data=message_data
        )
        
        # Process immediately (real-time)
        self._process_message(message)
        
        return message
    
    def _process_message(self, message: BotMessage):
        """Process message immediately"""
        try:
            # Update bot status
            self.bot.status = BotStatus.RUNNING
            self.bot.last_message = datetime.utcnow()
            
            # Send to configured endpoint immediately
            if self.connection:
                success = self._send_message(message.message_data)
                if success:
                    message.status = "sent"
                    message.sent_at = datetime.utcnow()
                    self.bot.total_messages += 1
                else:
                    message.status = "failed"
                    self.bot.error_message = "Failed to send message"
            
            # Update bot status back to idle
            self.bot.status = BotStatus.IDLE
            
        except Exception as e:
            message.status = "error"
            self.bot.status = BotStatus.ERROR
            self.bot.error_message = str(e)
    
    def _send_message(self, message_data: Dict[str, Any]) -> bool:
        """Send message through configured connection"""
        if not self.connection:
            return False
        
        # Format message for sending
        formatted_message = self._format_message(message_data)
        
        # Send immediately
        return self.connection.send_message(formatted_message)
    
    def _format_message(self, message_data: Dict[str, Any]) -> str:
        """Format message for sending"""
        if isinstance(message_data, str):
            return message_data
        elif isinstance(message_data, dict):
            # Convert dict to readable format
            if 'text' in message_data:
                return message_data['text']
            elif 'message' in message_data:
                return message_data['message']
            else:
                return str(message_data)
        else:
            return str(message_data)
    
    def test_connection(self) -> bool:
        """Test if connection is working"""
        if not self.connection:
            return False
        return self.connection.connect()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'bot_id': self.bot.id,
            'status': self.bot.status.value,
            'last_message': self.bot.last_message.isoformat() if self.bot.last_message else None,
            'total_messages': self.bot.total_messages,
            'connection_status': 'connected' if self.test_connection() else 'disconnected',
            'error_message': self.bot.error_message
        }
