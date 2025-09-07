# Twitter Scraper Email Setup Guide

This guide walks you through setting up email notifications for important tweets.

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key (choose one)
```bash
# For GPT-4o-mini (default, cheapest)
export OPENAI_API_KEY="sk-your-openai-key-here"

# For Claude 3.5 Haiku (better reasoning)  
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
```

### 3. Configure Email (Interactive)
```bash
python setup_email.py
```

### 4. Run with Email Notifications
```bash
python run_with_email.py
```

## Manual Email Configuration

If you prefer to set up email manually:

### Gmail Setup (Recommended)
1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and generate a 16-character app password
3. **Set Environment Variables**:
   ```bash
   export EMAIL_USER="your-email@gmail.com"
   export EMAIL_PASSWORD="your-16-char-app-password"
   export RECIPIENT_EMAIL="where-to-send@email.com"
   ```

### Outlook/Hotmail Setup
1. **Enable 2-Factor Authentication**
2. **Generate App Password** in security settings
3. **Set Environment Variables**:
   ```bash
   export EMAIL_USER="your-email@outlook.com"
   export EMAIL_PASSWORD="your-app-password"
   export RECIPIENT_EMAIL="where-to-send@email.com"
   export SMTP_SERVER="smtp-mail.outlook.com"
   export SMTP_PORT="587"
   ```

### Yahoo Mail Setup
1. **Enable 2-Factor Authentication**
2. **Generate App Password** in account security
3. **Set Environment Variables**:
   ```bash
   export EMAIL_USER="your-email@yahoo.com"
   export EMAIL_PASSWORD="your-app-password"
   export RECIPIENT_EMAIL="where-to-send@email.com"
   export SMTP_SERVER="smtp.mail.yahoo.com"
   export SMTP_PORT="587"
   ```

## Email Notification Settings

### Importance Thresholds
- **Score 8+**: High-priority tweets that trigger immediate email alerts
- **Score 6-7**: Important tweets shown in console but no email
- **Score 1-5**: Low-priority tweets filtered out

### Notification Types
1. **Individual Alerts**: Immediate email for tweets scoring 8+
2. **Batch Summary**: Summary email after multi-handle scraping

### Per-Handle Configuration
Edit `config.py` to customize thresholds:
```python
HANDLES_CONFIG = {
    "elonmusk": {
        "min_score": 6,
        "context": "Elon Musk tech/business content"
    },
    "naval": {
        "min_score": 8,  # Very selective
        "context": "Naval Ravikant investing/philosophy content"
    }
}
```

## Testing Email Setup

### Test Current Configuration
```bash
python setup_email.py test
```

### Send Test Email
```bash
python -c "
from email_notifier import EmailNotifier
notifier = EmailNotifier()
test_tweet = {
    'importance_score': 9,
    'importance_reason': 'Test notification',
    'author': 'Test User',
    'username': '@test',
    'text': 'This is a test email!',
    'stats': {'likes': '100', 'retweets': '50'}
}
notifier.send_tweet_notification(test_tweet, 'test')
"
```

## Running the Scraper

### With Email Notifications
```bash
python run_with_email.py
```

### Standard Mode (No Email)
```bash
python main.py
```

### Single Handle
```bash
python -c "
from main import scrape_single_handle
result = scrape_single_handle('elonmusk', ai_provider='gpt', min_score=7)
"
```

## Troubleshooting

### Common Issues

**Email Authentication Failed**
- Verify 2-factor authentication is enabled
- Use app passwords, not regular passwords
- Check SMTP server settings

**No Tweets Found**
- Verify local Twitter instance is running on `http://127.0.0.1:8080`
- Check handle names are correct (without @ symbol)

**AI Classification Not Working**
- Verify API keys are set correctly
- Check API quotas and billing
- System falls back to keyword classification if AI fails

**Deduplication Issues**
- Check `seen_tweets.json` file permissions
- Verify tweet IDs are being extracted correctly

### Error Messages

**"Email not configured"**
- Run `python setup_email.py` to configure
- Set required environment variables manually

**"Email connection failed"**
- Verify SMTP credentials and server settings
- Check firewall/network restrictions

**"No important tweets found"**
- Lower importance thresholds in `config.py`
- Verify AI classification is working

## Cost Estimation

### AI Classification Costs (per handle, ~600 tweets/month)
- **GPT-4o-mini**: ~$0.014/month
- **Claude 3.5 Haiku**: ~$0.023/month

### For 5 Handles
- **Total cost**: ~$0.07-0.12/month

## Configuration Files

- `config.py` - Handle settings and thresholds
- `seen_tweets.json` - Deduplication tracking (auto-created)
- `.env_email` - Email configuration (created by setup script)

## Advanced Usage

### Custom Handle Configuration
```python
custom_config = {
    "username": {
        "min_score": 7,
        "context": "Specific context for AI classification"
    }
}

scraper = TwitterScraper(
    handles_config=custom_config,
    ai_provider="claude",
    enable_email_notifications=True,
    email_min_score=8
)
```

### AI Provider Switching
```python
# Use Claude for better reasoning
scraper = TwitterScraper(ai_provider="claude")

# Use GPT for cost efficiency
scraper = TwitterScraper(ai_provider="gpt")
```

### Batch Processing
```python
# Multi-handle scraping with email
data = scraper.extract_tweets_from_multiple_handles()

# Process results
if data['stats']['total_important_tweets'] > 0:
    scraper.save_tweets(data)
    scraper.print_results_summary(data)
```