import requests
from django.shortcuts import render

from probe import get_img_for_prods


def main(request, page=None, pk=0):
    cats_url = f'http://127.0.0.1:8000/api/v1/delta/childs/{pk}/'
    cats_get_json = requests.get(cats_url).json()
    category = cats_get_json
    # parent = cats_get_json['parent']
    # grand = cats_get_json['grand']
    # print(category, parent, grand, sep='\n')


    # url = f'http://127.0.0.1:8000/api/v1/delta/products/{page}'
    if not page:
        url = 'http://127.0.0.1:8000/api/v1/delta/products/'
    else:
        url = f'http://127.0.0.1:8000/api/v1/delta/products/?{page}'

    get_json = requests.get(url).json()

    # print(get_json, url, sep='\n')

    prods = get_json['results']
    count_page = get_json['count']
    if get_json['previous']:
        if get_json['previous'][:-1] == '/':
            previous_page = '/page/' + get_json['previous'].split('?')[1:][0]
        else:
            previous_page = '/'
    else:
        previous_page = False
    if get_json['next']:
        next_page = '/page/' + get_json['next'].split('?')[1:][0]
    else:
        next_page = False

    context = {'title': 'Delta',
               'description': 'Delta main page',
               'prods': prods,
               'category': category,
               'count_page': count_page,
               'next_page': next_page,
               'previous_page': previous_page,
               }
    return render(request, 'delta/main_delta.html', context)






