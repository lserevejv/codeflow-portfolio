import os
import json
import boto3
from datetime import datetime, timedelta
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf
import requests
from utils.logger import logger


def handler(event, context):
    """
    Lambda handler for data ingestion from multiple financial APIs
    """
    logger.info("Starting data ingestion")
    
    s3_client = boto3.client('s3')
    bucket = os.getenv('S3_BUCKET')
    
    # Data collection results
    results = {
        'timestamp': datetime.now().isoformat(),
        'sources': {},
        'total_records': 0
    }
    
    try:
        # Collect data from Alpha Vantage
        alpha_vantage_data = collect_alpha_vantage_data()
        if alpha_vantage_data:
            s3_key = f"raw/alpha_vantage/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=json.dumps(alpha_vantage_data),
                ContentType='application/json'
            )
            results['sources']['alpha_vantage'] = len(alpha_vantage_data)
            results['total_records'] += len(alpha_vantage_data)
            logger.info(f"Uploaded Alpha Vantage data to s3://{bucket}/{s3_key}")
        
        # Collect data from Yahoo Finance
        yahoo_data = collect_yahoo_finance_data()
        if yahoo_data:
            s3_key = f"raw/yahoo_finance/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=json.dumps(yahoo_data),
                ContentType='application/json'
            )
            results['sources']['yahoo_finance'] = len(yahoo_data)
            results['total_records'] += len(yahoo_data)
            logger.info(f"Uploaded Yahoo Finance data to s3://{bucket}/{s3_key}")
        
        logger.info(f"Data ingestion completed: {results}")
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        logger.error(f"Data ingestion failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def collect_alpha_vantage_data():
    """
    Collect stock data from Alpha Vantage API
    """
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        logger.warning("Alpha Vantage API key not configured")
        return []
    
    try:
        ts = TimeSeries(key=api_key, output_format='pandas')
        
        # Popular stocks to track
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        data = []
        
        for symbol in symbols:
            try:
                # Get daily data
                df, meta_data = ts.get_daily(symbol=symbol, outputsize='compact')
                
                # Get the most recent data point
                latest = df.iloc[0]
                record = {
                    'symbol': symbol,
                    'date': latest.name.strftime('%Y-%m-%d'),
                    'open': float(latest['1. open']),
                    'high': float(latest['2. high']),
                    'low': float(latest['3. low']),
                    'close': float(latest['4. close']),
                    'volume': int(latest['5. volume']),
                    'source': 'alpha_vantage',
                    'collected_at': datetime.now().isoformat()
                }
                data.append(record)
                
            except Exception as e:
                logger.error(f"Error fetching {symbol} from Alpha Vantage: {str(e)}")
                continue
        
        return data
        
    except Exception as e:
        logger.error(f"Alpha Vantage API error: {str(e)}")
        return []


def collect_yahoo_finance_data():
    """
    Collect stock data from Yahoo Finance
    """
    try:
        # Popular stocks to track
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA']
        data = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    record = {
                        'symbol': symbol,
                        'date': latest.name.strftime('%Y-%m-%d'),
                        'open': float(latest['Open']),
                        'high': float(latest['High']),
                        'low': float(latest['Low']),
                        'close': float(latest['Close']),
                        'volume': int(latest['Volume']),
                        'source': 'yahoo_finance',
                        'collected_at': datetime.now().isoformat()
                    }
                    data.append(record)
                    
            except Exception as e:
                logger.error(f"Error fetching {symbol} from Yahoo Finance: {str(e)}")
                continue
        
        return data
        
    except Exception as e:
        logger.error(f"Yahoo Finance error: {str(e)}")
        return []