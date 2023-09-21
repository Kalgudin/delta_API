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
from .views import main, update_cats, update_prod, CategoryAPIView, CategoryAPIUpdate, CategoryViewSet

router = routers.SimpleRouter()
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', main, name='API'),
    path('v1/delta', main, name='API'),
    path('v1/delta/', include(router.urls)),  # http://127.0.0.1:8000/api/v1/delta/categories/ -list # /12324 -element
    path('v1/delta/WomenAPIView', CategoryViewSet.as_view({'get': 'list'}), name='CategoryList'),
    path('v1/delta/WomenAPIView/<int:pk>', CategoryViewSet.as_view({'put': 'update', 'get': 'retrieve'}), name='CategoryGetUpdate'),
    # path('v1/delta/WomenAPIView', CategoryAPIView.as_view(), name='CategoryAPIView'),
    # path('v1/delta/WomenAPIView/<int:pk>', CategoryAPIUpdate.as_view(), name='CategoryAPIUpdate'),
#     path('v1/delta/update_cats', update_cats, name='update_cats'),
#     path('v1/delta/update_prod', update_prod, name='update_prod'),
]
