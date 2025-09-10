import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # GitHub settings
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
    
    # Notification settings
    NOTIFICATION_METHOD = os.getenv('NOTIFICATION_METHOD', 'email')
    
    # Email settings
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_TO = os.getenv('EMAIL_TO')
    
    # Webhook settings
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    
    # Agent settings
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # File paths
    FOLLOWERS_FILE = 'followers.json'
    LOG_FILE = 'follower_agent.log'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN is required")
        
        if not cls.GITHUB_USERNAME:
            errors.append("GITHUB_USERNAME is required")
        
        if cls.NOTIFICATION_METHOD == 'email':
            if not cls.EMAIL_FROM or not cls.EMAIL_PASSWORD or not cls.EMAIL_TO:
                errors.append("Email configuration incomplete (EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO required)")
        
        elif cls.NOTIFICATION_METHOD == 'webhook':
            if not cls.WEBHOOK_URL:
                errors.append("WEBHOOK_URL is required for webhook notifications")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"- {error}" for error in errors))
        
        return True