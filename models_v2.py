"""
Bot Manager Models v2 - Connection-based Architecture
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
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

class ConnectionType(Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"
    WEBHOOK = "webhook"
    EMAIL = "email"

@dataclass
class ConnectionConfig:
    """Generic connection configuration"""
    connection_type: ConnectionType
    endpoint: str
    credentials: Dict[str, Any]
    settings: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'connection_type': self.connection_type.value,
            'endpoint': self.endpoint,
            'credentials': self.credentials,
            'settings': self.settings
        }

@dataclass
class BotConfig:
    """Flexible bot configuration"""
    name: str
    description: Optional[str] = None
    connection: Optional[ConnectionConfig] = None
    data_sources: List[Dict[str, Any]] = None
    processing_rules: Dict[str, Any] = None
    schedule: Optional[Dict[str, Any]] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = []
        if self.processing_rules is None:
            self.processing_rules = {}
        if self.schedule is None:
            self.schedule = {}
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.connection:
            result['connection'] = self.connection.to_dict()
        return result

@dataclass
class Bot:
    """Bot entity"""
    id: str
    config: BotConfig
    status: BotStatus = BotStatus.IDLE
    created_at: datetime = None
    last_run: Optional[datetime] = None
    total_posts: int = 0
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
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'total_posts': self.total_posts,
            'error_message': self.error_message
        }

@dataclass
class BotRun:
    """Bot run record"""
    id: str
    bot_id: str
    run_time: datetime
    processed: int = 0
    posted: int = 0
    duration: float = 0.0
    status: RunStatus = RunStatus.SUCCESS
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.run_time is None:
            self.run_time = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'run_time': self.run_time.isoformat(),
            'processed': self.processed,
            'posted': self.posted,
            'duration': self.duration,
            'status': self.status.value,
            'error_message': self.error_message,
            'metadata': self.metadata or {}
        }

# Predefined connection templates
TELEGRAM_CONNECTION = {
    'connection_type': ConnectionType.TELEGRAM,
    'endpoint': 'https://api.telegram.org/bot{token}',
    'credentials': {'bot_token': '', 'chat_id': ''},
    'settings': {
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False,
        'max_message_length': 4096
    }
}

WEBHOOK_CONNECTION = {
    'connection_type': ConnectionType.WEBHOOK,
    'endpoint': '',
    'credentials': {'api_key': '', 'secret': ''},
    'settings': {
        'timeout': 30,
        'retry_attempts': 3
    }
}

# Predefined data source templates
RSS_DATA_SOURCE = {
    'type': 'rss',
    'url': '',
    'settings': {
        'update_interval': 300,
        'max_items': 50
    }
}

NEWSAPI_DATA_SOURCE = {
    'type': 'newsapi',
    'url': 'https://newsapi.org/v2/everything',
    'credentials': {'api_key': ''},
    'settings': {
        'page_size': 20,
        'language': 'en'
    }
}

# Predefined processing rules
DEFAULT_PROCESSING_RULES = {
    'filters': {
        'min_relevance_score': 0.3,
        'exclude_duplicates': True,
        'max_age_hours': 24
    },
    'transformations': {
        'summarize': False,
        'translate': False,
        'target_language': 'en'
    },
    'limits': {
        'max_posts_per_run': 5,
        'min_interval_minutes': 30
    }
}
