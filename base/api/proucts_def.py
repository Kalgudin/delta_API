import time
from datetime import datetime
from threading import Thread

import requests
from .models import *

CAT_PAGES = 8


def time_track(func):
    def surrogate(*args, **kwargs):
        started_at = time.time()

        result = func(*args, **kwargs)

        ended_at = time.time()
        elapsed = round(ended_at - started_at, 4)
        print(f'Функция {func} работала {elapsed} секунд(ы)')
        return result

    return surrogate


def _get_basket(prod_id):
    vol = prod_id // 100000
    part = prod_id // 1000
    if 0 <= vol <= 143:
        basket_code = '01'
    elif 144 <= vol <= 287:
        basket_code = '02'
    elif 288 <= vol <= 431:
        basket_code = '03'
    elif 432 <= vol <= 719:
        basket_code = '04'
    elif 720 <= vol <= 1007:
        basket_code = '05'
    elif 1008 <= vol <= 1061:
        basket_code = '06'
    elif 1062 <= vol <= 1115:
        basket_code = '07'
    elif 1116 <= vol <= 1169:
        basket_code = '08'
    elif 1170 <= vol <= 1313:
        basket_code = '09'
    elif 1314 <= vol <= 1601:
        basket_code = '10'
    elif 1602 <= vol <= 1655:
        basket_code = '11'
    elif 1656 <= vol:
        basket_code = '12'
    else:
        basket_code = '13'
    return f"https://basket-{basket_code}.wb.ru/vol{vol}/part{part}/{str(prod_id)}"


def get_image(prod_id):
    basket = _get_basket(prod_id)
    link = f"{basket}/images/c246x328/1.webp"
    return link


def get_average_price(id, price, all_prices):
    new_price = {"dt": int(datetime.now().timestamp()), "price": {"RUB": price}}
    if not all_prices:  # список пуст
        #  https://basket-02.wb.ru/vol147/part14747/14747989/info/price-history.json
        # print(url_history)
        basket = _get_basket(int(id))
        url_history = f'{basket}/info/price-history.json'
        all_prices = requests.get(url_history).json()
        if not all_prices:
            print(f'Новый товар( {id} ), нет средней цены(ошибка)')
            return price, 0, new_price  # возвращает среднюю цену, скидку в % и список всех цен.  https://wbx-content-v2.wbstatic.net/price-history/114407749.json

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
    prod_db.url = f'https://www.wildberries.ru/catalog/{prod_json["id"]}/detail.aspx'  # надо будет убрать
    prod_db.category.add(*_get_cat_list(cat_id=cat, cat_list=[]))
    _basket = _get_basket(prod_json['id'])
    prod_db.basket = _basket
    prod_db.img = f"{_basket}/images/c246x328/1.webp"
    # prod_db.save()

    return prod_db


def _get_product_from_json_for_db(data_js, cat):
    prod_list = []
    for product in data_js['data']['products']:
        # print(f'-------------------------PRODUCT - ------{product}--------------------------------------------')
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
                                            'feedbacks', 'rating', 'url', 'img', 'basket'])
    # print(f'IN _get_product_from_json_for_db == prod_list = > {prod_list}-----------------------------')


def _start_thread(shard, query, cat, start_page, end_page):
    for page in range(start_page, end_page + 1):
        headers = {'Accept': "*/*"}
        print(f'Сбор позиций со страницы {page} из {end_page}')

        url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&cat={cat}&curr=rub&dest=-1257786&page={page}&regions=80,38,83,4,64,33,68,70,30,40,86,75,69,1,31,66,110,48,22,71,114&sort=popular&spp=33'

        r = requests.get(url, headers=headers)
        # print('======= _start_thread === request ---   ', r)
        try:
            data_js = r.json()
            # print('======= IN _start_thread === data_js ---   > ')
            _get_product_from_json_for_db(data_js=data_js, cat=cat)
        except Exception as ex:
            print(f'----Error----{ex}  / in _start_thread / -------requests --- {r}')
            break


# dramatiq.set_broker(RedisBroker())
# @dramatiq.actor

