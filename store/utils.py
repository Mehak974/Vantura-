"""
Store Utility Functions
"""
import re

def is_garbage(value):
    """
    Checks if a string value is 'garbage' (too short, or contains no letters).
    """
    if not value or len(value.strip()) < 2:
        return True
    
    # Check if it contains at least one letter
    if not re.search(r'[a-zA-Z]', value):
        return True
        
    return False
