from typing import List
from bs4 import BeautifulSoup
import requests
from requests import HTTPError
import validators
import os
import justext
from urllib.parse import urlparse


class Crawler:
    def __init__(self, start_page_url: str):
        self.start_page_url = start_page_url
        self.host_name = urlparse(self.start_page_url).hostname
        self.page_files_count = 0
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__init_pages_list_file()
        self.clear_page_directory()

    def clear_page_directory(self):
        dir = os.path.join(self.base_dir, 'pages')
        for file in os.listdir(dir):
            os.remove(os.path.join(dir, file))

    def __init_pages_list_file(self):
        with open(os.path.join(self.base_dir, 'task_1/pages_list.txt'), 'w') as file:
            file.write('')

    def __save_page(self, text: str):
        with open(os.path.join(self.base_dir, f'pages/page_{self.page_files_count + 1}.txt'), 'w',
                  encoding='utf-8') as file:
            file.write(text)
        self.page_files_count += 1

    def __save_url(self, url: str):
        with open(os.path.join(self.base_dir, 'task_1/pages_list.txt'), 'a') as file:
            file.write(f'[{self.page_files_count + 1}] {url}\n')

    def __get(self, url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            try:
                raw_html = response.content.decode('utf-8')
            except UnicodeDecodeError:
                raw_html = ''

            return raw_html
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return ''
        except Exception as err:
            print(f'Other error occurred: {err}')
            return ''

    def __get_links(self, soup: BeautifulSoup) -> List[str]:
        links = []
        for link in soup.find_all('a'):
            if 'href' not in link.attrs:
                continue

            href = str(link['href'])
            if href.startswith('/'):
                href = href[1:]
            href_with_base = self.start_page_url + href

            # Проверяем, чтобы не уходить по ссылкам вне сайта
            if validators.url(href) and self.host_name in href:
                links.append(href)
                continue

            if validators.url(href_with_base) and self.host_name in href_with_base:
                links.append(href_with_base)

        return links

    def collect(self, num_pages: int, max_depth: int):
        count = 0
        links = [list() for _ in range(max_depth + 1)]
        links[0] = [self.start_page_url]
        saved_links = []

        idx = 0
        while idx < max_depth - 1 and count < num_pages:
            current_list = links[idx]
            idx += 1

            for link in current_list:
                if count >= num_pages:
                    break

                print(f'Processing link #{count + 1} - {link}')
                raw_html = self.__get(link)
                if raw_html != '' and link not in saved_links:
                    self.__save_url(link)
                    saved_links.append(link)
                    paragraphs = justext.justext(raw_html, justext.get_stoplist('Russian'))
                    clear_page = ''
                    for paragraph in paragraphs:
                        clear_page += paragraph.text + ' '
                    self.__save_page(clear_page)

                    count += 1

                    soup = BeautifulSoup(raw_html, 'lxml')
                    urls = self.__get_links(soup)

                    links[idx] += urls


if __name__ == '__main__':
    crawler = Crawler('https://meduza.io/')
    crawler.collect(100, 4)