def get_product_for_db(shard, query, cat):
    if CAT_PAGES >= 4:  # Запускаем в 4 потока(думаю, больше не стоит)
        n = round(CAT_PAGES / 4)
        tr1 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                                    start_page=1, end_page=n))
        tr2 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                                    start_page=n + 1, end_page=2 * n))
        tr3 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                                    start_page=2 * n + 1, end_page=3 * n))
        tr4 = Thread(target=_start_thread, daemon=True, kwargs=dict(shard=shard, query=query, cat=cat,
                                                                    start_page=3 * n + 1, end_page=CAT_PAGES))
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
        # _start_thread(shard=shard, query=query, cat=cat, start_page=1, end_page=CAT_PAGES)

#  https://catalog.wb.ru/catalog/men_shoes/v4/filters?TestGroup=freq_02&TestID=286&appType=1&cat=8194&curr=rub&dest=-1257786&regions=80,38,83,4,64,33,68,70,30,40,86,75,69,1,31,66,110,48,22,71,114&spp=33
#  https://catalog.wb.ru/catalog/livingroom7/catalog?appType=1&cat=305&curr=rub&dest=-1257786&regions=80,38,83,4,64,33,68,70,30,40,86,75,69,1,31,66,110,48,22,71,114&sort=popular&spp=33
#  https://catalog.wb.ru/catalog/livingroom7/catalog?TestGroup=control&TestID=237&appType=1&cat=305&curr=rub&dest=-1257786&page=1&regions=80,38,83,4,64,33,68,70,30,40,86,75,69,1,31,66,110,48,22,71,114&sort=popular&spp=33

#  https://catalog.wb.ru/catalog/electronic14/catalog?appType=1&cat=59132&curr=rub&dest=-1257786&regions=80,38,83,4,64,33,68,70,30,40,86,75,69,1,31,66,110,48,22,71,114&sort=popular&spp=33


#  PRODUCT - ------
#  {'__sort': 58143, 'ksort': 4531, 'time1': 4, 'time2': 29, 'dist': 67, 'id': 141502445, 'root': 46456805, 'kindId': 3, 'subjectId': 276, 'subjec
# tParentId': 4607, 'name': 'Ползунки для малышей новорожденных', 'brand': 'Carrot', 'brandId': 32358, 'siteBrandId': 42358, 'supplierId': 26650, 'sale': 25, 'priceU': 180000, 'salePrice
# U': 135000, 'logisticsCost': 0, 'saleConditions': 0, 'returnCost': 0, 'pics': 5, 'rating': 5, 'reviewRating': 4.9, 'feedbacks': 2172, 'volume': 19, 'colors': [{'name': 'белый', 'id': 1
# 6777215}, {'name': 'коричневый', 'id': 10824234}], 'sizes': [{'name': '56-62', 'origName': '56-62', 'rank': 349783, 'optionId': 239658170, 'returnCost': 0, 'wh': 507, 'sign': 'pj/BO92U
# JKI0q5hq+loIF32bevs=', 'payload': ''}, {'name': '62-68', 'origName': '62-68', 'rank': 375540, 'optionId': 239658171, 'returnCost': 0, 'wh': 120762, 'sign': 'log5g3xX4SiZRdqivkko6tM/UR8
# =', 'payload': ''}, {'name': '68-74', 'origName': '68-74', 'rank': 391125, 'optionId': 239658172, 'returnCost': 0, 'wh': 507, 'sign': '7z5zEvHaa/cBf/J12FsBpUud/u0=', 'payload': ''}, {'
# name': '74-80', 'origName': '74-80', 'rank': 402047, 'optionId': 239658173, 'returnCost': 0, 'wh': 120762, 'sign': 'mf4QUv/fmzRKHVEOCAwwcxpBnog=', 'payload': ''}, {'name': '80-86', 'or
# igName': '80-86', 'rank': 412970, 'optionId': 239658174, 'returnCost': 0, 'wh': 507, 'sign': 'nItYNvASWAhmQOMEVhJ8QsA0InY=', 'payload': ''}, {'name': '86-92', 'origName': '86-92', 'ran
# k': 422670, 'optionId': 239658175, 'returnCost': 0, 'wh': 120762, 'sign': 'QY1v6xrOBQopEGtE8bX+5Sj1qgg=', 'payload': ''}], 'diffPrice': False, 'log': {}}
