"""
Bot Manager - Core Bot Management Logic
"""
import os
import uuid
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import Bot, BotConfig, BotRun, BotStatus, RunStatus

class BotManager:
    """Centralized Bot Management System"""
    
    def __init__(self, db_path: str = "bot_manager.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Initialize the bot manager database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Bots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bots (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    city_name TEXT NOT NULL,
                    country_code TEXT NOT NULL,
                    bot_token TEXT NOT NULL,
                    telegram_chat_id TEXT NOT NULL,
                    news_language TEXT DEFAULT 'en',
                    post_interval_minutes INTEGER DEFAULT 30,
                    max_posts_per_run INTEGER DEFAULT 5,
                    openai_api_key TEXT,
                    google_translate_api_key TEXT,
                    newsapi_key TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    status TEXT DEFAULT 'idle',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_run TIMESTAMP,
                    total_posts INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)
            
            # Bot runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_runs (
                    id TEXT PRIMARY KEY,
                    bot_id TEXT NOT NULL,
                    run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed INTEGER DEFAULT 0,
                    posted INTEGER DEFAULT 0,
                    duration REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    metadata TEXT,
                    FOREIGN KEY (bot_id) REFERENCES bots (id)
                )
            """)
            
            # Services table - for external service registration
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    endpoint_url TEXT NOT NULL,
                    api_key TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_ping TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def create_bot(self, config: BotConfig) -> Bot:
        """Create a new bot"""
        bot_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bots (
                    id, name, city_name, country_code, bot_token, telegram_chat_id,
                    news_language, post_interval_minutes, max_posts_per_run,
                    openai_api_key, google_translate_api_key, newsapi_key, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bot_id, config.name, config.city_name, config.country_code,
                config.bot_token, config.telegram_chat_id, config.news_language,
                config.post_interval_minutes, config.max_posts_per_run,
                config.openai_api_key, config.google_translate_api_key,
                config.newsapi_key, config.is_active
            ))
            conn.commit()
        
        return Bot(
            id=bot_id,
            config=config,
            status=BotStatus.IDLE,
            created_at=datetime.utcnow()
        )
    
    def get_bot(self, bot_id: str) -> Optional[Bot]:
        """Get a bot by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, city_name, country_code, bot_token, telegram_chat_id,
                       news_language, post_interval_minutes, max_posts_per_run,
                       openai_api_key, google_translate_api_key, newsapi_key, is_active,
                       status, created_at, last_run, total_posts, error_message
                FROM bots WHERE id = ?
            """, (bot_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            config = BotConfig(
                name=row[1], city_name=row[2], country_code=row[3],
                bot_token=row[4], telegram_chat_id=row[5], news_language=row[6],
                post_interval_minutes=row[7], max_posts_per_run=row[8],
                openai_api_key=row[9], google_translate_api_key=row[10],
                newsapi_key=row[11], is_active=bool(row[12])
            )
            
            return Bot(
                id=row[0], config=config, status=BotStatus(row[13]),
                created_at=datetime.fromisoformat(row[14]) if row[14] else None,
                last_run=datetime.fromisoformat(row[15]) if row[15] else None,
                total_posts=row[16], error_message=row[17]
            )
    
    def list_bots(self, active_only: bool = False) -> List[Bot]:
        """List all bots"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, name, city_name, country_code, bot_token, telegram_chat_id,
                       news_language, post_interval_minutes, max_posts_per_run,
                       openai_api_key, google_translate_api_key, newsapi_key, is_active,
                       status, created_at, last_run, total_posts, error_message
                FROM bots
            """
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            bots = []
            for row in rows:
                config = BotConfig(
                    name=row[1], city_name=row[2], country_code=row[3],
                    bot_token=row[4], telegram_chat_id=row[5], news_language=row[6],
                    post_interval_minutes=row[7], max_posts_per_run=row[8],
                    openai_api_key=row[9], google_translate_api_key=row[10],
                    newsapi_key=row[11], is_active=bool(row[12])
                )
                
                bots.append(Bot(
                    id=row[0], config=config, status=BotStatus(row[13]),
                    created_at=datetime.fromisoformat(row[14]) if row[14] else None,
                    last_run=datetime.fromisoformat(row[15]) if row[15] else None,
                    total_posts=row[16], error_message=row[17]
                ))
            
            return bots
    
    def update_bot(self, bot_id: str, config: BotConfig) -> bool:
        """Update bot configuration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE bots SET
                    name = ?, city_name = ?, country_code = ?, bot_token = ?,
                    telegram_chat_id = ?, news_language = ?, post_interval_minutes = ?,
                    max_posts_per_run = ?, openai_api_key = ?, google_translate_api_key = ?,
                    newsapi_key = ?, is_active = ?
                WHERE id = ?
            """, (
                config.name, config.city_name, config.country_code, config.bot_token,
                config.telegram_chat_id, config.news_language, config.post_interval_minutes,
                config.max_posts_per_run, config.openai_api_key, config.google_translate_api_key,
                config.newsapi_key, config.is_active, bot_id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_bot(self, bot_id: str) -> bool:
        """Delete a bot"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bot_runs WHERE bot_id = ?", (bot_id,))
            cursor.execute("DELETE FROM bots WHERE id = ?", (bot_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_bot_status(self, bot_id: str, status: BotStatus, error_message: str = None) -> bool:
        """Update bot status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE bots SET status = ?, error_message = ?
                WHERE id = ?
            """, (status.value, error_message, bot_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def record_bot_run(self, run: BotRun) -> bool:
        """Record a bot run"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bot_runs (
                    id, bot_id, run_time, processed, posted, duration, status, error_message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.id, run.bot_id, run.run_time, run.processed, run.posted,
                run.duration, run.status.value, run.error_message,
                str(run.metadata) if run.metadata else None
            ))
            
            # Update bot stats
            if run.status == RunStatus.SUCCESS:
                cursor.execute("""
                    UPDATE bots SET total_posts = total_posts + ?, last_run = ?
                    WHERE id = ?
                """, (run.posted, run.run_time, run.bot_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_bot_runs(self, bot_id: str, limit: int = 10) -> List[BotRun]:
        """Get recent runs for a bot"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, bot_id, run_time, processed, posted, duration, status, error_message, metadata
                FROM bot_runs
                WHERE bot_id = ?
                ORDER BY run_time DESC
                LIMIT ?
            """, (bot_id, limit))
            
            rows = cursor.fetchall()
            runs = []
            for row in rows:
                metadata = eval(row[8]) if row[8] else {}
                runs.append(BotRun(
                    id=row[0], bot_id=row[1], run_time=datetime.fromisoformat(row[2]),
                    processed=row[3], posted=row[4], duration=row[5],
                    status=RunStatus(row[6]), error_message=row[7], metadata=metadata
                ))
            
            return runs
    
    # Service Management Methods
    def register_service(self, service_id: str, name: str, service_type: str, 
                        endpoint_url: str, api_key: str = None) -> bool:
        """Register an external service"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO services (id, name, service_type, endpoint_url, api_key)
                VALUES (?, ?, ?, ?, ?)
            """, (service_id, name, service_type, endpoint_url, api_key))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_services(self, service_type: str = None) -> List[Dict[str, Any]]:
        """Get registered services"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT id, name, service_type, endpoint_url, api_key, is_active, created_at, last_ping FROM services"
            params = []
            if service_type:
                query += " WHERE service_type = ?"
                params.append(service_type)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [{
                'id': row[0], 'name': row[1], 'service_type': row[2],
                'endpoint_url': row[3], 'api_key': row[4], 'is_active': bool(row[5]),
                'created_at': row[6], 'last_ping': row[7]
            } for row in rows]
    
    def update_service_ping(self, service_id: str) -> bool:
        """Update service last ping time"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE services SET last_ping = CURRENT_TIMESTAMP WHERE id = ?
            """, (service_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_service(self, service_id: str) -> bool:
        """Delete a service"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
            conn.commit()
            return cursor.rowcount > 0
