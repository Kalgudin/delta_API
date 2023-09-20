from django.test import TestCase
from .models import Category, Product

NUMBER_OF_CATS = 3
NUMBER_OF_ITEMS = 10


class TestDelta(TestCase):
    @classmethod
    def setUpTestData(cls):
        for item_index in range(NUMBER_OF_CATS):
            Category.objects.create(
                name = (str(item_index) + ' Name'),
                url = (str(item_index) + ' URL'),
                shard = (str(item_index) + ' Shard'),
                query = (str(item_index) + ' Query'),
            )
        for prod_index in range(NUMBER_OF_ITEMS):
            Product.objects.create(
                id = prod_index,
                name = (str(prod_index) + ' Name'),
                sale_price = 100,
                sale = 50,
                url = (str(prod_index) + ' URL'),
            )

    def test_index(self):
        response = self.client.get('/')  # получаем ответ браузера
        self.assertEquals(200, response.status_code)  # простая проверка кода ответа
        self.assertTemplateUsed(response, 'main/index.html')  # проверка тот ли шаблон используется

    def test_index_contains(self):
        response = self.client.get('/')  # получаем ответ браузера
        self.assertIn('Created by Nick-Ka', response.content.decode())  #  получаем контент в байтах и декодируем в строку

    def test_index_content(self):
        response = self.client.get('/')  # получаем ответ браузера
        print(response.context['products'])
        self.assertEquals(NUMBER_OF_CATS, len(response.context['category']))
        self.assertEquals(NUMBER_OF_ITEMS, len(response.context['products']))