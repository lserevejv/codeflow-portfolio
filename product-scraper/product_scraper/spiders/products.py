import scrapy
from product_scraper.items import ProductItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random


class ProductsSpider(scrapy.Spider):
    name = 'products'
    
    def __init__(self, start_url=None, *args, **kwargs):
        super(ProductsSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else [
            'https://example-ecommerce.com/products'
        ]
        
        # Set up Selenium for JavaScript rendering
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def parse(self, response):
        # Use Selenium to handle JavaScript-rendered content
        self.driver.get(response.url)
        
        # Wait for product listings to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'product-item'))
            )
        except:
            self.logger.warning('Timeout waiting for products to load')
        
        # Extract product links
        product_links = self.driver.find_elements(By.CSS_SELECTOR, '.product-item a')
        
        for link in product_links[:20]:  # Limit to 20 products for demo
            product_url = link.get_attribute('href')
            if product_url:
                yield scrapy.Request(product_url, callback=self.parse_product)
        
        # Handle pagination
        next_page = self.driver.find_elements(By.CSS_SELECTOR, '.next-page')
        if next_page:
            next_url = next_page[0].get_attribute('href')
            if next_url:
                yield scrapy.Request(next_url, callback=self.parse)
    
    def parse_product(self, response):
        # Use Selenium for product page
        self.driver.get(response.url)
        
        # Wait for product details to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'product-title'))
            )
        except:
            self.logger.warning(f'Timeout waiting for product details: {response.url}')
        
        item = ProductItem()
        
        try:
            # Extract product data
            item['product_id'] = self.driver.find_element(By.CSS_SELECTOR, '.product-id').text
            item['name'] = self.driver.find_element(By.CSS_SELECTOR, '.product-title').text
            item['price'] = self.driver.find_element(By.CSS_SELECTOR, '.product-price').text
            item['description'] = self.driver.find_element(By.CSS_SELECTOR, '.product-description').text
            item['availability'] = self.driver.find_element(By.CSS_SELECTOR, '.product-availability').text
            item['url'] = response.url
            
            # Extract images
            images = self.driver.find_elements(By.CSS_SELECTOR, '.product-image img')
            item['images'] = [img.get_attribute('src') for img in images]
            
            # Extract category
            category = self.driver.find_elements(By.CSS_SELECTOR, '.product-category')
            item['category'] = category[0].text if category else None
            
            # Extract brand
            brand = self.driver.find_elements(By.CSS_SELECTOR, '.product-brand')
            item['brand'] = brand[0].text if brand else None
            
            self.logger.info(f'Successfully scraped product: {item["name"]}')
            
        except Exception as e:
            self.logger.error(f'Error extracting product data: {e}')
            return None
        
        # Random delay to avoid detection
        time.sleep(random.uniform(1, 3))
        
        yield item
    
    def closed(self, reason):
        self.driver.quit()
        self.logger.info(f'Spider closed: {reason}')