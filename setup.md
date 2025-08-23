# Multi-Handle AI Tweet Scraper Setup

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up API keys (choose one or both):

### For GPT-4o-mini (default, cheapest):
```bash
export OPENAI_API_KEY="sk-your-openai-key-here"
```

### For Claude 3.5 Haiku (better reasoning):
```bash  
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
```

## Usage Examples

### Multi-Handle Setup (Default):
```python
from scraper import TwitterScraper

handles_config = {
    "elonmusk": {
        "min_score": 6,
        "context": "Elon Musk tech/business content (Tesla, SpaceX, xAI)"
    },
    "sama": {
        "min_score": 7,  # Higher threshold
        "context": "Sam Altman content (OpenAI, AI development)"
    }
}

scraper = TwitterScraper(
    ai_classification=True,
    ai_provider="gpt",
    handles_config=handles_config
)

# Scrape all configured handles
data = scraper.extract_tweets_from_multiple_handles()
```

### Single Handle:
```python
from scraper import scrape_single_handle

data = scrape_single_handle(
    handle="elonmusk",
    ai_provider="claude",
    min_score=7
)
```

### Custom Handle Selection:
```python
# Only scrape specific handles from config
data = scraper.extract_tweets_from_multiple_handles(["elonmusk", "sama"])
```

### Switch AI Provider:
```python
scraper = TwitterScraper(
    ai_classification=True,
    ai_provider="claude",     # Use Claude instead of GPT
    handles_config=handles_config
)
```

### Disable AI (Free):
```python
scraper = TwitterScraper(
    ai_classification=False,  # No AI costs, keyword-based only
    handles_config=handles_config
)
```

## Handle Configuration

Each handle can have individual settings:

```python
handles_config = {
    "handle_name": {
        "min_score": 6,           # 1-10 importance threshold
        "context": "Description"   # AI context for classification
    }
}
```

### Example Configurations:

```python
handles_config = {
    "elonmusk": {
        "min_score": 6,
        "context": "Elon Musk tech/business (Tesla, SpaceX, xAI, major announcements)"
    },
    "naval": {
        "min_score": 8,  # Very selective
        "context": "Naval Ravikant (startups, investing, philosophy)"
    },
    "karpathy": {
        "min_score": 6,
        "context": "Andrej Karpathy (AI research, machine learning insights)"
    }
}
```

## Configuration Options

| Parameter | Options | Description |
|-----------|---------|-------------|
| `ai_classification` | `True`/`False` | Enable AI vs keyword-based |
| `ai_provider` | `"gpt"`/`"claude"` | Which AI API to use |
| `handles_config` | `dict` | Per-handle settings |

## Cost Estimates

Per handle, ~600 tweets/month:
- **GPT-4o-mini**: ~$0.014/month per handle
- **Claude 3.5 Haiku**: ~$0.023/month per handle  
- **Keyword-based**: Free

For 5 handles:
- **GPT**: ~$0.07/month
- **Claude**: ~$0.12/month

## Output Files

- `tweets_multi_handle.json` - Combined results from all handles
- `seen_tweets.json` - Tracking file to avoid duplicates

## Quick Start

Run interactive examples:
```bash
python config_example.py
```

Or run default multi-handle scraper:
```bash
python scraper.py
```