import scrapy
from local_policy_scraper.items import MentionItem
import datetime
from email.utils import parsedate_to_datetime

class NewsMentionSpider(scrapy.Spider):
    name = 'news_mention_spider'
    allowed_domains = ['news.google.com']

    def __init__(self, scheme_names=None, *args, **kwargs):
        super(NewsMentionSpider, self).__init__(*args, **kwargs)
        if scheme_names:
            self.scheme_names = scheme_names.split(',')
        else:
            self.scheme_names = ["Sanjay Gandhi Niradhar Yojana", "MahaDBT"]

    def start_requests(self):
        for scheme_name in self.scheme_names:
            # RSS feed for Google News
            query = scheme_name.replace(' ', '+')
            url = f"https://news.google.com/rss/search?q={query}+maharashtra&hl=hi&gl=IN&ceid=IN:hi"
            yield scrapy.Request(url, callback=self.parse, meta={'scheme_name': scheme_name})

    def parse(self, response):
        scheme_name = response.meta['scheme_name']
        
        # Scrape RSS XML items
        items = response.xpath('//item')
        for item in items:
            title = item.xpath('title/text()').get()
            link = item.xpath('link/text()').get()
            pub_date_str = item.xpath('pubDate/text()').get()
            source = item.xpath('source/text()').get()

            pub_date = datetime.datetime.now(datetime.timezone.utc)
            if pub_date_str:
                try:
                    pub_date = parsedate_to_datetime(pub_date_str)
                except Exception as e:
                    self.logger.warning(f"Could not parse date {pub_date_str}: {e}")

            if title:
                mention = MentionItem()
                mention['scheme_name'] = scheme_name
                mention['source'] = source or "Google News"
                mention['raw_text'] = title
                mention['language'] = 'hi'
                mention['published_date'] = pub_date
                mention['url'] = link
                yield mention
