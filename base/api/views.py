from threading import Thread

from django.shortcuts import render

from api.category_def import get_catalogs_wb_for_db
from api.models import Category
from api.proucts_def import get_product_for_db


def main(request):
    context = {'title': 'API',
               'description': 'API main page'}
    return render(request, 'api/main_API.html', context)


def update_cats(request):
    tr1 = Thread(target=get_catalogs_wb_for_db, daemon=True, kwargs=dict())
    print('Thread started')
    tr1.start()
    tr1.join()
    print('Thread Stopped')

    context = {'title': 'API',
               'description': 'Cats Updated'}
    return render(request, 'api/main_API.html', context)


def update_prod(request):
    cat_list = []
    for n in range(10000):
        try:
            cat_list.append(Category.objects.get(id=n+9000))
        except:
            pass

    for cat in cat_list:
        print(cat)
        t1 = Thread(target=get_product_for_db, daemon=True,
                    kwargs=dict(shard=cat.shard, query=cat.query, cat=cat.id))
        t1.start()  # Вроде работает
        print(f'{cat} - started')
        # t1.join()
        # print(f'{cat} - STOPPED')

    context = {'title': 'API',
               'description': 'Prods Updated'}
    return render(request, 'api/main_API.html', context)


