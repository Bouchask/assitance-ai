import time
from typing import Callable, Any, Dict

class RetryPolicy:
    @staticmethod
    def execute_with_retry(
        func: Callable[..., Any], 
        args: tuple = (), 
        kwargs: dict = None, 
        max_retries: int = 3, 
        delay: float = 1.0, 
        is_safe_to_retry: bool = True
    ) -> Any:
        """Execute a function with retries if it's safe to retry."""
        if kwargs is None:
            kwargs = {}
            
        if not is_safe_to_retry:
            max_retries = 1
            
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                # In a real implementation we would check if the error is transient
                # For MVP, we retry any error if is_safe_to_retry is True
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    
        raise RuntimeError(f"Operation failed after {max_retries} attempts. Last error: {str(last_exception)}")
