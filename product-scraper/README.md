# Product Scraper

Distributed web scraper for e-commerce product data with anti-bot measures and JavaScript rendering support.

## Features

- **JavaScript Rendering**: Handles dynamic content with Puppeteer
- **Anti-Bot Measures**: Proxy rotation, user agent management, rate limiting
- **Distributed Architecture**: Redis coordination for multiple workers
- **Data Normalization**: Converts raw HTML to structured JSON/CSV
- **Error Recovery**: Automatic retry logic and CAPTCHA handling
- **Scheduled Execution**: Supports cron-based scraping schedules
- **Monitoring**: Real-time progress tracking and logging

## Tech Stack

- Python 3.9+
- Scrapy (web scraping framework)
- Puppeteer (JavaScript rendering)
- Redis (distributed coordination)
- PostgreSQL (data storage)
- Docker (containerization)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start Redis and PostgreSQL:
```bash
docker-compose up -d
```

4. Run the scraper:
```bash
scrapy crawl products
```

## Architecture

```
Scheduler → Redis Queue → Scrapy Spiders → Puppeteer → PostgreSQL
                    ↓              ↓
              Proxy Rotation  Data Normalization
```

## Anti-Bot Features

- Rotating user agents (mobile/desktop/tablet)
- Proxy rotation with geolocation targeting
- Request throttling and rate limiting
- Browser fingerprinting avoidance
- CAPTCHA detection and handling
- Cookie and session management

## Data Output

Scraped data is stored in PostgreSQL with the following schema:
- Product ID, name, price, availability
- Product images and descriptions
- Category and brand information
- Timestamp and source URL
- Raw HTML for reference

## Configuration

Configure scraping behavior in `settings.py`:
- `CONCURRENT_REQUESTS`: Number of parallel requests
- `DOWNLOAD_DELAY`: Delay between requests
- `PROXY_LIST`: List of proxy servers
- `USER_AGENTS`: List of user agent strings
- `RETRY_TIMES`: Number of retry attempts

## Docker Deployment

```bash
docker-compose up -d
```

## Monitoring

Check scraping progress:
```bash
redis-cli llen scrape_queue
```

View logs:
```bash
docker-compose logs -f scraper
```

## License

MIT