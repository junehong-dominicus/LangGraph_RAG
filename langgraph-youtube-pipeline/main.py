import logging
from .graph import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Example 1: Long form default
    logger.info(">>> Running Pipeline: Long Form")
    initial_state = {"topic": "The History of Computing", "retry_count": 0}
    app.invoke(initial_state)
    
    print("\n" + "="*50 + "\n")

    # Example 2: Both (Parallel)
    logger.info(">>> Running Pipeline: Both (Short + Long)")
    # Trigger 'both' logic via topic keyword defined in content_type_router
    initial_state_both = {"topic": "AI Trends 2024 (Both)", "retry_count": 0}
    app.invoke(initial_state_both)