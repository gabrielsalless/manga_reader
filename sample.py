import os
import re
import time
import urllib.parse

import lxml.html
import requests


class MangaDownloader:
    url_base = 'http://www.mangareader.net'
    
    session = requests.Session()

    chapters_path = (
        '//table[@id="listing"]//div[@class="chico_manga"]'
        '/following-sibling::a/@href'
    )
    page_path = '//select[@id="pageMenu"]/option/@value'

    PATH = re.compile(r'^/(?P<manga>.*?)/(?P<chapter>\d+)/?(?P<page>\d+)?$')

    def __init__(self, manga):
        self.url_manga = urllib.parse.urljoin(self.url_base, manga)

    def get_response(self, url):
        response = self.session.get(url)
        response.raise_for_status()
        return response

    def get_root_html(self, response):
        root = lxml.html.fromstring(response.content, base_url=self.url_base)
        root.make_links_absolute()
        return root

    def get_root(self, url):
        response = self.get_response(url)
        root = self.get_root_html(response)
        return root

    def get_page(self, page):
        url = urllib.parse.urljoin(self.url_base, page)
        page = self.get_root(url)
        for url_img in page.xpath('//div[@id="imgholder"]//img/@src'):
            url = urllib.parse.urlparse(url)

            self.get_img(url_img, url.path)

    def get_img(self, url, path):
        m = self.PATH.match(path).groupdict()
        folder = os.path.join(
            BASE_DIR,
            'mangas',
            m['manga'],
            m['chapter'].zfill(4)
        )
        img_path = os.path.join(folder, (m['page'] or '1').zfill(2))

        if not os.path.exists(folder):
            os.makedirs(folder)

        if os.path.exists(img_path):
            return

        response = self.get_response(url)
        with open(f'{img_path}.jpg', 'wb') as fp:
            fp.write(response.content)

        print(f'{img_path}.jpg')

    def get_chapter(self, url):
        chapters = self.get_root(url)
        for page in chapters.xpath(self.page_path):
            self.get_page(page)

    def __call__(self):
        root = self.get_root(self.url_manga)
        for url in root.xpath(self.chapters_path):
            self.get_chapter(url)


if __name__ == "__main__":
    manga_reader = MangaDownloader('/one-piece')

    manga_reader()