"""
Bot Manager Models - Real-time Architecture
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

class BotStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    CONNECTED = "connected"
    ERROR = "error"
    DISABLED = "disabled"

class RunStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class ConnectionConfig:
    """Connection configuration"""
    connection_type: str  # telegram, webhook, email
    endpoint: str
    credentials: Dict[str, Any]
    settings: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BotConfig:
    """Real-time bot configuration"""
    name: str
    description: Optional[str] = None
    connection: Optional[ConnectionConfig] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.connection:
            result['connection'] = self.connection.to_dict()
        return result

@dataclass
class Bot:
    """Bot entity - Real-time"""
    id: str
    config: BotConfig
    status: BotStatus = BotStatus.IDLE
    created_at: datetime = None
    last_message: Optional[datetime] = None
    total_messages: int = 0
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'config': self.config.to_dict(),
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_message': self.last_message.isoformat() if self.last_message else None,
            'total_messages': self.total_messages,
            'error_message': self.error_message
        }

@dataclass
class BotMessage:
    """Message received by bot"""
    id: str
    bot_id: str
    received_at: datetime
    message_data: Dict[str, Any]
    processed_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.received_at is None:
            self.received_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'received_at': self.received_at.isoformat(),
            'message_data': self.message_data,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status
        }
