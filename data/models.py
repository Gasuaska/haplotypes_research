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


class NormalizedHaplotype(models.Model):
    research = models.ForeignKey(
        'Research',
        on_delete=models.CASCADE,
        related_name='normalized_haplotypes'
    )

    format_code = models.CharField(max_length=50)

    haplotype_str = models.CharField(max_length=255)

    people_amount = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('research', 'format_code', 'haplotype_str')
        ordering = ['research', 'format_code', 'haplotype_str']

    def __str__(self):
        return f'{self.research.number}|{self.format_code}|{self.haplotype_str}'


class NormalizedHaplotype1k(models.Model):
    research1k = models.ForeignKey(
        'Research', 
        on_delete=models.CASCADE,
        related_name='normalized_haplotypes1k'
    )

    format_code1k = models.CharField(max_length=50)

    haplotype_str1k = models.CharField(max_length=255)

    people_amount1k = models.PositiveIntegerField(default=0)
    notes1k = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('research1k', 'format_code1k', 'haplotype_str1k')
        ordering = ['research1k', 'format_code1k', 'haplotype_str1k']

    def __str__(self):
        return f'{self.research1k.number}|{self.format_code1k}|{self.haplotype_str1k}'
