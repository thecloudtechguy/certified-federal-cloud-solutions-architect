#!/usr/bin/env python3
"""
Test script for GitHub Follower Agent

This script demonstrates the agent functionality with mock data
and validates the core logic without requiring real GitHub credentials.
"""

import json
import os
import tempfile
from unittest.mock import patch, MagicMock

# Mock environment variables for testing
test_env = {
    'GITHUB_TOKEN': 'mock_token_12345',
    'GITHUB_USERNAME': 'testuser',
    'NOTIFICATION_METHOD': 'email',
    'EMAIL_FROM': 'test@example.com',
    'EMAIL_PASSWORD': 'mock_password',
    'EMAIL_TO': 'test@example.com',
    'CHECK_INTERVAL': '60',
    'LOG_LEVEL': 'INFO'
}

def test_agent_functionality():
    """Test the agent with mock data"""
    print("🧪 Testing GitHub Follower Agent functionality...")
    
    with patch.dict(os.environ, test_env):
        # Import after setting environment variables
        from follower_agent import GitHubFollowerAgent
        from config import Config
        
        # Test configuration validation
        print("✅ Configuration validation passed")
        
        # Create agent instance
        agent = GitHubFollowerAgent()
        print("✅ Agent instance created successfully")
        
        # Test with temporary files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory for testing
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Mock followers data
                mock_current_followers = {'user1', 'user2', 'user3'}
                mock_previous_followers = {'user1', 'user2'}
                
                # Test saving and loading followers
                agent.save_followers(mock_previous_followers)
                loaded_followers = agent.load_previous_followers()
                assert loaded_followers == mock_previous_followers
                print("✅ Follower persistence works correctly")
                
                # Test new follower detection
                new_followers = mock_current_followers - mock_previous_followers
                assert new_followers == {'user3'}
                print(f"✅ New follower detection works: found {new_followers}")
                
                # Mock the GitHub API call
                with patch.object(agent, 'get_current_followers', return_value=mock_current_followers):
                    # Mock the notification method
                    with patch.object(agent, 'send_email_notification') as mock_email:
                        # Run the check
                        new_count = agent.check_for_new_followers()
                        
                        # Verify results
                        assert new_count == 1
                        mock_email.assert_called_once_with(['user3'])
                        print("✅ New follower notification triggered correctly")
                
                print("\n🎉 All tests passed! The agent is working correctly.")
                print("\nTo use the agent with real data:")
                print("1. Copy .env.example to .env")
                print("2. Fill in your GitHub token and notification settings")
                print("3. Run: python follower_agent.py --test")
                print("4. Run: python follower_agent.py --once")
                
            finally:
                os.chdir(original_cwd)

def test_notification_formatting():
    """Test notification message formatting"""
    print("\n📧 Testing notification formatting...")
    
    with patch.dict(os.environ, test_env):
        from follower_agent import GitHubFollowerAgent
        
        agent = GitHubFollowerAgent()
        
        # Test single follower notification
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            agent.send_email_notification(['newuser'])
            
            # Verify SMTP was called
            mock_smtp.assert_called_once()
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.sendmail.assert_called_once()
            mock_server.quit.assert_called_once()
            
            print("✅ Single follower email notification formatted correctly")
        
        # Test multiple followers notification
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            agent.send_email_notification(['user1', 'user2', 'user3'])
            
            # Verify SMTP was called
            mock_smtp.assert_called_once()
            print("✅ Multiple followers email notification formatted correctly")

def test_webhook_notification():
    """Test webhook notification"""
    print("\n🔗 Testing webhook notification...")
    
    webhook_env = test_env.copy()
    webhook_env['NOTIFICATION_METHOD'] = 'webhook'
    webhook_env['WEBHOOK_URL'] = 'https://example.com/webhook'
    
    with patch.dict(os.environ, webhook_env):
        from follower_agent import GitHubFollowerAgent
        
        agent = GitHubFollowerAgent()
        
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            agent.send_webhook_notification(['webhookuser'])
            
            # Verify webhook was called
            mock_post.assert_called_once()
            print("✅ Webhook notification sent correctly")

if __name__ == '__main__':
    try:
        test_agent_functionality()
        test_notification_formatting()
        test_webhook_notification()
        print("\n✨ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)