import requests
from .models import *
from .proucts_def import time_track


def _append_category_to_db(cat):
    if 'shard' in cat:
        shard = cat['shard']
    else:
        if 'childs' not in cat:
            print(f'----- Пустая категория {cat["name"]}')
            return None
        shard = ''
    name = cat['name'] if 'name' in cat else cat['seo']
    query = cat['query'] if 'query' in cat else ''
    parent = int(cat['parent']) if 'parent' in cat else None

    category, created = Category.objects.get_or_create(id=int(cat['id']))

    category.name = name
    category.url = cat['url']
    category.shard = shard
    category.query = query
    category.parent_cat_id = parent
    category.updated_at = 0
    if created:
        print(f"Создана новая категория    {name}")
    else:
        print(f"Обнавлена старая категория {name}")
    return category


def _recursion_cat_to_db(cat_js, cat_list):
    res = _append_category_to_db(cat_js)
    if res:
        cat_list.append(res)
    if 'childs' in cat_js:
        for child in cat_js['childs']:
            _recursion_cat_to_db(cat_js=child, cat_list=cat_list)
    return cat_list


def _get_category_for_db(response):
    data = response.json()
    for cat in data:
        try:
            cat_list = _recursion_cat_to_db(cat_js=cat, cat_list=[])
            Category.objects.bulk_update(cat_list, ['name', 'url', 'shard', 'query', 'parent_cat_id', 'updated_at', ])
        except Exception as ex:
            print(f'----------ERROR {ex}  -- in _get_category_for_db')
            continue


def get_catalogs_wb_for_db():
    url = 'https://www.wildberries.ru/webapi/menu/main-menu-ru-ru.json'
    headers = {'Accept': "*/*"}
    response = requests.get(url, headers=headers)
    try:
        _get_category_for_db(response)
    except Exception as ex:
        print(f'Ошибка - {ex}  --  get_catalogs_wb_for_db')


##############################################################
