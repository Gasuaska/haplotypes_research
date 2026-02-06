from django.core.management.base import BaseCommand
import pandas as pd

from data.models import Research, Sample

class Command(BaseCommand):
    help = ('Генерирует Excel с гаплотипами в порядке A->B->C->DRB1/DQA1/DQB1'
    'для выбранных исследований')

    def handle(self, *args, **options):
        research_numbers = [9, 16]  # или любые другие исследования
        researches = Research.objects.filter(number__in=research_numbers)

        self.stdout.write(f'Найдено исследований: {researches.count()}')

        samples = Sample.objects.filter(
            research__in=researches
        ).prefetch_related('loci')

        rows = []

        for sample in samples:
            loci_dict = {locus.name: locus for locus in sample.loci.all()}

            # Определяем порядок локусов
            order = []
            for locus_name in ['A', 'B', 'C']:
                if locus_name in loci_dict:
                    order.append(loci_dict[locus_name])
            # Добавляем все остальные локусы, которые не A/B/C, сортируем по имени
            other_loci = [l for l_name, l in loci_dict.items() if l_name not in ['A', 'B', 'C']]
            other_loci_sorted = sorted(other_loci, key=lambda x: x.name)
            order.extend(other_loci_sorted)

            # Формируем строку гаплотипа
            parts = []
            for locus in order:
                if locus.coef1 is None:
                    continue
                if locus.coef2:
                    parts.append(f'{locus.name}*{locus.coef1}:{locus.coef2}')
                else:
                    parts.append(f'{locus.name}*{locus.coef1}')

            haplotype_str = '-'.join(parts)

            rows.append({
                'sample_id': sample.id,
                'haplotype': haplotype_str,
                'people_amount': sample.people_amount,
                'research': sample.research.number,
            })

        df = pd.DataFrame(rows)
        output_file = 'results/Research_Normalized_ABC.xlsx'
        df.to_excel(output_file, index=False)

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Файл сохранён как {output_file}'
        ))
