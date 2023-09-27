from threading import Thread

from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet

from .category_def import get_catalogs_wb_for_db
from .proucts_def import get_product_for_db, get_image, get_average_price
from rest_framework import generics, viewsets, mixins
from .models import Category, Product
from .serializers import CategorySerializer, CategoryAllSerializer, ProductSerializer


class CategoryViewSetPublic(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSetPublic(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(mixins.CreateModelMixin,  # Удаляем и добавляем миксины в зависимости от функционала
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryAPIUpdate(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


def main(request):
    context = {'title': 'API',
               'description': 'API main page'}
    return render(request, 'api/main_API.html', context)


def update_cats(request):
    tr1 = Thread(target=get_catalogs_wb_for_db, daemon=True, kwargs=dict())
    # print('Thread started')
    tr1.start()
    tr1.join()
    # print('Thread Stopped')

    context = {'title': 'API',
               'description': 'Cats Updated'}
    return render(request, 'api/main_API.html', context)


def update_prod(request):
    cat_list = Category.objects.all()[:10]

    for cat in cat_list:
        # print(cat)
        # get_product_for_db(shard=cat.shard, query=cat.query, cat=cat.id)
        t1 = Thread(target=get_product_for_db, daemon=True,
                    kwargs=dict(shard=cat.shard, query=cat.query, cat=cat.id))
        t1.start()  # Вроде работает
        # t1.join()
        print(f'{cat} - STOPPED----------')

    context = {'title': 'API',
               'description': 'Prods Updated'}
    return render(request, 'api/main_API.html', context)


def update_pr(request):
    counter = 1
    context = {'title': 'API',
               'description': 'Img updated'}
    prods = Product.objects.all()
    for prod in prods:
        prod.img = get_image(prod.id)
        prod.save()
        counter += 1
    print(f'{counter} - prods Updated')
    return render(request, 'api/main_API.html', context)


