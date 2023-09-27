import requests
from django.shortcuts import render

from probe import get_img_for_prods


def main(request):
    url = 'http://127.0.0.1:8000/api/v1/delta/products/'
    prods = requests.get(url).json()[:10]

    context = {'title': 'Delta',
               'description': 'Delta main page',
               'prods': prods}
    return render(request, 'delta/main_delta.html', context)






