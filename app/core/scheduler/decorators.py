"""
Decorators untuk job registration (future enhancement).
Saat ini menggunakan explicit registration via manager.
"""

from typing import List
from app.core.scheduler.base import BaseScheduledJob

# Registry untuk auto-discovery
_job_registry: List[BaseScheduledJob] = []


def register_job(job_class: type):
    """
    Decorator untuk auto-register job class.
    
    Usage:
        @register_job
        class MyJob(BaseScheduledJob):
            job_id = "my_job"
            ...
    """
    if not issubclass(job_class, BaseScheduledJob):
        raise TypeError(f"{job_class} harus inherit dari BaseScheduledJob")
    
    # Instantiate dan tambahkan ke registry
    job_instance = job_class()
    _job_registry.append(job_instance)
    
    return job_class


def get_registered_jobs() -> List[BaseScheduledJob]:
    """
    Get semua jobs yang sudah di-register via decorator.
    
    Returns:
        List of job instances
    """
    return _job_registry.copy()


def clear_registry():
    """Clear job registry (untuk testing)"""
    _job_registry.clear()
