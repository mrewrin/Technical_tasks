import os.path
import json
import logging
import pandas as pd
from scrapy import Spider, Request, signals
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class OzonSpider(Spider):
    name = 'ozon'

    def __init__(self, *args, **kwargs):
        super(OzonSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.ozon.ru/category/smartfony-15502/?sorting=rating']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        smartphone_links = response.css('.b8r1.q9gq.wjy.wju.bz9.b3l3.b3l9 a::attr(href)').extract()[:100]
        for link in smartphone_links:
            yield Request(url=link, callback=self.parse_smartphone)

    def parse_smartphone(self, response):
        sel = Selector(text=response.body)
        os_version = sel.xpath('//div[contains(text(), "Версия ОС")]/following-sibling::div/text()').get()
        smartphone_name = sel.css('h1::text').get()
        if os_version is not None:
            os_version = os_version.strip()
        else:
            self.logger.warning("Operating system version not found for smartphone: %s", smartphone_name)
            os_version = None
        yield {
            'Smartphone Name': smartphone_name.strip(),
            'OS Version': os_version
        }

    def closed(self, reason):
        self.driver.quit()


class SaveToJsonPipeline:
    def open_spider(self, spider):
        if not os.path.exists('items.json'):
            with open('items.json', 'w') as f:
                f.write("[\n")

    def close_spider(self, spider):
        with open('items.json', 'a') as f:
            f.write("\n]")

    def process_item(self, item, spider):
        line = json.dumps(dict(item), indent=4, ensure_ascii=False) + ",\n"
        with open('items.json', 'a') as f:
            f.write(line)
        return item


def main():
    # Setting up logging
    logging.basicConfig(level=logging.INFO)

    # Configuring Selenium Chrome driver
    chrome_driver_path = 'C:\\Drivers\\chromedriver-win64\\chromedriver.exe'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = chrome_driver_path
    driver = webdriver.Chrome(options=chrome_options)

    # Setting up scrapy
    process = CrawlerProcess(settings={
        'ITEM_PIPELINES': {'__main__.SaveToJsonPipeline': 300},
        'FEEDS': {'items.json': {'format': 'json', 'overwrite': True}},
        'DOWNLOADER_MIDDLEWARES': {'scrapy_selenium.SeleniumMiddleware': 800},
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': chrome_driver_path,
        'SELENIUM_DRIVER_ARGUMENTS': ['--headless', '--no-sandbox', '--disable-dev-shm-usage'],
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4,
        'LOG_LEVEL': 'INFO'
    })
    process.signals.connect(reactor.stop, signal=signals.spider_closed)
    process.crawl(OzonSpider)
    process.start()
    reactor.run()


if __name__ == '__main__':
    main()
