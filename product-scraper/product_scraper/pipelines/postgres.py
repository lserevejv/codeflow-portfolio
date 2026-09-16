import psycopg2
from psycopg2 import sql
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from datetime import datetime


class PostgresPipeline:
    def __init__(self, postgres_settings):
        self.postgres_settings = postgres_settings
        self.connection = None
    
    @classmethod
    def from_crawler(cls, crawler):
        postgres_settings = {
            'host': crawler.settings.get('POSTGRES_HOST'),
            'port': crawler.settings.get('POSTGRES_PORT'),
            'database': crawler.settings.get('POSTGRES_DB'),
            'user': crawler.settings.get('POSTGRES_USER'),
            'password': crawler.settings.get('POSTGRES_PASSWORD'),
        }
        return cls(postgres_settings)
    
    def open_spider(self, spider):
        self.connection = psycopg2.connect(**self.postgres_settings)
        self.create_tables()
        spider.logger.info('Connected to PostgreSQL')
    
    def close_spider(self, spider):
        if self.connection:
            self.connection.close()
            spider.logger.info('Closed PostgreSQL connection')
    
    def create_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    product_id VARCHAR(255) UNIQUE,
                    name VARCHAR(500),
                    price DECIMAL(10, 2),
                    description TEXT,
                    availability VARCHAR(50),
                    url TEXT,
                    category VARCHAR(255),
                    brand VARCHAR(255),
                    scraped_at TIMESTAMP,
                    source_domain VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_product_id 
                ON products(product_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_source_domain 
                ON products(source_domain)
            """)
            
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_products_updated_at()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql'
            """)
            
            cursor.execute("""
                DROP TRIGGER IF EXISTS update_products_updated_at ON products
            """)
            
            cursor.execute("""
                CREATE TRIGGER update_products_updated_at
                BEFORE UPDATE ON products
                FOR EACH ROW
                EXECUTE FUNCTION update_products_updated_at()
            """)
            
            self.connection.commit()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        try:
            with self.connection.cursor() as cursor:
                query = sql.SQL("""
                    INSERT INTO products (
                        product_id, name, price, description, availability,
                        url, category, brand, scraped_at, source_domain
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (product_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        price = EXCLUDED.price,
                        description = EXCLUDED.description,
                        availability = EXCLUDED.availability,
                        url = EXCLUDED.url,
                        category = EXCLUDED.category,
                        brand = EXCLUDED.brand,
                        scraped_at = EXCLUDED.scraped_at,
                        source_domain = EXCLUDED.source_domain
                    RETURNING id
                """)
                
                cursor.execute(query, (
                    adapter.get('product_id'),
                    adapter.get('name'),
                    adapter.get('price'),
                    adapter.get('description'),
                    adapter.get('availability'),
                    adapter.get('url'),
                    adapter.get('category'),
                    adapter.get('brand'),
                    adapter.get('scraped_at'),
                    adapter.get('source_domain')
                ))
                
                result = cursor.fetchone()
                item['db_id'] = result[0] if result else None
                
                self.connection.commit()
                spider.logger.debug(f'Saved product to database: {adapter.get("name")}')
                
        except Exception as e:
            self.connection.rollback()
            spider.logger.error(f'Error saving to database: {e}')
            raise DropItem(f'Database error: {e}')
        
        return item