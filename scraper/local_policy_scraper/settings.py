BOT_NAME = 'local_policy_scraper'

SPIDER_MODULES = ['local_policy_scraper.spiders']
NEWSPIDER_MODULE = 'local_policy_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Playwright settings
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright browser config
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 20 * 1000,  # 20 seconds
}

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2

# Enable or disable pipelines
ITEM_PIPELINES = {
   'local_policy_scraper.pipelines.SQLAlchemyPipeline': 300,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
