#!/usr/bin/env python3
"""
Example usage of the GitHub Follower Agent

This script shows how to use the agent programmatically
and demonstrates different ways to run it.
"""

import os
import sys
from follower_agent import GitHubFollowerAgent

def example_one_time_check():
    """Example: Run a one-time check for new followers"""
    print("🔍 Running one-time follower check...")
    
    try:
        agent = GitHubFollowerAgent()
        new_count = agent.run_once()
        print(f"✅ Check completed. Found {new_count} new follower(s)")
        return new_count
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def example_monitor_followers():
    """Example: Monitor followers continuously"""
    print("🔄 Starting continuous follower monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        agent = GitHubFollowerAgent()
        agent.run_continuously()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def example_get_current_followers():
    """Example: Just get the current follower list"""
    print("👥 Fetching current followers...")
    
    try:
        agent = GitHubFollowerAgent()
        followers = agent.get_current_followers()
        
        print(f"📊 You have {len(followers)} followers:")
        for follower in sorted(followers):
            print(f"  • {follower} (https://github.com/{follower})")
        
        return followers
    except Exception as e:
        print(f"❌ Error: {e}")
        return set()

def main():
    """Main example runner"""
    if len(sys.argv) < 2:
        print("GitHub Follower Agent Examples")
        print("Usage: python examples.py <command>")
        print()
        print("Commands:")
        print("  check      - Run one-time check for new followers")
        print("  monitor    - Monitor followers continuously")
        print("  list       - List current followers")
        print("  help       - Show this help")
        return 1
    
    command = sys.argv[1].lower()
    
    # Check if configuration exists
    if not os.path.exists('.env'):
        print("❌ Configuration file (.env) not found!")
        print("Please copy .env.example to .env and configure your settings.")
        return 1
    
    if command == 'check':
        example_one_time_check()
    elif command == 'monitor':
        example_monitor_followers()
    elif command == 'list':
        example_get_current_followers()
    elif command == 'help':
        main()
    else:
        print(f"❌ Unknown command: {command}")
        main()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())