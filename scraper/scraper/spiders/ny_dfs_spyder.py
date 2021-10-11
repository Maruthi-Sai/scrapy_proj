import scrapy
import datetime


def string_cleaner(rouge_text):
    return (''.join(rouge_text.strip()).encode('utf-8', 'ignore').decode('ascii', 'ignore'))


def format_date(date):
    return datetime.datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')


class PressReleasesNY(scrapy.Spider):
    name = 'ny_press_releases'

    start_urls = [
        'https://www.dfs.ny.gov/reports_and_publications/press_releases'
    ]

    def parse(self, response):
        for url in response.css('tr.data-row td a::attr(href)'):
            yield response.follow(url.get(), callback=self.parse_post)
            
        next_page = response.css('li.pager__item--next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_post(self, response):
        title = string_cleaner(response.css('h1::text').get())
        content = ''
        for data in response.css('h3 em::text').getall():
            content += string_cleaner(data)
        yield {
            'date'      : format_date(response.css('p::text')[1].get().strip()),
            'title'     : title,
            'url'       : response.request.url,
            'content'   : f'{title} {content}'
        }