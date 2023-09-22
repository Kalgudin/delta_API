from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, default='', verbose_name='название', db_index=True)
    url = models.CharField(max_length=1000, default='', verbose_name='url')
    shard = models.CharField(max_length=100, default='', verbose_name='shard')
    query = models.CharField(max_length=800, default='', verbose_name='query')
    parent_cat = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True, default=None)
    updated_at = models.IntegerField(null=True, blank=True)
    total_views = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Категории"

    def counter(self):
        self.total_views += 1
        self.save()

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='ИД продукта')
    name = models.CharField(max_length=100, verbose_name='Наименование', default='', db_index=True)
    base_price = models.IntegerField(verbose_name='базовая цена', default=0)
    sale_price = models.IntegerField(verbose_name='цена со скидкой', default=0, db_index=True)
    average_price = models.IntegerField(verbose_name='Средняя цена', default=0)
    sale = models.IntegerField(verbose_name='Скидка от средней цены', default=0, db_index=True)
    all_prices = models.JSONField(verbose_name='Список цен', default=dict)
    # brand = models.CharField(max_length=100, verbose_name='Бренд', default='')
    # brand_id = models.IntegerField(verbose_name='ИД бренда', default=0)
    feedbacks = models.IntegerField(verbose_name='колличество отзывов', default=0)
    rating = models.IntegerField(verbose_name='рейтинг', default=0)
    url = models.CharField(max_length=300, verbose_name='url', blank=True)
    category = models.ManyToManyField(Category, verbose_name='список категорий', blank=True)  # олучилось дольше, чем со строкой

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Товары"


class Visitors(models.Model):
    ip = models.CharField(max_length=50)  #, verbose_name='IP посетителя', default='', db_index=True)
    count = models.IntegerField(default=0) #, verbose_name='количество посещенй')
    last_visit = models.IntegerField(default=0) #, verbose_name='последнее посещение', null=True, blank=True)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name_plural = "Посетители"


class Constants(models.Model):
    sale = models.IntegerField(default=15, verbose_name='размер минимальной скидки отображаемого товара на странице')
    paginate = models.IntegerField(default=20, verbose_name='количество товара на одной странице')
    pages = models.IntegerField(default=50, verbose_name='количество страниц поиска товаров на Wildberries')
    cache_time = models.IntegerField(default=60, verbose_name='время кэширования в секундах')

    class Meta:
        verbose_name_plural = "Константы"


try:
    MIN_SALE = Constants.objects.first().sale  # размер минимальной скидки отображаемого товара на странице
    PAGINATE = Constants.objects.first().paginate  # количество товара на одной странице
    CAT_PAGES = Constants.objects.first().pages  # количество страниц поиска товаров на Wildberries
    CACHE_TIME = Constants.objects.first().cache_time  # время кэширования в секундах
except Exception as ex:
    # print('Первый запуск, установите значения в модели "Константы" и перезапустите сервер.', ex)
    MIN_SALE = 15
    PAGINATE = 20
    CAT_PAGES = 4
    CACHE_TIME = 60