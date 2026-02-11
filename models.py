"""
Bot Manager Models - Data Models for Bot Management
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
class BotConfig:
    """Bot configuration data"""
    name: str
    city_name: str
    country_code: str
    bot_token: str
    telegram_chat_id: str
    news_language: str = "en"
    post_interval_minutes: int = 30
    max_posts_per_run: int = 5
    openai_api_key: Optional[str] = None
    google_translate_api_key: Optional[str] = None
    newsapi_key: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

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
