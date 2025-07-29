"""Base model functionality for wikijs-python-sdk."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class BaseModel(PydanticBaseModel):
    """Base model with common functionality for all data models.
    
    Provides:
    - Automatic validation via Pydantic
    - JSON serialization/deserialization
    - Field aliases for API compatibility
    - Consistent datetime handling
    """
    
    model_config = ConfigDict(
        # Allow population by field name or alias
        populate_by_name=True,
        # Validate assignment to attributes
        validate_assignment=True,
        # Use enum values instead of names
        use_enum_values=True,
        # Allow extra fields for forward compatibility
        extra="ignore",
        # Serialize datetime as ISO format
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary.
        
        Args:
            exclude_none: Whether to exclude None values
            
        Returns:
            Dictionary representation of the model
        """
        return self.model_dump(exclude_none=exclude_none, by_alias=True)
    
    def to_json(self, exclude_none: bool = True) -> str:
        """Convert model to JSON string.
        
        Args:
            exclude_none: Whether to exclude None values
            
        Returns:
            JSON string representation of the model
        """
        return self.model_dump_json(exclude_none=exclude_none, by_alias=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create model instance from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            Model instance
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseModel":
        """Create model instance from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            Model instance
        """
        return cls.model_validate_json(json_str)


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def is_new(self) -> bool:
        """Check if this is a new (unsaved) model."""
        return self.created_at is None