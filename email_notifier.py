#!/usr/bin/env python3

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    
    def __init__(self, smtp_server=None, smtp_port=587, email_user=None, email_password=None, 
                 recipient_email=None, min_score_for_email=8):
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port
        self.email_user = email_user or os.getenv('EMAIL_USER')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
        self.recipient_email = recipient_email or os.getenv('RECIPIENT_EMAIL')
        self.min_score_for_email = min_score_for_email
        self.is_configured = all([
            self.email_user, 
            self.email_password, 
            self.recipient_email
        ])
        
        if not self.is_configured:
            print("⚠️ Email notifications not configured. Set EMAIL_USER, EMAIL_PASSWORD, RECIPIENT_EMAIL environment variables.")
    
    def send_tweet_notification(self, tweet, handle):
        if not self.is_configured:
            return False
        
        score = tweet.get('importance_score', 0)
        if score < self.min_score_for_email:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.recipient_email
            msg['Subject'] = f"🚨 Important Tweet from @{handle} (Score: {score}/10)"
            
            body = self._create_tweet_email_body(tweet, handle)
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"📧 Email sent for tweet from @{handle} (Score: {score})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_batch_notification(self, tweets_by_handle, total_important):
        if not self.is_configured or total_important == 0:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.recipient_email
            msg['Subject'] = f"📊 Twitter Digest: {total_important} Important Tweets"
            
            body = self._create_batch_email_body(tweets_by_handle, total_important)
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"📧 Batch email sent for {total_important} important tweets")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send batch email: {e}")
            return False
    
    def _create_tweet_email_body(self, tweet, handle):
        score = tweet.get('importance_score', 0)
        reason = tweet.get('importance_reason', 'Unknown')
        author = tweet.get('author', 'Unknown')
        username = tweet.get('username', f'@{handle}')
        date = tweet.get('date', 'Unknown')
        text = tweet.get('text', 'No text available')
        tweet_url = tweet.get('tweet_url', '')
        
        body = f"""🚨 IMPORTANT TWEET ALERT 🚨

Handle: @{handle}
Author: {author} ({username})
Importance Score: {score}/10
Reason: {reason}
Date: {date}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Tweet Content:
{text}

"""
        if tweet.get('quoted_tweet'):
            quoted = tweet['quoted_tweet']
            body += f"""
Quoted Tweet:
From: {quoted.get('author', 'Unknown')} ({quoted.get('username', 'Unknown')})
"{quoted.get('text', 'No text')}"
"""
        if tweet.get('media'):
            media_count = len(tweet['media'])
            media_types = [m.get('type', 'unknown') for m in tweet['media']]
            body += f"\nMedia: {media_count} attachments ({', '.join(set(media_types))})"
        stats = tweet.get('stats', {})
        if any(stats.values()):
            body += f"""
Engagement:
- Likes: {stats.get('likes', 'N/A')}
- Retweets: {stats.get('retweets', 'N/A')}
- Replies: {stats.get('replies', 'N/A')}
"""
        
        body += f"""
--
AI Twitter Scraper
Powered by {tweet.get('ai_provider', 'keyword')} classification
"""
        
        return body
    
    def _create_batch_email_body(self, tweets_by_handle, total_important):
        body = f"""📊 TWITTER DIGEST REPORT

Total Important Tweets: {total_important}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        for handle, tweets in tweets_by_handle.items():
            if not tweets:
                continue
                
            body += f"""
                    {'='*50}
                    @{handle.upper()} ({len(tweets)} important tweets)
                    {'='*50}

                    """
            sorted_tweets = sorted(tweets, key=lambda x: x.get('importance_score', 0), reverse=True)
            
            for i, tweet in enumerate(sorted_tweets):
                score = tweet.get('importance_score', 0)
                reason = tweet.get('importance_reason', 'Unknown')
                author = tweet.get('author', 'Unknown')
                date = tweet.get('full_date') or tweet.get('date') or 'Unknown date'
                text = tweet.get('text', 'No text available')
                urls = tweet.get('urls', [])
                
                body += f"""
                    {i+1}. [{score}/10] {reason}
                    Author: {author}
                    Date: {date}
                    Text: {text[:1000]}{'...' if len(text) > 1000 else ''}
                    """
                if urls:
                    body += f"URLs: {', '.join(urls)}\n"
        
        body += """
                --
                AI Twitter Scraper - Batch Notification
                Configure notification settings in email_notifier.py
                """
        
        return body
    
    def test_email_connection(self):
        if not self.is_configured:
            print("❌ Email not configured. Set EMAIL_USER, EMAIL_PASSWORD, RECIPIENT_EMAIL environment variables.")
            return False
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
            
            print("✅ Email configuration is working!")
            return True
            
        except Exception as e:
            print(f"❌ Email configuration failed: {e}")
            print("\nTroubleshooting tips:")
            print("- For Gmail, use an 'App Password' instead of your regular password")
            print("- Enable 2-factor authentication and generate an app-specific password")
            print("- Check that EMAIL_USER, EMAIL_PASSWORD, RECIPIENT_EMAIL are set correctly")
            return False


def setup_gmail_instructions():
    print("""
📧 GMAIL SETUP INSTRUCTIONS

1. Enable 2-Factor Authentication on your Google account:
   - Go to https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select 'Mail' as the app
   - Copy the generated 16-character password

3. Set environment variables:
   export EMAIL_USER="your-email@gmail.com"
   export EMAIL_PASSWORD="your-16-char-app-password"  
   export RECIPIENT_EMAIL="where-to-send@email.com"

4. Test the configuration:
   python -c "from email_notifier import EmailNotifier; EmailNotifier().test_email_connection()"

For other email providers, update SMTP_SERVER:
- Outlook: smtp-mail.outlook.com
- Yahoo: smtp.mail.yahoo.com
""")


if __name__ == "__main__":
    setup_gmail_instructions()