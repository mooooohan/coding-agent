class Config:
    """Flask app configuration"""
    SECRET_KEY = 'your-secret-key-here'  # For session management
    DEBUG = True  # Enable debug mode for development
    JSON_AS_ASCII = False  # Allow non-ASCII characters in JSON responses
    PAPERS_JSON_PATH = 'papers.json'  # Path to the papers JSON file