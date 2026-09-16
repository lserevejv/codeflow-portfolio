import re
from datetime import datetime
from itemadapter import ItemAdapter


class DataNormalizationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Normalize price (remove currency symbols, convert to float)
        if adapter.get('price'):
            price_text = adapter['price']
            price_clean = re.sub(r'[^\d.]', '', price_text)
            try:
                adapter['price'] = float(price_clean)
            except ValueError:
                adapter['price'] = None
        
        # Normalize availability
        if adapter.get('availability'):
            availability = adapter['availability'].lower()
            adapter['availability'] = 'in_stock' if 'stock' in availability else 'out_of_stock'
        
        # Add timestamp
        adapter['scraped_at'] = datetime.now().isoformat()
        
        # Extract source domain
        if adapter.get('url'):
            from urllib.parse import urlparse
            adapter['source_domain'] = urlparse(adapter['url']).netloc
        
        # Clean description
        if adapter.get('description'):
            adapter['description'] = adapter['description'].strip()
        
        # Clean name
        if adapter.get('name'):
            adapter['name'] = adapter['name'].strip()
        
        spider.logger.debug(f'Normalized item: {adapter.get("name")}')
        return item