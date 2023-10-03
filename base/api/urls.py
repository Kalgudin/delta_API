"""
URL configuration for base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import main, CategoryViewSet, ProductViewSetPublic, CategoryViewSetPublic, update_prod, update_pr, \
    CatForMenuViewSet

router = routers.SimpleRouter()
# router.register(r'categories', CategoryViewSetPublic, basename='categories')
router.register(r'products', ProductViewSetPublic, basename='products')

urlpatterns = [
    path('', main, name='API'),
    path('v1/delta/', main, name='API'),
    path('v1/delta/', include(router.urls)),  # http://127.0.0.1:8000/api/v1/delta/products/ -list # /6994 -element
    path('v1/delta/childs/<int:pk>/', CatForMenuViewSet.as_view()),  # http://127.0.0.1:8000/api/v1/delta/categories/0 -list

    path('v1/delta/childs_categories/<int:pk>/', CategoryViewSetPublic.as_view({'get': 'list'})),  # НЕ ИСПОЛЬЗУЕТСЯ


    # path('v1/delta/WomenAPIView', CategoryViewSet.as_view({'get': 'list'}), name='CategoryList'),
    # path('v1/delta/WomenAPIView/<int:pk>', CategoryViewSet.as_view({'put': 'update', 'get': 'retrieve'}), name='CategoryGetUpdate'),
    # path('v1/delta/WomenAPIView', CategoryAPIView.as_view(), name='CategoryAPIView'),
    # path('v1/delta/WomenAPIView/<int:pk>', CategoryAPIUpdate.as_view(), name='CategoryAPIUpdate'),
    # path('v1/delta/update_pr', update_pr, name='update_pr'),
    # path('v1/delta/update_prod', update_prod, name='update_prod'),
]
