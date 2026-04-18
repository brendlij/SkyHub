"""Event system for real-time notifications."""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, asdict


@dataclass
class Event:
    """Base event class."""
    type: str
    timestamp: datetime
    scope: str = "global"  # global, node:{id}, camera:{id}
    data: Dict[str, Any] = None
    
    def to_dict(self) -> dict:
        """Convert to dict."""
        return {
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "scope": self.scope,
            "data": self.data or {},
        }


class EventSystem:
    """In-memory event bus for real-time updates."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue: Dict[str, List[Event]] = {}  # Per-scope queue
        self.max_queue_size = 100
    
    def emit(self, event: Event) -> None:
        """
        Emit an event to all subscribers.
        
        Args:
            event: Event to emit
        """
        # Add to queue
        if event.scope not in self.event_queue:
            self.event_queue[event.scope] = []
        
        self.event_queue[event.scope].append(event)
        
        # Keep queue size bounded
        if len(self.event_queue[event.scope]) > self.max_queue_size:
            self.event_queue[event.scope].pop(0)
        
        # Call subscribers
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event subscriber: {e}")
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            if callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
    
    def get_events_since(self, scope: str, since: datetime) -> List[Event]:
        """
        Get all events for a scope since a given time.
        
        Args:
            scope: Event scope (e.g., "camera:node-1:camera-1")
            since: Only return events after this timestamp
            
        Returns:
            List of events
        """
        if scope not in self.event_queue:
            return []
        
        return [e for e in self.event_queue[scope] if e.timestamp > since]
    
    def clear_events(self, scope: str) -> None:
        """Clear event queue for a scope."""
        if scope in self.event_queue:
            self.event_queue[scope] = []


# Global event system instance
event_system = EventSystem()


# Event type constants
class EventType:
    """Event types."""
    CONFIG_CHANGED = "CONFIG_CHANGED"
    CAPTURE_STARTED = "CAPTURE_STARTED"
    CAPTURE_COMPLETED = "CAPTURE_COMPLETED"
    NODE_CONNECTED = "NODE_CONNECTED"
    NODE_DISCONNECTED = "NODE_DISCONNECTED"
    ERROR = "ERROR"
