"""
these functions are used by the "Home" page of the website
and the associated route in the views.py file
"""
from project.utils.configure import configure_redis

def get_startup_status() -> str:
    """
    Returns the start status of celery. 
    This status is displayed on the "Home" page, to indicates errors during startup.
    """
    redis = configure_redis()
    return redis.hgetall('startup_status')

