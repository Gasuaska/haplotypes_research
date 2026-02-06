from django.core.management.base import BaseCommand
import pandas as pd

from data.models import Research, Sample

class Command(BaseCommand):
    help = 'Нормализует выбранные исследования: оставляет только A, B, C, DRB1 и сортирует их в нужном порядке'

    def add_arguments(self, parser):
        parser.add_argument(
            'research_numbers',
            type=str,
            help='Номера исследований через запятую, например "9,16"'
        )

    def handle(self, *args, **options):
        numbers_str = options['research_numbers']
        research_numbers = [int(x.strip()) for x in numbers_str.split(',') if x.strip().isdigit()]
        researches = Research.objects.filter(number__in=research_numbers)

        self.stdout.write(f'Найдено исследований: {researches.count()}')

        samples = Sample.objects.filter(
            research__in=researches
        ).prefetch_related('loci')

        rows = []

        for sample in samples:
            loci_dict = {locus.name: locus for locus in sample.loci.all()}

            # Порядок локусов
            order_names = ['A', 'B', 'C', 'DRB1']
            ordered_loci = [loci_dict[name] for name in order_names if name in loci_dict]

            # Формируем строку гаплотипа
            parts = []
            for locus in ordered_loci:
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
        output_file = 'results/Normalized_ABC_DRB1.xlsx'
        df.to_excel(output_file, index=False)

        self.stdout.write(self.style.SUCCESS(
            f'Готово! Файл сохранён как {output_file}'
        ))