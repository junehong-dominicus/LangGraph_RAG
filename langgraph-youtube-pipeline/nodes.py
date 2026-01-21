import logging
from typing import Any, Dict
from .state import VideoState

logger = logging.getLogger(__name__)

# --- Core Logic Nodes ---

def topic_planner(state: VideoState) -> VideoState:
    """Section 10.3: Validate or select the topic."""
    logger.info("--- Topic Planner ---")
    # Ensure a topic exists, fallback to default if empty or None
    topic = state.get("topic") or "Default AI Topic"
    return {"topic": topic, "error": None}

def content_type_router(state: VideoState) -> VideoState:
    """Section 12.1: Decide content type (short, long, both)."""
    logger.info("--- Content Type Router ---")
    topic = state.get("topic", "").lower()
    
    # Decision Rules
    if "both" in topic:
        c_type = "both"
    elif any(keyword in topic for keyword in ["trend", "promo", "short"]):
        c_type = "short"
    else:
        c_type = "long" # Default
    
    logger.info(f"Decision: {c_type}")
    return {"content_type": c_type}

# --- Long Form Pipeline Nodes ---

def script_generator(state: VideoState) -> VideoState:
    """Section 10.4: Generate long-form script."""
    logger.info("--- Script Generator (Long) ---")
    return {"script": f"Long script about {state['topic']}...", "error": None}

def voice_generator(state: VideoState) -> VideoState:
    """Section 10.5: TTS for long-form."""
    logger.info("--- Voice Generator (Long) ---")
    return {"voice_path": "output/long_voice.mp3", "error": None}

def asset_generator(state: VideoState) -> VideoState:
    """Section 10.6: Visual assets for long-form."""
    logger.info("--- Asset Generator (Long) ---")
    return {"image_paths": ["img1.png", "img2.png", "img3.png"], "error": None}

def video_composer(state: VideoState) -> VideoState:
    """Section 10.7: Compose long-form video."""
    logger.info("--- Video Composer (Long) ---")
    return {"video_path": "output/final_video.mp4", "error": None}

def metadata_generator(state: VideoState) -> VideoState:
    """Section 10.8: Generate metadata."""
    logger.info("--- Metadata Generator (Long) ---")
    return {
        "title": f"Deep Dive: {state['topic']}",
        "description": "A comprehensive look at...",
        "tags": ["AI", "Tech", state['topic']],
        "error": None
    }

def youtube_upload(state: VideoState) -> VideoState:
    """Section 10.9: Upload long-form video."""
    logger.info("--- YouTube Upload (Long) ---")
    return {"upload_status": "success", "error": None}

# --- Short Form Pipeline Nodes (Section 12) ---

def short_script_generator(state: VideoState) -> VideoState:
    """Section 12.3: Generate shorts script."""
    logger.info("--- Script Generator (Short) ---")
    return {"short_script": f"Shorts script: {state['topic']} in 60s!", "error": None}

def short_voice_generator(state: VideoState) -> VideoState:
    """Implied by 12.4: TTS for shorts."""
    logger.info("--- Voice Generator (Short) ---")
    return {"short_voice_path": "output/short_voice.mp3", "error": None}

def short_asset_generator(state: VideoState) -> VideoState:
    """Implied by 12.4: Assets for shorts."""
    logger.info("--- Asset Generator (Short) ---")
    return {"short_image_paths": ["s_img1.png", "s_img2.png"], "error": None}

def short_video_composer(state: VideoState) -> VideoState:
    """Section 12.4: Compose shorts video (9:16)."""
    logger.info("--- Video Composer (Short) ---")
    return {"short_video_path": "output/short_video.mp4", "error": None}

def short_metadata_generator(state: VideoState) -> VideoState:
    """Section 12.5: Shorts metadata."""
    logger.info("--- Metadata Generator (Short) ---")
    return {
        "short_title": f"{state['topic']} #Shorts",
        "tags": ["#Shorts", state['topic']],
        "error": None
    }

def short_youtube_upload(state: VideoState) -> VideoState:
    """Section 12.6: Upload shorts video."""
    logger.info("--- YouTube Upload (Short) ---")
    return {"short_upload_status": "success", "error": None}