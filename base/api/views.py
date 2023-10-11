from threading import Thread

from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from .category_def import get_catalogs_wb_for_db
from .proucts_def import get_product_for_db, get_image, get_average_price
from rest_framework import generics, viewsets, mixins
from .models import Category, Product
from .serializers import CategorySerializer, CategoryAllSerializer, ProductSerializer, CategoryParentSerializer


class ProductsAPIPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProductViewSetPublic(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(sale__gte=0)
    serializer_class = ProductSerializer
    pagination_class = ProductsAPIPagination


class CategoryViewSetPublic(mixins.ListModelMixin, GenericViewSet):  # не используется
    serializer_class = CategorySerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk") if self.kwargs.get("pk") != 0 else None
        cat_list = Category.objects.filter(parent_cat=pk)
        print(cat_list)
        return cat_list


class CatForMenuViewSet(APIView):
    def get(self, request, pk):
        if not pk:
            cat_list = Category.objects.filter(parent_cat=None)
            parent = None
            grand = None
        else:
            cat_list = Category.objects.filter(parent_cat=pk)
            parent = Category.objects.get(pk=pk)
            grand = {'name': parent.parent_cat.name, 'id': parent.parent_cat.id} if parent.parent_cat else None
            parent = {'name': parent.name, 'id': parent.id} if parent else None

        return Response({'posts': CategorySerializer(cat_list, many=True).data, 'parent': parent, 'grand': grand})


class CategoryDetailPublic(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryParentSerializer


class CategoryViewSet(mixins.CreateModelMixin,  # Удаляем и добавляем миксины в зависимости от функционала
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class CategoryAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class CategoryAPIUpdate(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


def main(request):
    print(encode())
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
    t1 = Thread(target=_cat_update_in_threads, daemon=True)
    t1.start()
    context = {'title': 'API',
               'description': 'Prods Updated'}
    return render(request, 'api/main_API.html', context)


def _cat_update_in_threads():
    cat_list = Category.objects.all()[71:80]
    # print(f'IN _cat_update_in_threads == catList - >  {cat_list}')
    for cat in cat_list:
        get_product_for_db(shard=cat.shard, query=cat.query, cat=cat.id)
        print(f'{cat} / {cat.name} - STOPPED----------')


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
