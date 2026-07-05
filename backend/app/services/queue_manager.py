import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class QueuePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class QueueManagerService:
    """Service for queue management and prioritization"""
    
    def __init__(self, max_queue_size: int = 100, timeout_minutes: int = 30):
        """
        Initialize queue manager
        
        Args:
            max_queue_size: Maximum queue size
            timeout_minutes: Queue entry timeout in minutes
        """
        self.max_queue_size = max_queue_size
        self.timeout_minutes = timeout_minutes
        self.priority_weights = {
            "critical": 100,
            "high": 75,
            "normal": 50,
            "low": 25
        }
    
    def get_next_in_queue(self, queue_entries: List[Dict]) -> Optional[Dict]:
        """
        Get next person in queue based on priority
        
        Args:
            queue_entries: List of queue entries
            
        Returns:
            Next queue entry or None
        """
        if not queue_entries:
            return None
        
        # Filter waiting entries
        waiting = [e for e in queue_entries if e.get("status") == "waiting"]
        
        if not waiting:
            return None
        
        # Sort by priority and queue number
        waiting.sort(
            key=lambda x: (
                -self.priority_weights.get(x.get("priority"), 50),
                x.get("created_at", datetime.utcnow())
            )
        )
        
        return waiting[0]
    
    def calculate_wait_time(self, position: int, avg_processing_time: float = 5.0) -> float:
        """
        Calculate estimated wait time
        
        Args:
            position: Position in queue
            avg_processing_time: Average processing time in minutes
            
        Returns:
            Estimated wait time in minutes
        """
        return (position - 1) * avg_processing_time
    
    def check_queue_timeouts(self, queue_entries: List[Dict]) -> List[Dict]:
        """
        Check for timed out queue entries
        
        Args:
            queue_entries: List of queue entries
            
        Returns:
            List of timed out entries
        """
        timeout_entries = []
        now = datetime.utcnow()
        timeout_delta = timedelta(minutes=self.timeout_minutes)
        
        for entry in queue_entries:
            if entry.get("status") == "waiting":
                created_at = entry.get("created_at")
                if created_at and (now - created_at) > timeout_delta:
                    timeout_entries.append(entry)
                    logger.warning(f"Queue entry timed out: {entry.get('id')}")
        
        return timeout_entries
    
    def recalculate_queue_positions(self, queue_entries: List[Dict]) -> List[Dict]:
        """
        Recalculate queue positions after changes
        
        Args:
            queue_entries: List of queue entries
            
        Returns:
            Updated queue entries with new positions
        """
        # Filter waiting entries and sort
        waiting = [e for e in queue_entries if e.get("status") == "waiting"]
        waiting.sort(
            key=lambda x: (
                -self.priority_weights.get(x.get("priority"), 50),
                x.get("created_at", datetime.utcnow())
            )
        )
        
        # Update positions
        for idx, entry in enumerate(waiting, 1):
            entry["queue_position"] = idx
        
        logger.info(f"Queue positions recalculated: {len(waiting)} entries")
        
        return waiting
    
    def get_queue_statistics(self, queue_entries: List[Dict]) -> Dict:
        """
        Get queue statistics
        
        Args:
            queue_entries: List of queue entries
            
        Returns:
            Queue statistics dictionary
        """
        waiting = len([e for e in queue_entries if e.get("status") == "waiting"])
        in_progress = len([e for e in queue_entries if e.get("status") == "in_progress"])
        completed = len([e for e in queue_entries if e.get("status") == "completed"])
        
        # Calculate average processing time
        completed_entries = [e for e in queue_entries if e.get("status") == "completed"]
        avg_time = 0.0
        if completed_entries:
            total_time = 0.0
            for entry in completed_entries:
                start = entry.get("processing_start")
                end = entry.get("processing_end")
                if start and end:
                    total_time += (end - start).total_seconds() / 60  # Convert to minutes
            avg_time = total_time / len(completed_entries)
        
        return {
            "waiting": waiting,
            "in_progress": in_progress,
            "completed": completed,
            "total": len(queue_entries),
            "avg_processing_time_minutes": avg_time,
            "queue_utilization": len(queue_entries) / self.max_queue_size,
            "timestamp": datetime.utcnow().isoformat()
        }
