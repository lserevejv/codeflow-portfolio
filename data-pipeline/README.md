# Financial Data Pipeline

Automated data pipeline for financial API integration and processing using AWS serverless architecture.

## Features

- **Multi-API Integration**: Ingests data from Alpha Vantage, Yahoo Finance, and custom APIs
- **Serverless Processing**: AWS Lambda for cost-effective, scalable processing
- **Data Transformation**: Normalizes and enriches financial data
- **Automated Scheduling**: CloudWatch Events for scheduled execution
- **Error Handling**: Comprehensive error tracking and retry logic
- **Monitoring**: CloudWatch metrics and logs
- **Storage**: S3 for raw data, Redshift for analytics

## Tech Stack

- Python 3.9+
- AWS Lambda (serverless computing)
- AWS S3 (object storage)
- AWS Redshift (data warehouse)
- AWS CloudWatch (monitoring)
- Pandas (data processing)
- Boto3 (AWS SDK)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials:
```bash
aws configure
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and AWS configuration
```

4. Deploy to AWS:
```bash
serverless deploy
```

## Architecture

```
CloudWatch Events → Lambda Functions → S3 → Redshift
                      ↓                 ↓
                 API Integrations   Data Transformation
```

## Pipeline Stages

### 1. Data Ingestion
- Fetches data from multiple financial APIs
- Handles rate limiting and API errors
- Stores raw data in S3

### 2. Data Processing
- Normalizes data formats
- Calculates derived metrics
- Validates data quality

### 3. Data Loading
- Loads processed data into Redshift
- Handles schema updates
- Maintains data history

## Environment Variables

- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key
- `YAHOO_FINANCE_API_KEY`: Your Yahoo Finance API key
- `AWS_REGION`: AWS region for deployment
- `S3_BUCKET`: S3 bucket for raw data
- `REDSHIFT_CLUSTER`: Redshift cluster identifier
- `REDSHIFT_DATABASE`: Redshift database name

## Monitoring

View Lambda logs:
```bash
aws logs tail /aws/lambda/data-pipeline --follow
```

Check CloudWatch metrics:
```bash
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Invocations --dimensions Name=FunctionName,Value=data-pipeline --start-time 2024-01-01 --end-time 2024-01-02 --period 3600 --statistics Sum
```

## Scheduling

Configure schedule in `serverless.yml`:
```yaml
events:
  - schedule: rate(1 hour)  # Run every hour
```

## Error Handling

- Automatic retry for failed API calls
- Dead-letter queue for failed records
- CloudWatch alarms for error rates
- Email notifications for critical failures

## Cost Optimization

- Lambda pay-per-use model
- S3 lifecycle policies for data archival
- Redshift concurrency scaling
- Reserved instances for predictable workloads

## License

MIT