from typing import TypedDict, Optional, List, Literal

class VideoState(TypedDict):
    # Inputs
    topic: str
    
    # Control Flow
    content_type: Literal["short", "long", "both"]
    retry_count: int
    
    # Long-form Artifacts
    script: Optional[str]
    voice_path: Optional[str]
    image_paths: Optional[List[str]]
    video_path: Optional[str]
    title: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    upload_status: Optional[str]
    
    # Short-form Artifacts
    short_script: Optional[str]
    short_voice_path: Optional[str] # Added to support parallel execution
    short_image_paths: Optional[List[str]] # Added to support parallel execution
    short_video_path: Optional[str]
    short_title: Optional[str]
    short_upload_status: Optional[str]
    
    # Common
    error: Optional[str]