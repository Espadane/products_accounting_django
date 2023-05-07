from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError



class Product(models.Model):
    name = models.CharField(max_length=100, unique=True, 
                            verbose_name='Название товара')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self) -> str:
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=50, unique=True, 
                            verbose_name='Название точки')
    head_of_store = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        verbose_name='Ответственный',
        related_name='stores'
    )

    class Meta:
        verbose_name = 'Торговая точка'
        verbose_name_plural = 'Торговые точки'

    def __str__(self) -> str:
        return self.name


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    store = models.ForeignKey(Store, on_delete=models.PROTECT, verbose_name='Торговая точка')
    quantity = models.IntegerField(verbose_name='Количество')
    minimum_quantity = models.PositiveIntegerField(default=0, verbose_name='Минимальное количество')

    class Meta:
        verbose_name = 'Товар на точке'
        verbose_name_plural = 'Товары на точке'
        unique_together = ('product', 'store')

    def __str__(self) -> str:
        return f'{self.product}'


class Transfer(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Товар')
    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name='transfers_from',
        verbose_name='Торговая точка'
    )
    starting_quantity = models.IntegerField(
        verbose_name='Начальное количество товара'
    )
    difference = models.IntegerField(
        verbose_name='Изменение количества товара'
    )
    ending_quantity = models.IntegerField(
        verbose_name='Конечное количество товара',
        editable=False
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата перемещения')
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Пользователь',
        related_name='transfers_made'
    )
    comment = models.CharField(
        max_length=100,
        default='',
        blank=True,
        verbose_name='Комментарий'
    )

    class Meta:
        verbose_name = 'Перемещение'
        verbose_name_plural = 'Перемещения'

    def save(self, *args, **kwargs):
        if self.starting_quantity is not None and self.difference is not None:
            self.ending_quantity = self.starting_quantity + self.difference
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product}'
