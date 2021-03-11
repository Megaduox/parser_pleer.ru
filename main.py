from selectorlib import Extractor
import requests
import csv
import time
from lxml import html


# проблема с 204 кодом решается добавлением хедеров
# делать задержку при парсинге рандомом в несколько секунд
# рандом хедеров
# пейджинация чуть хитрее, потому что несуществующие страницы отдают 200 код, а не 404
# сайт банит, даже если делаешь не много запросов, нужно пилить либо через прокси, либо через selenium
# если нет в наличии, ценник зелёным цветом и вёрстка меняется

# надо писать:
# 1. функция сбора урл +
# 2. функция парсинга каждого товара +
# 3. функция записи в csv +
# 4. функция работы через прокси - осталось доделать
headers = {
    'authority': 'https://www.google.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'referer': 'https://www.google.com/',
    'accept-language': 'ru-RU, ru;q=0.9',
}
url = 'https://www.pleer.ru/list_svetodiodnye-dizajnerskie-lampochki.html'
domain = 'https://www.pleer.ru/'
ALL_DATA = dict()
QUEUE_URL = set()


def add_to_csv_from_file(product_dict):
    # записывает по очереди данные, полученные из словаря со спаршенными значениями в виде словаря в csv-файл

    with open('data.csv', 'a', newline='') as csvfile:
        fieldnames = ["Name", "Price", "Id", "Title"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL)
        writer.writerow(product_dict)


def get_data(product_link):
    # принимает на вход один урл товара, парсит данные
    # она их никуда не записывает, возвращает список данных в виде словаря

    product = dict()
    r = requests.get(product_link, headers=headers)
    tree = html.fromstring(r.content)
    product_name = tree.xpath("//span[@class='product_title']")
    product_id = tree.xpath("//div[@class='product_id']")
    product_price = tree.xpath("//div[@class='product_price product_price_color4']"
                               "/div[@class='price']/div[@class='hide']")
    product_title = tree.findtext('.//title')
    product['Title'] = product_title
    for name in product_name:
        print(name.text)
        product['Name'] = name.text
    for price in product_price:
        print(price.text)
        product['Price'] = price.text
    for id in product_id:
        print(id.text)
        product['Id'] = id.text
    time.sleep(3)

    return product


def get_links(page_url):
    # функция принимает на вход урл, берёт все ссылки с него на товары из листинга, проходит по пейдижнации
    # складывает ссылки в множество QUEUE_URL

    first_url = page_url.split(".html")[0]
    pages_count = 0
    r = requests.get(page_url, headers=headers)
    tree = html.fromstring(r.content)
    # поставить условие, если не содержит основного контента - стоп и печать ошибки
    first_page_links = tree.xpath('//div[@class="product_link h3"]//a/@href')
    print('Код ответа корневого УРЛ: ', r.status_code)
    time.sleep(3)

    while True:
        pages_count += 1
        page_url = f'{first_url}_page{pages_count}.html'
        print("Проверяю доступность урл:", page_url)
        r = requests.get(url, headers=headers)
        tree = html.fromstring(r.content)
        # поставить условие, если не содержит основного контента - стоп и печать ошибки
        page_links = tree.xpath('//div[@class="product_link h3"]//a/@href')

        for one_link in page_links:

            QUEUE_URL.add(domain+one_link) # add to QUEUE

        print('Все ссылки со страниц добавил в очередь')

        if r.status_code == 404 or page_links == first_page_links:
            print('Останавливаю цикл, все страницы пейджинации спарсил')
            break

        time.sleep(3)


def main():
    with open('data.csv', 'a', newline='') as csvfile:
        fieldnames = ["Name", "Price", "Id", "Title"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL)
        writer.writeheader()

    get_links(url)

    while len(QUEUE_URL) != 0:
        current_url = QUEUE_URL.pop()
        add_to_csv_from_file(get_data(current_url))


if __name__ == '__main__':
    main()




