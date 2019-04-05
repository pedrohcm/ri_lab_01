# -*- coding: utf-8 -*-
import scrapy
import json
import datetime

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class OantagonistaSpider(scrapy.Spider):
    name = 'oantagonista'
    allowed_domains = ['oantagonista.com']
    start_urls = []
    pageStart = 1
    limitDate = datetime.datetime(2018,1,1)


    def __init__(self, *a, **kw):
        super(OantagonistaSpider, self).__init__(*a, **kw)
        with open('seeds/oantagonista.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    
    def parse(self, response):

        def checkDateLimit(response, lowerLimit):
            currentDate = response.css('time.entry-date ::attr(datetime)').get()
            currentDate = currentDate.split(' ')[0].split('-')

            date =  datetime.datetime(int(currentDate[-3]), int(currentDate[-2]), int(currentDate[-1]))

            return date > lowerLimit


        if not checkDateLimit(response, self.limitDate) :
            return

        articles = response.css('article')

        for href in articles.css('a.article_link::attr(href)'):
            yield response.follow(href, callback= self.scrapeNewsPage)

        page = response.url.split("/")[-2]

        nextPage = self.start_urls[0] + 'pagina/' + str(self.pageStart) +'/?ajax'
        self.pageStart = self.pageStart + 1


        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        
        yield scrapy.Request(nextPage, callback=self.parse)


    def scrapeNewsPage(self, response):

        def getArticleText(response):

            articleText = ""

            for paragraph in response.css('div.entry-content p::text'):
                articleText = articleText + paragraph.get()

            return articleText
            
        def reverseDate(date):
            date,time = date.split(" ")
            adjustedDate = date.split("-")
            adjustedDate.reverse()
            formattedDate = '/'.join(adjustedDate)	
            return formattedDate + " " + time

        def encodeUTF8(target):
            return target.encode('UTF-8')

        def getArticleAuthor(field):
            articleAuthor = field.replace('Por ','')
            return encodeUTF8(articleAuthor) if articleAuthor.strip() else "Sem autor"

        yield {
            'title': encodeUTF8(response.css('h1.entry-title::text').get()),
            # This source does not provide subtitles
            'subtitle': 'None',
            # Some articles have no author
            'author': getArticleAuthor(response.css('header.entry-header div::text').get()),
            # Formats date to match (dd/mm/yyyy hh:mi:ss)
            'date': encodeUTF8(reverseDate(response.css('time.entry-date ::attr(datetime)').get())),
            'section': encodeUTF8(response.css('header.entry-header span.postmeta span.categoria a::text').get()),
            # Joins paragraphs
            'text': encodeUTF8(getArticleText(response)),
            'url': response.request.url
        }
