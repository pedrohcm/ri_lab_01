# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class OantagonistaSpider(scrapy.Spider):
    name = 'oantagonista'
    allowed_domains = ['oantagonista.com']
    start_urls = []

    def __init__(self, *a, **kw):
        super(OantagonistaSpider, self).__init__(*a, **kw)
        with open('seeds/oantagonista.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
 
        for article in response.css('article'):
            yield {
				'titulo': article.css('div.container-post-home a.article_link h2::text').get(),
                'secao': article.css('div.container-post-home a.article_link span.postmeta span.categoria::text').get(),
                'data': article.css('div.container-post-home a.article_link span.postmeta time::text').get(),
                'autor': article.css('div.container-post-home a.article_link span.postmeta div::text').get(),
                'texto': article.css('div.container-post-home a.article_link p::text').get(),
                'url': article.css('div.container-post-home a.article_link::attr("href")').get()
            }
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        
        #
        #
        #
