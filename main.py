import os
import re

import lxml.html
import requests
from betamax import Betamax
from betamax_serializers import pretty_json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CASSETTES_DIR = os.path.join(BASE_DIR, u'resources', u'cassettes')
MATCH_REQUESTS_ON = [u'method', u'uri', u'path', u'query']

Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
with Betamax.configure() as config:
    config.cassette_library_dir = CASSETTES_DIR
    config.default_cassette_options[u'serialize_with'] = u'prettyjson'
    config.default_cassette_options[u'match_requests_on'] = MATCH_REQUESTS_ON
    config.default_cassette_options[u'preserve_exact_body_bytes'] = True


url_base = 'http://www.mangareader.net'

url_manga = url_base + '/one-piece'
PATH = re.compile(r'^/(?P<manga>.*?)/(?P<chapter>\d+)/?(?P<page>\d+)?$')

session = requests.Session()
def manga_reader():

    response = session.get(url_manga)
    root = lxml.html.fromstring(response.content, base_url=url_base)
    root.make_links_absolute()

    for link in root.xpath('//table[@id="listing"]//a/@href'):
        chapter = session.get(link)
        chapter_root = lxml.html.fromstring(chapter.content, base_url=url_base)
        chapter_root.make_links_absolute()
        pages = chapter_root.xpath('//select[@id="pageMenu"]/option/@value')

        for page in pages:
            url_page = url_base + page
            chapter_page = session.get(url_page)
            chapter_page = lxml.html.fromstring(
                chapter_page.content, base_url=url_base
            )
            chapter_page.make_links_absolute()
            m = PATH.match(page).groupdict()
            for img in chapter_page.xpath('//img[@id="img"]/@src'):
                folder = os.path.join(BASE_DIR,'mangas',m['manga'],m['chapter'].zfill(4))
                img_path = os.path.join(folder,(m['page'] or '1').zfill(2))

                if not os.path.exists(folder):
                    os.makedirs(folder)
                if os.path.exists (img_path):
                    continue
                chapter_img = session.get(img)
                with open(f'{img_path}.jpg','wb') as fp:
                    fp.write(chapter_img.content)
                print (img_path)


if __name__ == "__main__":
    manga_reader()






