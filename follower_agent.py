#!/usr/bin/env python3
"""
GitHub Follower Notification Agent

This script monitors a GitHub user's followers and sends notifications
when new followers are detected.
"""

import json
import logging
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Set, List, Dict

import requests

from config import Config


class GitHubFollowerAgent:
    def __init__(self):
        """Initialize the GitHub Follower Agent"""
        # Validate configuration
        Config.validate()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize GitHub API headers
        self.headers = {
            'Authorization': f'token {Config.GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Follower-Agent'
        }
        
        self.logger.info(f"Initialized GitHub Follower Agent for user: {Config.GITHUB_USERNAME}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_current_followers(self) -> Set[str]:
        """Fetch current followers from GitHub API"""
        followers = set()
        page = 1
        
        while True:
            url = f'https://api.github.com/users/{Config.GITHUB_USERNAME}/followers'
            params = {'page': page, 'per_page': 100}
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                if not data:  # No more followers
                    break
                
                for follower in data:
                    followers.add(follower['login'])
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching followers: {e}")
                break
        
        self.logger.info(f"Found {len(followers)} current followers")
        return followers
    
    def load_previous_followers(self) -> Set[str]:
        """Load previously stored followers from file"""
        try:
            with open(Config.FOLLOWERS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('followers', []))
        except FileNotFoundError:
            self.logger.info("No previous followers file found, starting fresh")
            return set()
        except json.JSONDecodeError:
            self.logger.error("Error reading followers file, starting fresh")
            return set()
    
    def save_followers(self, followers: Set[str]):
        """Save current followers to file"""
        data = {
            'followers': list(followers),
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(Config.FOLLOWERS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.debug(f"Saved {len(followers)} followers to file")
        except Exception as e:
            self.logger.error(f"Error saving followers: {e}")
    
    def send_email_notification(self, new_followers: List[str]):
        """Send email notification for new followers"""
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.EMAIL_FROM
            msg['To'] = Config.EMAIL_TO
            msg['Subject'] = f"🎉 New GitHub Follower{'s' if len(new_followers) > 1 else ''}!"
            
            # Create email body
            if len(new_followers) == 1:
                body = f"""
Hi there!

You have a new follower on GitHub! 🎉

👤 {new_followers[0]}
🔗 https://github.com/{new_followers[0]}

Keep up the great work!

---
GitHub Follower Agent
                """.strip()
            else:
                follower_list = '\n'.join([f"👤 {follower} - https://github.com/{follower}" for follower in new_followers])
                body = f"""
Hi there!

You have {len(new_followers)} new followers on GitHub! 🎉

{follower_list}

Keep up the great work!

---
GitHub Follower Agent
                """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(Config.EMAIL_SMTP_SERVER, Config.EMAIL_SMTP_PORT)
            server.starttls()
            server.login(Config.EMAIL_FROM, Config.EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(Config.EMAIL_FROM, Config.EMAIL_TO, text)
            server.quit()
            
            self.logger.info(f"Email notification sent for {len(new_followers)} new follower(s)")
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")
    
    def send_webhook_notification(self, new_followers: List[str]):
        """Send webhook notification for new followers"""
        try:
            payload = {
                'event': 'new_followers',
                'username': Config.GITHUB_USERNAME,
                'new_followers': new_followers,
                'count': len(new_followers),
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(Config.WEBHOOK_URL, json=payload)
            response.raise_for_status()
            
            self.logger.info(f"Webhook notification sent for {len(new_followers)} new follower(s)")
            
        except Exception as e:
            self.logger.error(f"Error sending webhook notification: {e}")
    
    def notify_new_followers(self, new_followers: List[str]):
        """Send notifications for new followers"""
        if not new_followers:
            return
        
        self.logger.info(f"Notifying about {len(new_followers)} new follower(s): {', '.join(new_followers)}")
        
        if Config.NOTIFICATION_METHOD == 'email':
            self.send_email_notification(new_followers)
        elif Config.NOTIFICATION_METHOD == 'webhook':
            self.send_webhook_notification(new_followers)
        else:
            self.logger.warning(f"Unknown notification method: {Config.NOTIFICATION_METHOD}")
    
    def check_for_new_followers(self):
        """Check for new followers and send notifications"""
        self.logger.info("Checking for new followers...")
        
        # Get current and previous followers
        current_followers = self.get_current_followers()
        previous_followers = self.load_previous_followers()
        
        # Find new followers
        new_followers = current_followers - previous_followers
        
        if new_followers:
            new_followers_list = sorted(list(new_followers))
            self.notify_new_followers(new_followers_list)
        else:
            self.logger.info("No new followers found")
        
        # Save current followers for next check
        self.save_followers(current_followers)
        
        return len(new_followers)
    
    def run_once(self):
        """Run the agent once"""
        try:
            new_count = self.check_for_new_followers()
            self.logger.info(f"Check completed. Found {new_count} new follower(s)")
            return new_count
        except Exception as e:
            self.logger.error(f"Error during follower check: {e}")
            return 0
    
    def run_continuously(self):
        """Run the agent continuously"""
        self.logger.info(f"Starting continuous monitoring (checking every {Config.CHECK_INTERVAL} seconds)")
        
        try:
            while True:
                self.run_once()
                self.logger.debug(f"Sleeping for {Config.CHECK_INTERVAL} seconds...")
                time.sleep(Config.CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            self.logger.info("Agent stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Follower Notification Agent')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--test', action='store_true', help='Test configuration and exit')
    
    args = parser.parse_args()
    
    if args.test:
        try:
            Config.validate()
            print("✅ Configuration is valid!")
            
            # Test GitHub API access
            agent = GitHubFollowerAgent()
            followers = agent.get_current_followers()
            print(f"✅ Successfully connected to GitHub API. Found {len(followers)} followers.")
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return 1
        
        return 0
    
    # Create and run agent
    agent = GitHubFollowerAgent()
    
    if args.once:
        return agent.run_once()
    else:
        agent.run_continuously()
        return 0


if __name__ == '__main__':
    exit(main())