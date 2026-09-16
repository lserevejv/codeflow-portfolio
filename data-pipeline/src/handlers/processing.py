import os
import json
import boto3
import pandas as pd
from datetime import datetime
from utils.logger import logger


def handler(event, context):
    """
    Lambda handler for data processing and normalization
    """
    logger.info("Starting data processing")
    
    s3_client = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    try:
        # Download raw data from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        raw_data = json.loads(response['Body'].read().decode('utf-8'))
        
        logger.info(f"Processing {len(raw_data)} records from {key}")
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(raw_data)
        
        # Data normalization and enrichment
        processed_data = normalize_data(df)
        
        # Calculate derived metrics
        processed_data = calculate_metrics(processed_data)
        
        # Convert back to JSON
        processed_json = processed_data.to_dict('records')
        
        # Upload processed data to S3
        processed_key = key.replace('raw/', 'processed/')
        s3_client.put_object(
            Bucket=bucket,
            Key=processed_key,
            Body=json.dumps(processed_json),
            ContentType='application/json'
        )
        
        logger.info(f"Uploaded processed data to s3://{bucket}/{processed_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed_records': len(processed_json),
                'source_key': key,
                'processed_key': processed_key
            })
        }
        
    except Exception as e:
        logger.error(f"Data processing failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def normalize_data(df):
    """
    Normalize and clean financial data
    """
    # Ensure numeric columns are float
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Add normalized timestamp
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    
    # Standardize symbol format
    df['symbol'] = df['symbol'].str.upper()
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['symbol', 'date', 'source'])
    
    # Remove rows with missing critical data
    df = df.dropna(subset=['symbol', 'close'])
    
    logger.info(f"Normalized data: {len(df)} records")
    return df


def calculate_metrics(df):
    """
    Calculate derived financial metrics
    """
    # Calculate daily change
    df['daily_change'] = df['close'] - df['open']
    df['daily_change_pct'] = (df['daily_change'] / df['open']) * 100
    
    # Calculate price range
    df['price_range'] = df['high'] - df['low']
    df['price_range_pct'] = (df['price_range'] / df['open']) * 100
    
    # Calculate volatility indicators
    df['volatility'] = df['price_range_pct']
    
    # Add market cap estimate (simplified)
    df['estimated_volume_value'] = df['close'] * df['volume']
    
    # Add technical indicators
    df = df.groupby('symbol').apply(calculate_moving_averages).reset_index(drop=True)
    
    logger.info(f"Calculated metrics for {len(df)} records")
    return df


def calculate_moving_averages(group):
    """
    Calculate moving averages for a single symbol
    """
    group = group.sort_values('date')
    
    # Simple moving averages
    group['sma_5'] = group['close'].rolling(window=5, min_periods=1).mean()
    group['sma_10'] = group['close'].rolling(window=10, min_periods=1).mean()
    
    # Relative strength index (simplified)
    delta = group['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / loss
    group['rsi'] = 100 - (100 / (1 + rs))
    
    return group