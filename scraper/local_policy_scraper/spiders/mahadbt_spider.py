import scrapy
from local_policy_scraper.items import SchemeItem

class MahaDBTSpider(scrapy.Spider):
    name = 'mahadbt_spider'
    allowed_domains = ['mahadbt.maharashtra.gov.in']
    start_urls = ['https://mahadbt.maharashtra.gov.in/SchemeData/SchemeData?MenuID=1101']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, 
                meta={"playwright": True, "playwright_include_page": True}
            )

    async def parse(self, response):
        page = response.meta.get("playwright_page")
        if not page:
            # Fallback if playwright isn't working
            self.logger.warning("Playwright page not available, parsing static DOM.")
            yield from self.parse_static(response)
            return

        try:
            # Wait for the accordion or table to load
            await page.wait_for_selector(".accordion", timeout=10000)
            
            # Extract content using Playwright page context if needed
            # For simplicity, we fallback to response.css if the DOM is loaded
            content = await page.content()
            html_response = scrapy.http.HtmlResponse(url=page.url, body=content, encoding='utf-8')
            yield from self.parse_static(html_response)

        except Exception as e:
            self.logger.error(f"Playwright error: {e}")
        finally:
            await page.close()

    def parse_static(self, response):
        # Generic parsing logic for demonstration (assuming accordion structure)
        # This will need to be adjusted based on the actual DOM structure of MahaDBT
        departments = response.css('div.accordion-group')
        for dept in departments:
            dept_name = dept.css('.accordion-heading a::text').get(default='').strip()
            schemes = dept.css('.accordion-inner li a')
            for scheme in schemes:
                scheme_name = scheme.css('::text').get(default='').strip()
                scheme_url = scheme.attrib.get('href', '')
                if scheme_url.startswith('/'):
                    scheme_url = f"https://mahadbt.maharashtra.gov.in{scheme_url}"

                if scheme_name:
                    item = SchemeItem()
                    item['name'] = scheme_name
                    item['launching_authority'] = dept_name
                    item['category'] = "Welfare" # Default category
                    item['source_url'] = scheme_url
                    item['description'] = f"A welfare scheme administered by {dept_name}."
                    
                    yield item
