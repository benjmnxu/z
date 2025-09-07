#!/usr/bin/env python3

import os
import getpass
from email_notifier import EmailNotifier, setup_gmail_instructions


def setup_email_config():
    """Interactive setup for email notifications"""
    print("📧 TWITTER SCRAPER EMAIL SETUP")
    print("="*50)
    
    if os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASSWORD') and os.getenv('RECIPIENT_EMAIL'):
        print("✅ Email already configured!")
        print(f"From: {os.getenv('EMAIL_USER')}")
        print(f"To: {os.getenv('RECIPIENT_EMAIL')}")
        
        test = input("Test email configuration? (y/n): ").lower().strip()
        if test == 'y':
            notifier = EmailNotifier()
            notifier.test_email_connection()
        return
    
    print("Setting up email notifications for important tweets...")
    print()
    
    print("Choose your email provider:")
    print("1. Gmail (recommended)")
    print("2. Outlook/Hotmail")
    print("3. Yahoo Mail")
    print("4. Other")
    
    choice = input("Enter choice (1-4): ").strip()
    
    smtp_configs = {
        '1': ('smtp.gmail.com', 587),
        '2': ('smtp-mail.outlook.com', 587),
        '3': ('smtp.mail.yahoo.com', 587),
        '4': (None, 587)
    }
    
    smtp_server, smtp_port = smtp_configs.get(choice, ('smtp.gmail.com', 587))
    
    if choice == '4':
        smtp_server = input("Enter SMTP server: ").strip()
        smtp_port = int(input("Enter SMTP port (587): ").strip() or "587")
    
    print("\nEmail Configuration:")
    email_user = input("Your email address: ").strip()
    
    if choice == '1':  # Gmail
        print("\n⚠️  IMPORTANT: For Gmail, you need an 'App Password', not your regular password!")
        print("   1. Enable 2-factor authentication on your Google account")
        print("   2. Go to https://myaccount.google.com/apppasswords")
        print("   3. Generate an app password for 'Mail'")
        print("   4. Use that 16-character password below")
        print()
    
    email_password = getpass.getpass("Email password (or app password): ")
    recipient_email = input("Send notifications to (email): ").strip() or email_user
    
    print("\nNotification Settings:")
    min_score = input("Minimum importance score for email (8): ").strip() or "8"
    
    env_vars = f"""
# Add these to your shell profile (.bashrc, .zshrc, etc.)
export EMAIL_USER="{email_user}"
export EMAIL_PASSWORD="{email_password}"
export RECIPIENT_EMAIL="{recipient_email}"
export SMTP_SERVER="{smtp_server}"
export SMTP_PORT="{smtp_port}"
export EMAIL_MIN_SCORE="{min_score}"
"""
    
    print("\n🧪 Testing email configuration...")
    
    os.environ['EMAIL_USER'] = email_user
    os.environ['EMAIL_PASSWORD'] = email_password
    os.environ['RECIPIENT_EMAIL'] = recipient_email
    os.environ['SMTP_SERVER'] = smtp_server
    os.environ['SMTP_PORT'] = str(smtp_port)
    
    notifier = EmailNotifier(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        email_user=email_user,
        email_password=email_password,
        recipient_email=recipient_email,
        min_score_for_email=int(min_score)
    )
    
    if notifier.test_email_connection():
        print("\n✅ Email configuration successful!")
        
        send_test = input("Send test notification? (y/n): ").lower().strip()
        if send_test == 'y':
            test_tweet = {
                'importance_score': 9,
                'importance_reason': 'Test notification',
                'author': 'Twitter Scraper',
                'username': '@test',
                'date': 'now',
                'text': 'This is a test notification from your Twitter scraper setup!',
                'stats': {'likes': '100', 'retweets': '50'},
                'ai_provider': 'test'
            }
            
            if notifier.send_tweet_notification(test_tweet, 'test'):
                print("✅ Test email sent successfully!")
            else:
                print("❌ Test email failed")
        
        print("\n📝 CONFIGURATION SETUP:")
        print(env_vars)
        
        with open('.env_email', 'w') as f:
            f.write(env_vars.strip())
        
        print("Configuration saved to .env_email")
        print("\nTo use permanently:")
        print("1. Add the export commands to your shell profile (~/.bashrc or ~/.zshrc)")
        print("2. Or run: source .env_email")
        print("3. Restart your terminal or run: source ~/.bashrc")
        
    else:
        print("\n❌ Email configuration failed!")
        if choice == '1':
            print("\nFor Gmail troubleshooting:")
            setup_gmail_instructions()


def test_current_config():
    """Test current email configuration"""
    print("🧪 Testing current email configuration...")
    
    notifier = EmailNotifier()
    if notifier.test_email_connection():
        test_tweet = {
            'importance_score': 9,
            'importance_reason': 'Configuration test',
            'author': 'Test User',
            'username': '@test',
            'date': 'now',
            'text': 'Testing email notifications for Twitter scraper. If you receive this, email setup is working correctly!',
            'stats': {'likes': '42', 'retweets': '13'},
            'ai_provider': 'test'
        }
        
        if notifier.send_tweet_notification(test_tweet, 'test'):
            print("✅ Test notification sent! Check your email.")
        else:
            print("❌ Failed to send test notification")
    else:
        print("❌ Email configuration is not working")


def main():
    """Main setup menu"""
    if len(os.sys.argv) > 1 and os.sys.argv[1] == 'test':
        test_current_config()
        return
    
    print("📧 Twitter Scraper Email Setup")
    print("1. Setup email notifications")
    print("2. Test current configuration")
    print("3. View Gmail setup instructions")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == '1':
        setup_email_config()
    elif choice == '2':
        test_current_config()
    elif choice == '3':
        setup_gmail_instructions()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()