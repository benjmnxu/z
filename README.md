# Twitter/X Scraper for Elon Musk

A Python web scraper designed to extract tweets from a local Twitter/X instance running at `http://127.0.0.1:8080/elonmusk`. This tool extracts detailed tweet information including text content, media, statistics, quoted tweets, and metadata.

## Features

- **Comprehensive Tweet Extraction**: Extracts full tweet content, author information, timestamps, and engagement statistics
- **Media Support**: Handles images and videos with thumbnail extraction
- **Quoted Tweet Detection**: Captures quoted tweet content and metadata
- **Engagement Metrics**: Extracts likes, retweets, quotes, replies, and view counts
- **Retweet Detection**: Identifies and processes retweets with original author information
- **Pinned Tweet Recognition**: Detects pinned tweets
- **JSON Output**: Saves structured data in JSON format for easy processing

## Prerequisites

- Python 3.6+
- Local Twitter/X instance running on `http://127.0.0.1:8080`

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd z
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- `requests==2.31.0` - HTTP library for making web requests
- `beautifulsoup4==4.12.2` - HTML parsing library
- `lxml==4.9.3` - XML and HTML parser

## Usage

### Basic Usage

Run the scraper to extract tweets:

```bash
python scraper.py
```

This will:
1. Connect to `http://127.0.0.1:8080/elonmusk`
2. Extract all available tweets from the page
3. Save the data to `tweets.json`
4. Display a summary with the first 3 tweets as preview

### Programmatic Usage

```python
from scraper import ElonMuskScraper

# Initialize the scraper
scraper = ElonMuskScraper()

# Extract tweets
data = scraper.extract_tweets()

# Save to custom file
if data:
    scraper.save_tweets(data, "custom_output.json")
```

### Custom Base URL

If your local instance runs on a different URL:

```python
scraper = ElonMuskScraper(base_url="http://localhost:3000")
```

## Output Format

The scraper generates a JSON file with the following structure:

```json
{
  "url": "http://127.0.0.1:8080/elonmusk",
  "scrape_timestamp": "2025-08-22 15:50:09",
  "tweets_count": 20,
  "tweets": [
    {
      "tweet_url": "/elonmusk/status/1958846872157921546#m",
      "tweet_id": "1958846872157921546",
      "is_retweet": false,
      "is_pinned": true,
      "author": "Elon Musk",
      "username": "@elonmusk",
      "date": "11h",
      "full_date": "Aug 22, 2025 · 11:01 AM UTC",
      "text": "Tweet content here...",
      "quoted_tweet": {
        "author": "Quoted Author",
        "username": "@quoted_user",
        "date": "21h",
        "text": "Quoted tweet content...",
        "link": "/quoted_user/status/123456789#m"
      },
      "media": [
        {
          "type": "image",
          "src": "/pic/image_path.jpg",
          "alt": "Alt text"
        }
      ],
      "stats": {
        "replies": "2856",
        "retweets": "2962",
        "quotes": "238",
        "likes": "20082"
      }
    }
  ]
}
```

## Data Fields

### Tweet Object
- `tweet_url`: Relative URL to the tweet
- `tweet_id`: Unique tweet identifier
- `is_retweet`: Boolean indicating if this is a retweet
- `is_pinned`: Boolean indicating if this tweet is pinned
- `author`: Display name of the tweet author
- `username`: Twitter handle (e.g., @elonmusk)
- `date`: Relative timestamp (e.g., "11h", "3m")
- `full_date`: Full timestamp with timezone
- `text`: Tweet content text
- `retweet_info`: Information about original tweet if this is a retweet
- `quoted_tweet`: Object containing quoted tweet details (if applicable)
- `media`: Array of media objects (images, videos)
- `stats`: Engagement statistics object

### Media Object
- `type`: "image" or "video"
- `src`: Source URL for images
- `thumbnail`: Thumbnail URL for videos
- `alt`: Alt text for accessibility

### Statistics Object
- `replies`: Number of replies
- `retweets`: Number of retweets
- `quotes`: Number of quote tweets
- `likes`: Number of likes
- `views`: Number of views (when available)

## Error Handling

The scraper includes comprehensive error handling:
- Network timeout protection (10 seconds)
- HTTP status code validation
- JSON serialization error handling
- Graceful failure with error messages

## Limitations

- Requires a local Twitter/X instance running on the specified URL
- Designed specifically for the HTML structure of the target instance
- Single-page scraping (does not handle pagination)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is intended for educational and research purposes. Please ensure compliance with Twitter's Terms of Service and applicable laws when using this tool.

## Disclaimer

This scraper is designed for use with local instances and educational purposes. Users are responsible for ensuring their usage complies with all applicable terms of service and legal requirements.
