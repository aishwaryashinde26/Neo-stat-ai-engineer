import json
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from db.models import ConversationHistory
from db.database import SessionLocal


class MemoryManager:
    """
    Manages short-term conversation memory for the AI booking assistant.
    Stores and retrieves the last N messages for context-aware conversations.
    """
    
    def __init__(self, max_messages: int = 25):
        """
        Initialize the memory manager.
        
        Args:
            max_messages: Maximum number of messages to keep per session (default: 25)
        """
        self.max_messages = max_messages
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: Unique identifier for the conversation session
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional dictionary with additional context
        """
        db = SessionLocal()
        try:
            message = ConversationHistory(
                session_id=session_id,
                role=role,
                content=content,
                extra_metadata=json.dumps(metadata) if metadata else None
            )
            db.add(message)
            db.commit()
            
            # Auto-cleanup to maintain message limit
            self.cleanup_old_messages(session_id, keep_last=self.max_messages)
        finally:
            db.close()
    
    def get_recent_messages(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve recent messages for a session.
        
        Args:
            session_id: Unique identifier for the conversation session
            limit: Maximum number of messages to retrieve (default: self.max_messages)
        
        Returns:
            List of message dictionaries with role, content, timestamp, and metadata
        """
        if limit is None:
            limit = self.max_messages
            
        db = SessionLocal()
        try:
            messages = db.query(ConversationHistory)\
                .filter(ConversationHistory.session_id == session_id)\
                .order_by(ConversationHistory.timestamp.desc())\
                .limit(limit)\
                .all()
            
            # Reverse to get chronological order
            messages = list(reversed(messages))
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "metadata": json.loads(msg.extra_metadata) if msg.extra_metadata else None
                }
                for msg in messages
            ]
        finally:
            db.close()
    
    def get_formatted_context(
        self, 
        session_id: str, 
        format_type: str = 'rag',
        limit: Optional[int] = None
    ) -> str:
        """
        Get formatted conversation context for different use cases.
        
        Args:
            session_id: Unique identifier for the conversation session
            format_type: 'rag' for RAG prompts, 'booking' for booking flow
            limit: Maximum number of messages to include
        
        Returns:
            Formatted string of conversation history
        """
        messages = self.get_recent_messages(session_id, limit)
        
        if format_type == 'rag':
            # Format for RAG: Simple role-content pairs
            formatted = []
            for msg in messages:
                formatted.append(f"{msg['role'].upper()}: {msg['content']}")
            return "\n".join(formatted)
        
        elif format_type == 'booking':
            # Format for booking flow: More detailed with timestamps
            formatted = []
            for msg in messages:
                time_str = msg['timestamp'].strftime("%H:%M:%S")
                formatted.append(f"[{time_str}] {msg['role']}: {msg['content']}")
            return "\n".join(formatted)
        
        else:
            # Default format
            return str(messages)
    
    def get_messages_as_list(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Get messages as a simple list of role-content dictionaries.
        Useful for Streamlit session state.
        
        Args:
            session_id: Unique identifier for the conversation session
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of dictionaries with 'role' and 'content' keys
        """
        messages = self.get_recent_messages(session_id, limit)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
    
    def cleanup_old_messages(
        self, 
        session_id: str, 
        keep_last: int = 25
    ) -> int:
        """
        Remove old messages beyond the limit.
        
        Args:
            session_id: Unique identifier for the conversation session
            keep_last: Number of most recent messages to keep
        
        Returns:
            Number of messages deleted
        """
        db = SessionLocal()
        try:
            # Get all messages for this session, ordered by timestamp
            all_messages = db.query(ConversationHistory)\
                .filter(ConversationHistory.session_id == session_id)\
                .order_by(ConversationHistory.timestamp.desc())\
                .all()
            
            # If we have more than keep_last, delete the oldest ones
            if len(all_messages) > keep_last:
                messages_to_delete = all_messages[keep_last:]
                deleted_count = 0
                for msg in messages_to_delete:
                    db.delete(msg)
                    deleted_count += 1
                db.commit()
                return deleted_count
            
            return 0
        finally:
            db.close()
    
    def clear_session(self, session_id: str) -> int:
        """
        Clear all messages for a session.
        
        Args:
            session_id: Unique identifier for the conversation session
        
        Returns:
            Number of messages deleted
        """
        db = SessionLocal()
        try:
            deleted_count = db.query(ConversationHistory)\
                .filter(ConversationHistory.session_id == session_id)\
                .delete()
            db.commit()
            return deleted_count
        finally:
            db.close()
    
    def get_session_count(self, session_id: str) -> int:
        """
        Get the number of messages in a session.
        
        Args:
            session_id: Unique identifier for the conversation session
        
        Returns:
            Number of messages in the session
        """
        db = SessionLocal()
        try:
            count = db.query(ConversationHistory)\
                .filter(ConversationHistory.session_id == session_id)\
                .count()
            return count
        finally:
            db.close()


# Singleton instance
memory_manager = MemoryManager(max_messages=25)
