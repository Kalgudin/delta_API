import time
from datetime import datetime
from threading import Thread

import requests
from .models import *

CAT_PAGES = 2


def time_track(func):
    def surrogate(*args, **kwargs):
        started_at = time.time()

        result = func(*args, **kwargs)

        ended_at = time.time()
        elapsed = round(ended_at - started_at, 4)
        print(f'Функция {func} работала {elapsed} секунд(ы)')
        return result
    return surrogate


def _get_basket(vol):
    if 0 <= vol <= 143: return '01'
    elif 144 <= vol <= 287: return '02'
    elif 288 <= vol <= 431: return '03'
    elif 432 <= vol <= 719: return '04'
    elif 720 <= vol <= 1007: return '05'
    elif 1008 <= vol <= 1061: return '06'
    elif 1062 <= vol <= 1115: return '07'
    elif 1116 <= vol <= 1169: return '08'
    elif 1170 <= vol <= 1313: return '09'
    elif 1314 <= vol <= 1601: return '10'
    elif 1602 <= vol <= 1655: return '11'
    elif 1656 <= vol: return '12'
    else: return '13'


def get_image(prod_id):
    vol = str(prod_id)[:-5]
    part = str(prod_id)[:-3]
    basket = _get_basket(vol)
    link = f"https://basket-{basket}.wb.ru/vol{vol}/part{part}/{str(prod_id)}/images/c246x328/1.webp"
    return link


def get_average_price(id, price, all_prices):
    new_price = {"dt": int(datetime.now().timestamp()), "price": {"RUB": price}}

    if not all_prices:  #  список пуст
        url_history = f'https://wbx-content-v2.wbstatic.net/price-history/{id}.json'
        try:
            all_prices = requests.get(url_history).json()
        except Exception as ex:
            print(f'Новый товар( {id} ), нет средней цены(ошибка - {ex})')
            return price, 0, new_price  # возвращает среднюю цену, скидку в % и список всех цен.

    all_prices = all_prices[-3:] if len(all_prices) > 3 else all_prices  # Оставляем последние 4 цены

    summa = 0
    for element in all_prices:
        summa += element['price']['RUB']
    av_price = int(summa / len(all_prices))
    sale = int((1 - (price / av_price)) * 100)

    all_prices.append(new_price)

    return av_price, sale, all_prices


def _get_cat_list(cat_id, cat_list):
    def _get_parent(id, cat_list):
        if id:
            if id not in cat_list:
                cat_list.append(id)
            parent = Category.objects.get(id=id).parent_cat_id
            id, cat_list = _get_parent(parent, cat_list)
            return id, cat_list
        else:
            return id, cat_list

    cat_id, cat_list = _get_parent(cat_id, cat_list)
    return cat_list


def _product_to_db(prod_db, prod_json, cat, priceU):
    average_price, real_sale, all_prices = get_average_price(id=prod_json['id'],
                                                             price=priceU, all_prices=prod_db.all_prices)

    # if not prod_db.name:  # Новый продукт
    #     print(f'******* PRODUCT Created  {prod_json["name"]}, ID - {prod_json["id"]} ******** {real_sale} % ******* ')
    # else:
    #     print(f'******* PRODUCT  Edited {prod_json["name"]}, ID - {prod_json["id"]} ******* {real_sale} % ******** ')

    import re
    prod_db.name = re.compile('[^a-zA-Z0-9а-яА-Я ]').sub('', prod_json["name"])
    # prod_db.name = prod_json["name"]
    prod_db.base_price = int(prod_json["priceU"])
    prod_db.sale_price = int(prod_json["salePriceU"])
    prod_db.average_price = average_price
    prod_db.sale = real_sale
    prod_db.all_prices = all_prices
    prod_db.feedbacks = int(prod_json['feedbacks'])
    prod_db.rating = int(prod_json['rating'])
    prod_db.url = f'https://www.wildberries.ru/catalog/{prod_json["id"]}/detail.aspx?targetUrl=BP'  # надо будет убрать
    prod_db.category.add(*_get_cat_list(cat_id=cat, cat_list=[]))
    prod_db.img = get_image(prod_json['id'])
    # prod_db.save()

    return prod_db


def _get_product_from_json_for_db(data_js, cat):
    prod_list = []
    for product in data_js['data']['products']:
        cond_1 = (int(product['rating']) >= 4)
        cond_2 = (int(product['feedbacks']) >= 100)
        if cond_1 and cond_2:
            priceU = product["salePriceU"] if product["salePriceU"] else product["priceU"]
            pr, created = Product.objects.get_or_create(id=product['id'])
            # _product_to_db(prod_db=pr, prod_json=product, cat=cat, priceU=priceU)
            if created:  # Продукт новый
                prod_list.append(_product_to_db(prod_db=pr, prod_json=product, cat=cat, priceU=priceU))
            else:
                if pr.sale_price != priceU:  # У продукта изменилась цена
                    prod_list.append(_product_to_db(prod_db=pr, prod_json=product, cat=cat, priceU=priceU))

    Product.objects.bulk_update(prod_list, ['name', 'base_price', 'sale_price', 'average_price', 'sale', 'all_prices',
                                            'feedbacks', 'rating', 'url', ])
    # print(f'count prods = {len(prod_list)}')


def _start_thread(shard, query, cat, start_page, end_page):
    for page in range(start_page, end_page+1):
        headers = {'Accept': "*/*"}
        # print(f'Сбор позиций со страницы {page} из {end_page}')
        url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499&locale=ru&page={page}&sort=popular&spp=0&{query}'
        # print(url)
        r = requests.get(url, headers=headers)
        try:
            data_js = r.json()
            _get_product_from_json_for_db(data_js=data_js, cat=cat)
        except Exception as ex:
            print(f'----Error----{ex}  / in _start_thread / -------requests --- {r}')
            break


# dramatiq.set_broker(RedisBroker())
# @dramatiq.actor

def get_product_for_db(shard, query, cat):
    # print(CAT_PAGES)
    if CAT_PAGES >= 4:  # Запускаем в 4 потока(думаю, больше не стоит)
        n = round(CAT_PAGES / 4)
        tr1 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                              start_page=1, end_page=n))
        tr2 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                              start_page=n+1, end_page=2*n))
        tr3 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                              start_page=2*n+1, end_page=3*n))
        tr4 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                              start_page=3*n+1, end_page=CAT_PAGES))
        tr1.start()
        tr2.start()
        tr3.start()
        tr4.start()
        tr1.join()
        tr2.join()
        tr3.join()
        tr4.join()
    else:
        tr1 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                              start_page=1, end_page=CAT_PAGES))
        tr1.start()
        tr1.join()




