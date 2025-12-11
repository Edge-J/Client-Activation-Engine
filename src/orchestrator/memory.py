"""
Memory management for orchestration workflows.

This module provides working memory, artifact registry, and context management
for maintaining state throughout the client activation process.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from ..core.enums import ProcessingStatus
from ..core.schema_definitions import BaseSchema


class WorkingMemoryItem(BaseSchema):
    """Individual item stored in working memory."""
    key: str
    value: Any
    item_type: str
    ttl_seconds: int | None = None
    access_count: int = 0
    last_accessed: datetime = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if the memory item has expired."""
        if self.ttl_seconds is None:
            return False
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() > expiry_time
    
    def access(self) -> None:
        """Mark item as accessed and update statistics."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class WorkingMemory:
    """
    Working memory for temporary storage during workflow execution.
    
    Manages short-term data with automatic expiration and cleanup.
    """
    
    def __init__(self, max_items: int = 1000, default_ttl: int = 3600):
        """
        Initialize working memory.
        
        Args:
            max_items: Maximum number of items to store
            default_ttl: Default time-to-live in seconds
        """
        self.max_items = max_items
        self.default_ttl = default_ttl
        self._items: dict[str, WorkingMemoryItem] = {}
        
    def store(
        self, 
        key: str, 
        value: Any, 
        item_type: str = "general",
        ttl_seconds: int | None = None,
    ) -> None:
        """
        Store an item in working memory.
        
        Args:
            key: Unique identifier for the item
            value: Value to store
            item_type: Type classification for the item
            ttl_seconds: Time-to-live in seconds (uses default if None)
        """
        # Clean up expired items if at capacity
        if len(self._items) >= self.max_items:
            self._cleanup_expired()
            
        # If still at capacity, remove oldest item
        if len(self._items) >= self.max_items:
            oldest_key = min(
                self._items.keys(),
                key=lambda k: self._items[k].last_accessed,
            )
            del self._items[oldest_key]
        
        # Store new item
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._items[key] = WorkingMemoryItem(
            key=key,
            value=value,
            item_type=item_type,
            ttl_seconds=ttl,
        )
    
    def retrieve(self, key: str) -> Any | None:
        """
        Retrieve an item from working memory.
        
        Args:
            key: Item identifier
            
        Returns:
            Stored value or None if not found/expired
        """
        if key not in self._items:
            return None
            
        item = self._items[key]
        
        # Check if expired
        if item.is_expired():
            del self._items[key]
            return None
        
        # Update access statistics
        item.access()
        return item.value
    
    def get(self, key: str) -> Any | None:
        """
        Get an item from working memory (alias for retrieve).
        
        Args:
            key: Item identifier
            
        Returns:
            Stored value or None if not found/expired
        """
        return self.retrieve(key)
    
    def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired."""
        if key not in self._items:
            return False
        
        item = self._items[key]
        if item.is_expired():
            del self._items[key]
            return False
        
        return True
    
    def remove(self, key: str) -> bool:
        """
        Remove an item from memory.
        
        Args:
            key: Item identifier
            
        Returns:
            True if item was removed, False if not found
        """
        if key in self._items:
            del self._items[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all items from memory."""
        self._items.clear()
    
    def get_stats(self) -> dict[str, Any]:
        """
        Get memory usage statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        self._cleanup_expired()
        
        total_items = len(self._items)
        type_counts = {}
        total_access = 0
        
        for item in self._items.values():
            type_counts[item.item_type] = type_counts.get(item.item_type, 0) + 1
            total_access += item.access_count
        
        return {
            "total_items": total_items,
            "max_items": self.max_items,
            "utilization": total_items / self.max_items if self.max_items > 0 else 0,
            "type_distribution": type_counts,
            "total_accesses": total_access,
            "average_accesses": total_access / max(total_items, 1),
        }
    
    def _cleanup_expired(self) -> int:
        """
        Remove expired items from memory.
        
        Returns:
            Number of items removed
        """
        expired_keys = [
            key for key, item in self._items.items()
            if item.is_expired()
        ]
        
        for key in expired_keys:
            del self._items[key]
            
        return len(expired_keys)


class ArtifactRecord(BaseSchema):
    """Record of a generated or processed artifact."""
    name: str
    artifact_type: str
    file_path: str | None = None
    content: str | None = None
    metadata: dict[str, Any] = {}
    checksum: str | None = None
    size_bytes: int = 0
    client_id: UUID | None = None
    workflow_id: UUID | None = None
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary information about the artifact.""" 
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.artifact_type,
            "size": self.size_bytes,
            "created": self.created_at.isoformat(),
            "has_file": self.file_path is not None,
            "has_content": self.content is not None,
        }


class ArtifactRegistry:
    """
    Registry for tracking generated and processed artifacts.
    
    Maintains a catalog of all artifacts created during workflows
    with metadata and access tracking.
    """
    
    def __init__(self):
        """Initialize the artifact registry."""
        self._artifacts: dict[UUID, ArtifactRecord] = {}
        self._name_index: dict[str, UUID] = {}
        self._client_index: dict[UUID, list[UUID]] = {}
        
    def register_artifact(
        self,
        name: str,
        artifact_type: str,
        file_path: str | None = None,
        content: str | None = None,
        metadata: dict[str, Any] | None = None,
        client_id: UUID | None = None,
        workflow_id: UUID | None = None,
    ) -> UUID:
        """
        Register a new artifact in the registry.
        
        Args:
            name: Artifact name (should be unique)
            artifact_type: Type of artifact
            file_path: Path to artifact file
            content: Direct content if not file-based
            metadata: Additional metadata
            client_id: Associated client ID
            workflow_id: Associated workflow ID
            
        Returns:
            UUID of the registered artifact
        """
        artifact_id = uuid4()
        
        # Calculate size if possible
        size_bytes = 0
        if content:
            size_bytes = len(content.encode('utf-8'))
        elif file_path:
            try:
                from pathlib import Path
                size_bytes = Path(file_path).stat().st_size
            except (OSError, FileNotFoundError):
                size_bytes = 0
        
        # Create artifact record
        artifact = ArtifactRecord(
            id=artifact_id,
            name=name,
            artifact_type=artifact_type,
            file_path=file_path,
            content=content,
            metadata=metadata or {},
            size_bytes=size_bytes,
            client_id=client_id,
            workflow_id=workflow_id,
        )
        
        # Store in registry
        self._artifacts[artifact_id] = artifact
        self._name_index[name] = artifact_id
        
        # Update client index
        if client_id:
            if client_id not in self._client_index:
                self._client_index[client_id] = []
            self._client_index[client_id].append(artifact_id)
        
        return artifact_id
    
    def get_artifact(self, artifact_id: UUID) -> ArtifactRecord | None:
        """Get artifact by ID."""
        return self._artifacts.get(artifact_id)
    
    def get_artifact_by_name(self, name: str) -> ArtifactRecord | None:
        """Get artifact by name."""
        artifact_id = self._name_index.get(name)
        if artifact_id:
            return self._artifacts.get(artifact_id)
        return None
    
    def get_client_artifacts(self, client_id: UUID) -> list[ArtifactRecord]:
        """Get all artifacts for a specific client."""
        artifact_ids = self._client_index.get(client_id, [])
        return [
            self._artifacts[aid] for aid in artifact_ids
            if aid in self._artifacts
        ]
    
    def list_artifacts(
        self, 
        artifact_type: str | None = None,
        client_id: UUID | None = None,
    ) -> list[ArtifactRecord]:
        """
        List artifacts with optional filtering.
        
        Args:
            artifact_type: Filter by artifact type
            client_id: Filter by client ID
            
        Returns:
            List of matching artifacts
        """
        artifacts = list(self._artifacts.values())
        
        if artifact_type:
            artifacts = [a for a in artifacts if a.artifact_type == artifact_type]
            
        if client_id:
            artifacts = [a for a in artifacts if a.client_id == client_id]
            
        return artifacts
    
    def get_registry_stats(self) -> dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with registry statistics
        """
        total_artifacts = len(self._artifacts)
        total_size = sum(a.size_bytes for a in self._artifacts.values())
        
        type_counts = {}
        client_counts = {}
        
        for artifact in self._artifacts.values():
            # Count by type
            type_counts[artifact.artifact_type] = (
                type_counts.get(artifact.artifact_type, 0) + 1
            )
            
            # Count by client
            if artifact.client_id:
                client_id_str = str(artifact.client_id)
                client_counts[client_id_str] = (
                    client_counts.get(client_id_str, 0) + 1
                )
        
        return {
            "total_artifacts": total_artifacts,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "type_distribution": type_counts,
            "client_distribution": client_counts,
            "unique_clients": len(self._client_index),
        }


class OrchestrationMemory:
    """
    Combined memory management system for orchestration workflows.
    
    Provides both working memory and artifact registry functionality
    in a unified interface.
    """
    
    def __init__(
        self,
        max_working_items: int = 1000,
        default_ttl: int = 3600,
    ):
        """
        Initialize orchestration memory.
        
        Args:
            max_working_items: Maximum working memory items
            default_ttl: Default TTL for working memory items
        """
        self.working_memory = WorkingMemory(max_working_items, default_ttl)
        self.artifact_registry = ArtifactRegistry()
        
    def get_memory_summary(self) -> dict[str, Any]:
        """
        Get comprehensive memory usage summary.
        
        Returns:
            Dictionary with memory and registry statistics
        """
        return {
            "working_memory": self.working_memory.get_stats(),
            "artifact_registry": self.artifact_registry.get_registry_stats(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def cleanup(self) -> dict[str, int]:
        """
        Perform cleanup operations.
        
        Returns:
            Dictionary with cleanup statistics
        """
        # Clean up expired working memory items
        expired_items = self.working_memory._cleanup_expired()
        
        return {
            "expired_working_items": expired_items,
            "remaining_working_items": len(self.working_memory._items),
            "total_artifacts": len(self.artifact_registry._artifacts),
        }


def create_orchestration_memory() -> OrchestrationMemory:
    """
    Create a new orchestration memory instance with default configuration.
    
    Returns:
        Configured OrchestrationMemory instance
    """
    return OrchestrationMemory(
        max_working_items=1000,
        default_ttl=3600,  # 1 hour
    )
