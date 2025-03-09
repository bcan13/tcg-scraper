import random
import string

def generate_random_yopmail() -> str:
    """Generate a random yopmail address."""
    # Generate random string of 10 characters
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{random_string}@yopmail.com"