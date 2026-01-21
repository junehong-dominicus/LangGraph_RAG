"""Publishing module for Tistory blog platform."""
import requests
from typing import Optional
from datetime import datetime
from models import BlogContent, PublishResult
from config import settings
import logging

logger = logging.getLogger(__name__)


class TistoryPublisher:
    """Publishes content to Tistory blog platform."""
    
    def __init__(self, api_key: Optional[str] = None, blog_name: Optional[str] = None):
        self.api_key = api_key or settings.tistory_api_key
        self.blog_name = blog_name or settings.tistory_blog_name
        self.base_url = "https://www.tistory.com/apis"
        
        if not self.api_key:
            logger.warning("Tistory API key not configured")
        if not self.blog_name:
            logger.warning("Tistory blog name not configured")
    
    def publish(self, content: BlogContent, visibility: str = "draft") -> PublishResult:
        """
        Publish content to Tistory.
        
        Args:
            content: Blog content to publish
            visibility: "draft" or "publish"
        
        Returns:
            PublishResult with publication status
        """
        if not self.api_key or not self.blog_name:
            return PublishResult(
                success=False,
                error_message="Tistory credentials not configured",
            )
        
        logger.info(f"Publishing to Tistory: {content.title} (mode: {visibility})")
        
        try:
            # Prepare post data
            post_data = {
                "access_token": self.api_key,
                "blogName": self.blog_name,
                "title": content.title,
                "content": content.content,
                "visibility": "0" if visibility == "draft" else "3",  # 0=draft, 3=public
                "category": content.category,
                "tag": ",".join(content.tags) if content.tags else "",
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/post/write",
                data=post_data,
                timeout=30,
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("tistory", {}).get("status") == "200":
                post_id = result["tistory"]["postId"]
                post_url = result["tistory"]["url"]
                
                logger.info(f"Successfully published: {post_url}")
                
                return PublishResult(
                    success=True,
                    post_url=post_url,
                    post_id=post_id,
                    published_at=datetime.now(),
                )
            else:
                error_msg = result.get("tistory", {}).get("error_message", "Unknown error")
                logger.error(f"Tistory API error: {error_msg}")
                return PublishResult(
                    success=False,
                    error_message=error_msg,
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error publishing to Tistory: {e}")
            return PublishResult(
                success=False,
                error_message=f"Network error: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error publishing to Tistory: {e}")
            return PublishResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
            )
    
    def update_post(self, post_id: str, content: BlogContent) -> PublishResult:
        """
        Update an existing post on Tistory.
        
        Args:
            post_id: ID of the post to update
            content: Updated content
        
        Returns:
            PublishResult with update status
        """
        if not self.api_key or not self.blog_name:
            return PublishResult(
                success=False,
                error_message="Tistory credentials not configured",
            )
        
        logger.info(f"Updating Tistory post {post_id}: {content.title}")
        
        try:
            post_data = {
                "access_token": self.api_key,
                "blogName": self.blog_name,
                "postId": post_id,
                "title": content.title,
                "content": content.content,
                "category": content.category,
                "tag": ",".join(content.tags) if content.tags else "",
            }
            
            response = requests.post(
                f"{self.base_url}/post/modify",
                data=post_data,
                timeout=30,
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("tistory", {}).get("status") == "200":
                post_url = result["tistory"]["url"]
                logger.info(f"Successfully updated: {post_url}")
                
                return PublishResult(
                    success=True,
                    post_url=post_url,
                    post_id=post_id,
                    published_at=datetime.now(),
                )
            else:
                error_msg = result.get("tistory", {}).get("error_message", "Unknown error")
                return PublishResult(
                    success=False,
                    error_message=error_msg,
                )
                
        except Exception as e:
            logger.error(f"Error updating Tistory post: {e}")
            return PublishResult(
                success=False,
                error_message=str(e),
            )


class DryRunPublisher:
    """Mock publisher for testing without actual publication."""
    
    def publish(self, content: BlogContent, visibility: str = "draft") -> PublishResult:
        """Simulate publishing."""
        logger.info(f"[DRY RUN] Would publish: {content.title}")
        logger.info(f"[DRY RUN] Mode: {visibility}")
        logger.info(f"[DRY RUN] Word count: {content.word_count}")
        logger.info(f"[DRY RUN] Tags: {', '.join(content.tags)}")
        
        return PublishResult(
            success=True,
            post_url=f"https://example.tistory.com/dry-run-{content.title[:20]}",
            post_id="dry-run-12345",
            published_at=datetime.now(),
        )
    
    def update_post(self, post_id: str, content: BlogContent) -> PublishResult:
        """Simulate updating a post."""
        logger.info(f"[DRY RUN] Would update post {post_id}: {content.title}")
        
        return PublishResult(
            success=True,
            post_url=f"https://example.tistory.com/dry-run-{post_id}",
            post_id=post_id,
            published_at=datetime.now(),
        )


def get_publisher(dry_run: bool = False) -> TistoryPublisher | DryRunPublisher:
    """Factory function to get appropriate publisher."""
    if dry_run:
        return DryRunPublisher()
    return TistoryPublisher()