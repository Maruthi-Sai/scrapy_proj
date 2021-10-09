import scrapy


class PressReleasesNY(scrapy.Spider):
    name = 'ny_press_releases'

    start_urls = [
        'https://www.dfs.ny.gov/reports_and_publications/press_releases'
    ]

    def parse(self, response):
        for post in response.css('tr.data-row'):
            url = 'https://www.dfs.ny.gov' + post.css("td a::attr(href)").get()
            yield {
                "date"      : post.css("td::text").get().strip(),
                "title"     : post.css("td a::text").get(),
                "url"       : url,
                "content"   : response.follow(url.get(), callback=self.parse_post)
            }
        next_page = response.css('li.pager__item--next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
    
    def parse_post(self, response):
        yield response.css('h1::text').get()