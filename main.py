import shutil
import os
import pathlib

from environs import Env
from pathvalidate import sanitize_filename
import requests


class CollectPhotos:
    def __init__(self, login, password, url, directory):
        self.login = login
        self.password = password
        self.url = url
        self.directory = directory
        self.required_articles = self.get_required_articles()
        self.items = []
        self.barcodes = []
        self.get_all_items()
        self.photos = []
        self.get_photos()

    def get_required_articles(self):
        with open('required_articles.txt', 'r') as file:
            lines = [x.strip() for x in file.readlines()]
        return lines

    def get_all_items(self):
        for article in self.required_articles:
            params = {'article': article}
            response = requests.get(
                self.url, params=params, auth=(self.login, self.password)
            )
            items = response.json()['result']
            for item in items:
                item['required_article'] = article
                item['photos'] = []
            self.items += items
        self.barcodes = [x['barcode'] for x in self.items]

    def get_photos(self):
        res = pathlib.Path(self.directory)
        for dir_item in res.iterdir():
            for barcode in self.barcodes:
                if barcode in dir_item.stem:
                    self.photos.append(dir_item)

    def fill_photos(self):
        for item in self.items:
            for photo in self.photos:
                if item['barcode'] in photo.stem:
                    item['photos'].append(photo)

    def add_photos_by_article(self):
        for required_article, articles in self.res.items():
            self.res[required_article] = dict.fromkeys(articles, [])
            for article in articles:
                found_item = next(
                    item for item in self.items if item['article'] == article
                )
                self.res[required_article][article] = found_item['photos']

    def build_objects(self):
        self.fill_photos()
        self.res = {}
        for required_article in self.required_articles:
            articles = {
                x['article']
                for x in self.items
                if x['required_article'] == required_article
            }
            self.res[required_article] = articles
        self.add_photos_by_article()

    def carry_out_file_operation(self):
        root_folder = 'result'
        os.makedirs(root_folder, exist_ok=True)
        for required_article, articles in self.res.items():
            article_folder = sanitize_filename(required_article)
            intermediate_folder = f'{root_folder}/{article_folder}'
            os.makedirs(intermediate_folder, exist_ok=True)
            for article, files in articles.items():
                nested_folder = sanitize_filename(article)
                current_folder = f'{intermediate_folder}/{nested_folder}/'
                os.makedirs(current_folder, exist_ok=True)
                for file in files:
                    shutil.copy(str(file), f'{current_folder}/{file.name}')




def main():
    env = Env()
    env.read_env()
    api_login = env('API_LOGIN')
    api_password = env('API_PASSWORD')
    api_url = env('API_URL')
    directory = env('PHOTO_DIRECTORY')
    collect_photos = CollectPhotos(api_login, api_password, api_url, directory)
    collect_photos.build_objects()
    collect_photos.carry_out_file_operation()


if __name__ == '__main__':
    main()
