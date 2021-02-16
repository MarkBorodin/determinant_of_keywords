import uuid

import psycopg2
import requests
from bs4 import BeautifulSoup
from scrapy.http import Request
from scrapy.spiders import SitemapSpider
from main import KeyWordsForScrapy
from test_scraper.items import Subpage, Home_Page


class MySpider(SitemapSpider):
    name = 'sitemap_spider'
    home_page = []

    def start_requests(self):
        """get start urls. Parse home page"""

        # open_db
        self.open_db()

        # parse home page
        self.parse_main()

        # get sitemap.xml for sitemap_urls
        sitemap = self.home_page + 'sitemap.xml'
        response = requests.get(sitemap)
        if response.status_code == 200:
            self.sitemap_urls = [sitemap]

        # get robots.txt for sitemap_urls
        sitemap_with_robots = self.home_page + 'robots.txt'
        response = requests.get(sitemap_with_robots)
        if response.status_code == 200:
            self.sitemap_urls.append(sitemap_with_robots)

        for url in self.sitemap_urls:
            yield Request(url, self._parse_sitemap)

    def parse_main(self):
        """parse home page and write to db"""

        # create item
        item = Home_Page()

        item['uuid'] = str(uuid.uuid1())
        item['url'] = self.home_page
        item['sitemap_exists'] = 't' if requests.get(self.home_page + 'sitemap.xml').status_code == 200 else 'f'

        self.home_page_id = item['uuid'] # noqa

        # write to db Home_Page
        self.cur.execute(
            """INSERT INTO Home_Page (id, url, sitemap_exists)
               VALUES (%s, %s, %s)""", (
                item['uuid'],
                item['url'],
                item['sitemap_exists'],
            )
        )
        self.connection.commit()

    def parse(self, response, **kwargs):
        """parse page, page data and write to db"""

        # create item
        item = Subpage()

        # get html
        html = response.text
        self.html = html
        self.url = response.url

        # subpage
        subpage_id = str(uuid.uuid1())
        item['uuid'] = subpage_id
        item['url'] = response.url
        item['indexed_in_sitemap'] = 't'
        item['robots_follow_no_follow'] = 't'
        item['home_page'] = self.home_page_id

        # write subpage to db
        self.cur.execute(
            """INSERT INTO Subpage (id, url, indexed_in_sitemap, robots_follow_no_follow, home_page)
               VALUES (%s, %s, %s, %s, %s)""", (
                item['uuid'],
                item['url'],
                item['indexed_in_sitemap'],
                item['robots_follow_no_follow'],
                item['home_page'],
            )
        )
        self.connection.commit()

        # get_keywords
        self.get_keywords()

        # write keywords to db
        self.cur.execute(
            f"""INSERT INTO keywords (subpage, tf_idf_keywords, tf_idf_keywords_in_tags, tf_idf_keywords_in_url, 
            most_frequently_used_words, most_frequently_used_words_in_tags, most_frequently_used_words_in_url,
            rake_keywords, rake_keywords_in_tags, rake_keywords_in_url, rake_phrases, 
            keywords_that_are_common_to_all_methods, keywords_from_all_methods_that_are_in_the_main_tags)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
                subpage_id,
                str(self.item['tf_idf_keywords']),
                str(self.item['tf_idf_keywords_in_tags']),
                str(self.item['tf_idf_keywords_in_url']),
                str(self.item['most_frequently_used_words']),
                str(self.item['most_frequently_used_words_in_tags']),
                str(self.item['most_frequently_used_words_in_url']),
                str(self.item['rake_keywords']),
                str(self.item['rake_keywords_in_tags']),
                str(self.item['rake_keywords_in_url']),
                str(self.item['rake_phrases']),
                str(self.item['keywords_that_are_common_to_all_methods']),
                str(self.item['keywords_from_all_methods_that_are_in_the_main_tags']),
            )
        )
        self.connection.commit()

        # get data and write to db
        soup = BeautifulSoup(html, 'lxml')
        all_tags = soup.find_all()
        len_tags = len(all_tags)
        required_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'a', 'p', 'meta', 'title']

        for tag, num in zip(all_tags, range(1, len_tags)):
            if tag.name in required_tags:
                item['text'] = str(tag)
                item['appearance_position'] = str(num)
                item['subpage'] = subpage_id

                # write to db subpage
                self.cur.execute(
                    f"""INSERT INTO {str(tag.name)} (text, appearance_position, subpage)
                       VALUES (%s, %s, %s)""", (
                        item['text'],
                        item['appearance_position'],
                        item['subpage'],
                    )
                )
                self.connection.commit()

    def open_db(self):
        """open the database"""
        hostname = '127.0.0.1'
        username = 'parsing_admin'
        password = 'parsing_adminparsing_admin'
        database = 'parsing'
        port = "5444"
        self.connection = psycopg2.connect( # noqa
            host=hostname,
            user=username,
            password=password,
            dbname=database,
            port=port)
        self.cur = self.connection.cursor() # noqa

    def close_db(self):
        """close the database"""
        self.cur.close()
        self.connection.close()

    def close(self, reason):
        """close the database before closing the spider"""
        self.close_db()
        super().close(self, reason)

    def get_keywords(self):
        # get object. The first argument is url. The second argument is the number of keywords
        key_words = KeyWordsForScrapy(self.html, self.url)
        key_words.start()

        print('--------------------------------')
        ########################################
        print('keywords according to tf idf')

        self.item = dict()

        # get keywords according to tf idf
        self.item['tf_idf_keywords'] = key_words.keywords_tf_idf()

        # tf_idf_keywords on the page, which are also contained in main_tags tags
        self.item['tf_idf_keywords_in_tags'] = key_words.check_for_presence_in_main_tags(self.item['tf_idf_keywords'])

        # tf_idf_keywords on the page, which are also contained in site name
        self.item['tf_idf_keywords_in_url'] = key_words.check_by_site_name(self.item['tf_idf_keywords'])

        print('--------------------------------')
        ########################################
        print('most frequently used words on the page')

        # get most frequently used words
        self.item['most_frequently_used_words'] = key_words.most_frequently_used_words()

        # most_frequently_used_words on the page, which are also contained in main_tags tags
        self.item['most_frequently_used_words_in_tags'] = key_words.check_for_presence_in_main_tags(
            self.item['most_frequently_used_words']
        )

        # most_frequently_used_words on the page, which are also contained in site name
        self.item['most_frequently_used_words_in_url'] = key_words.check_by_site_name(
            self.item['most_frequently_used_words']
        )

        print('--------------------------------')
        ########################################
        print('keywords and phrases according to rake')

        # get keywords according to rake
        self.item['rake_keywords'] = key_words.rake_keywords()

        # keywords according to rake on the page, which are also contained in main_tags tags
        self.item['rake_keywords_in_tags'] = key_words.check_for_presence_in_main_tags(self.item['rake_keywords'])

        # keywords according to rake on the page, which are also contained in site name
        self.item['rake_keywords_in_url'] = key_words.check_by_site_name(self.item['rake_keywords'])

        print('--------------------------------')
        # get phrases according to rake
        self.item['rake_phrases'] = key_words.rake_phrase()

        # get keywords that are common to all methods (tf_idf, most_frequently_used_words, rake keywords)
        self.item['keywords_that_are_common_to_all_methods'] = key_words.all_methods_keywords()

        print('--------------------------------')
        print('keywords from all methods that are in the main tags')
        self.item['keywords_from_all_methods_that_are_in_the_main_tags'] = set(
            self.item['tf_idf_keywords_in_tags'] + self.item['most_frequently_used_words_in_tags'] +
            self.item['rake_keywords_in_tags']
        )
        print(self.item['keywords_from_all_methods_that_are_in_the_main_tags'])
