import scrapy
import json
import datetime
from local_policy_scraper.items import MentionItem

class RedditSpider(scrapy.Spider):
    name = 'reddit_spider'
    allowed_domains = ['reddit.com']
    
    # We use a custom user agent for Reddit API
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 PolicyAnalyzer/1.0',
        'DOWNLOAD_DELAY': 3,
    }

    def __init__(self, scheme_names=None, *args, **kwargs):
        super(RedditSpider, self).__init__(*args, **kwargs)
        if scheme_names:
            self.scheme_names = scheme_names.split(',')
        else:
            self.scheme_names = ["Sanjay Gandhi Niradhar Yojana", "MahaDBT"]

    def start_requests(self):
        for scheme_name in self.scheme_names:
            # We use the unauthenticated search JSON endpoint
            query = scheme_name.replace(' ', '+')
            url = f"https://www.reddit.com/search.json?q={query}&sort=new"
            yield scrapy.Request(url, callback=self.parse, meta={'scheme_name': scheme_name})

    def parse(self, response):
        scheme_name = response.meta['scheme_name']
        try:
            data = json.loads(response.body)
            children = data.get('data', {}).get('children', [])
            
            for child in children:
                post = child.get('data', {})
                title = post.get('title', '')
                selftext = post.get('selftext', '')
                permalink = post.get('permalink', '')
                created_utc = post.get('created_utc')
                
                raw_text = f"{title}\n{selftext}".strip()
                if not raw_text:
                    continue

                mention = MentionItem()
                mention['scheme_name'] = scheme_name
                mention['source'] = 'Reddit'
                mention['raw_text'] = raw_text
                mention['language'] = 'en' # Assuming english for reddit
                mention['url'] = f"https://www.reddit.com{permalink}"
                
                if created_utc:
                    mention['published_date'] = datetime.datetime.fromtimestamp(created_utc, tz=datetime.timezone.utc)
                else:
                    mention['published_date'] = datetime.datetime.now(datetime.timezone.utc)
                    
                yield mention
        except Exception as e:
            self.logger.error(f"Error parsing Reddit JSON: {e}")
