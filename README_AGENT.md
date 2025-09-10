# GitHub Follower Notification Agent

A lightweight Python agent that monitors your GitHub followers and sends notifications when someone new follows you.

## Features

- 🔍 **Automatic Monitoring**: Continuously checks for new followers using GitHub API
- 📧 **Email Notifications**: Send email alerts when new followers are detected
- 🔗 **Webhook Support**: Alternative webhook notifications for integration with other services
- 📊 **Follower Tracking**: Maintains persistent storage of follower history
- ⚙️ **Configurable**: Flexible configuration through environment variables
- 📝 **Logging**: Comprehensive logging with configurable levels
- 🚀 **Easy Setup**: Simple configuration and deployment

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Required: GitHub credentials
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username

# Required: Notification method (email or webhook)
NOTIFICATION_METHOD=email

# For email notifications
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=your_email@gmail.com
```

### 3. Test Configuration

```bash
python follower_agent.py --test
```

### 4. Run the Agent

**Run once:**
```bash
python follower_agent.py --once
```

**Run continuously:**
```bash
python follower_agent.py
```

## Configuration

### GitHub Setup

1. **Create a Personal Access Token:**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `read:user` scope
   - Copy the token to your `.env` file

2. **Set your username:**
   - Add your GitHub username to `GITHUB_USERNAME` in `.env`

### Email Notifications

For Gmail (recommended):

1. **Enable 2-Factor Authentication** on your Google account
2. **Create an App Password:**
   - Go to Google Account settings → Security → App passwords
   - Generate a new app password for "Mail"
   - Use this app password (not your regular password) in `EMAIL_PASSWORD`

3. **Configure SMTP settings:**
   ```env
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_FROM=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_TO=your_email@gmail.com
   ```

### Webhook Notifications

To use webhooks instead of email:

```env
NOTIFICATION_METHOD=webhook
WEBHOOK_URL=https://your-webhook-endpoint.com/notify
```

The webhook will receive a POST request with this payload:
```json
{
  "event": "new_followers",
  "username": "your_username",
  "new_followers": ["follower1", "follower2"],
  "count": 2,
  "timestamp": "2023-12-07T10:30:00"
}
```

## Advanced Configuration

### Agent Settings

```env
CHECK_INTERVAL=300    # Check every 5 minutes (300 seconds)
LOG_LEVEL=INFO        # Logging level: DEBUG, INFO, WARNING, ERROR
```

### Running as a Service

**Using systemd (Linux):**

1. Create a service file `/etc/systemd/system/github-follower-agent.service`:

```ini
[Unit]
Description=GitHub Follower Notification Agent
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/your/agent
ExecStart=/usr/bin/python3 /path/to/your/agent/follower_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:

```bash
sudo systemctl enable github-follower-agent
sudo systemctl start github-follower-agent
```

**Using cron (alternative):**

Add to your crontab to run every 5 minutes:

```cron
*/5 * * * * cd /path/to/your/agent && python3 follower_agent.py --once
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "follower_agent.py"]
```

Build and run:

```bash
docker build -t github-follower-agent .
docker run -d --name follower-agent --env-file .env github-follower-agent
```

## Usage Examples

### Check Configuration
```bash
python follower_agent.py --test
```

### Run Once (for testing)
```bash
python follower_agent.py --once
```

### Run Continuously
```bash
python follower_agent.py
```

### View Logs
```bash
tail -f follower_agent.log
```

## Troubleshooting

### Common Issues

**"Configuration errors: GITHUB_TOKEN is required"**
- Make sure you've created a `.env` file with your GitHub token

**"Error fetching followers: 401 Client Error"**
- Check that your GitHub token is valid and has the correct permissions

**"Error sending email notification"**
- Verify your email credentials and app password
- Check that 2FA is enabled and you're using an app password (not your regular password)

**"No new followers found" (when you expect new followers)**
- The agent tracks followers in `followers.json` - delete this file to reset tracking
- Check that your GitHub username is correct

### Debug Mode

Run with debug logging to see detailed information:

```bash
# Set LOG_LEVEL=DEBUG in .env, then run:
python follower_agent.py --once
```

### Reset Follower Tracking

To start fresh and re-detect all followers:

```bash
rm followers.json
python follower_agent.py --once
```

## Files Created

- `followers.json` - Stores current follower list (auto-created)
- `follower_agent.log` - Log file with agent activity
- `.env` - Your configuration file (create from `.env.example`)

## Security Notes

- Never commit your `.env` file to version control
- Use app passwords instead of regular passwords for email
- Store your GitHub token securely
- The agent only needs `read:user` scope for GitHub API access

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `python follower_agent.py --test` to validate configuration
3. Check the log file `follower_agent.log` for detailed error messages
4. Ensure all required environment variables are set in `.env`