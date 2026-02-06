from django.db import models


class Research(models.Model):
    number = models.IntegerField(verbose_name='Номер исследования')
    people_amount = models.IntegerField(verbose_name='Количество человек')
    def __str__(self):
        return f'Research #{self.number}'

class Sample(models.Model):
    haplotype = models.CharField(verbose_name='Название')
    people_amount = models.IntegerField(verbose_name='Числовое значение')
    research = models.ForeignKey(
        Research,
        on_delete=models.CASCADE,
        related_name='samples',
        verbose_name = 'Исследование'
    )

    def __str__(self):
        return f'Sample #{self.id} {self.haplotype} ({self.people_amount})'


class Locus(models.Model):
    sample = models.ForeignKey(
        Sample,
        on_delete=models.CASCADE,
        related_name='loci'
    )
    name = models.CharField(
        max_length=10,
        verbose_name='Локус'
        )

    coef1 = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Коэффициент 1, есть всегда')
    coef2 = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Коэффициент2')

    raw_coef = models.CharField(
        max_length=20,
        verbose_name='Сырой коэффициент',
    )

    class Meta:
        unique_together = ('sample', 'name', 'coef1', 'coef2')

    def __str__(self):
        return f'{self.name}*{self.coef1}:{self.coef2} ({self.sample})'