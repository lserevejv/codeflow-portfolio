import os
import json
import boto3
import redshift_connector
from datetime import datetime
from utils.logger import logger


def handler(event, context):
    """
    Lambda handler for loading processed data into Redshift
    """
    logger.info("Starting data loading")
    
    s3_client = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    try:
        # Download processed data from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        processed_data = json.loads(response['Body'].read().decode('utf-8'))
        
        logger.info(f"Loading {len(processed_data)} records into Redshift")
        
        # Connect to Redshift
        conn = connect_to_redshift()
        
        # Create table if not exists
        create_table(conn)
        
        # Load data into Redshift
        records_loaded = load_data(conn, processed_data)
        
        conn.close()
        
        logger.info(f"Successfully loaded {records_loaded} records into Redshift")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'records_loaded': records_loaded,
                'source_key': key
            })
        }
        
    except Exception as e:
        logger.error(f"Data loading failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def connect_to_redshift():
    """
    Establish connection to Redshift cluster
    """
    host = os.getenv('REDSHIFT_CLUSTER')
    database = os.getenv('REDSHIFT_DATABASE')
    user = os.getenv('REDSHIFT_USER')
    password = os.getenv('REDSHIFT_PASSWORD')
    
    conn = redshift_connector.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=5439
    )
    
    logger.info("Connected to Redshift")
    return conn


def create_table(conn):
    """
    Create financial data table if it doesn't exist
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS financial_data (
        id INT IDENTITY(1,1),
        symbol VARCHAR(10),
        date DATE,
        open DECIMAL(15, 4),
        high DECIMAL(15, 4),
        low DECIMAL(15, 4),
        close DECIMAL(15, 4),
        volume BIGINT,
        source VARCHAR(50),
        daily_change DECIMAL(15, 4),
        daily_change_pct DECIMAL(10, 2),
        price_range DECIMAL(15, 4),
        price_range_pct DECIMAL(10, 2),
        volatility DECIMAL(10, 2),
        sma_5 DECIMAL(15, 4),
        sma_10 DECIMAL(15, 4),
        rsi DECIMAL(10, 2),
        collected_at TIMESTAMP,
        loaded_at TIMESTAMP DEFAULT SYSDATE,
        PRIMARY KEY (id)
    )
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info("Table created or already exists")
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        raise


def load_data(conn, data):
    """
    Load processed data into Redshift
    """
    insert_sql = """
    INSERT INTO financial_data (
        symbol, date, open, high, low, close, volume, source,
        daily_change, daily_change_pct, price_range, price_range_pct,
        volatility, sma_5, sma_10, rsi, collected_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    records_loaded = 0
    
    try:
        with conn.cursor() as cursor:
            for record in data:
                try:
                    cursor.execute(insert_sql, (
                        record.get('symbol'),
                        record.get('date'),
                        record.get('open'),
                        record.get('high'),
                        record.get('low'),
                        record.get('close'),
                        record.get('volume'),
                        record.get('source'),
                        record.get('daily_change'),
                        record.get('daily_change_pct'),
                        record.get('price_range'),
                        record.get('price_range_pct'),
                        record.get('volatility'),
                        record.get('sma_5'),
                        record.get('sma_10'),
                        record.get('rsi'),
                        record.get('collected_at')
                    ))
                    records_loaded += 1
                    
                except Exception as e:
                    logger.error(f"Error inserting record: {str(e)}")
                    continue
            
            conn.commit()
            
    except Exception as e:
        conn.rollback()
        logger.error(f"Error loading data: {str(e)}")
        raise
    
    return records_loaded