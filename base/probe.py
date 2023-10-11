import re

import requests

from api.models import Product


#  https://basket-10.wb.ru/vol1398/part139817/139817823/images/c246x328/1.webp
def _get_basket(vol):
    if 0 <= vol <= 143:
        return '01'
    elif 144 <= vol <= 287:
        return '02'
    elif 288 <= vol <= 431:
        return '03'
    elif 432 <= vol <= 719:
        return '04'
    elif 720 <= vol <= 1007:
        return '05'
    elif 1008 <= vol <= 1061:
        return '06'
    elif 1062 <= vol <= 1115:
        return '07'
    elif 1116 <= vol <= 1169:
        return '08'
    elif 1170 <= vol <= 1313:
        return '09'
    elif 1314 <= vol <= 1601:
        return '10'
    elif 1602 <= vol <= 1655:
        return '11'
    elif 1656 <= vol:
        return '12'
    else:
        return '13'


def get_image(id):
    vol = str(id)[:-5]
    part = str(id)[:-3]
    basket = _get_basket(int(vol))

    print(f'ID - {id}, Vol - {vol}, Part - {part}')
    link = f"https://basket-{basket}.wb.ru/vol{vol}/part{part}/{str(id)}/images/c246x328/1.webp"
    return link


def get_img_for_prods():
    prods = Product.objects.all()
    for prod in prods:
        prod.img = get_image(prod.id)
        prod.save()
    return 'Images added :)'




#################################









# # https://catalog.wb.ru/catalog/school2/catalog?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499&locale=ru&page=1&sort=popular&spp=0&cat=130014'
# #
#
# # get_image(139200508)
#
# headers = {'Accept': "*/*"}
# # print(f'Сбор позиций со страницы {page} из {end_page}')
# url = 'https://catalog.wb.ru/catalog/office_bigroot/catalog?appType=1&curr=rub&dest=-1075831,-77677,-398551,12358499&locale=ru&page=1&sort=popular&spp=0&cat=10470'
#
# # print(url)
# r = requests.get(url, headers=headers)
# print(r)

