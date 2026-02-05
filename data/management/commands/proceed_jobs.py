from django.core.management.base import BaseCommand
import pandas as pd
from collections import defaultdict

from data.models import Research, Sample


class Command(BaseCommand):
    help = 'Выполняет задания из excel-файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Путь к excel-файлу'
        )

    def handle(self, *args, **options):
        file_path = options['excel_file']
        try:
            df = pd.read_excel(file_path, sheet_name=0)
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Ошибка при чтении файла: {e}'))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Файл {file_path} успешно прочитан. Задач: {len(df)}'))

        for index, row in df.iterrows():
            researches = row['researches']
            full_loci = row['full_loci']
            partial_loci = row['partial_loci']
            output = row['output']

            researches_list = [int(float(x)) for x in str(researches).split('.') if str(x).lower() != 'nan']
            full_loci_list = [x.strip() for x in str(full_loci).split(',') if str(x).lower() != 'nan']
            partial_loci_list = [x.strip() for x in str(partial_loci).split(',') if str(x).lower() != 'nan']
                
            self.stdout.write('Загружаем исследования...')

            research_1 = Research.objects.get(number=researches_list[0])
            research_2 = Research.objects.get(number=researches_list[1])

            self.stdout.write('Загружаем образцы...')

            samples = Sample.objects.filter(
                research__in=[research_1, research_2]
            ).prefetch_related('loci')

            # структура:
            # key -> {
            #   total: int,
            #   r1: int,
            #   r2: int
            # }
            haplotypes = defaultdict(lambda: {
                'total': 0,
                'r1': 0,
                'r2': 0
            })

            self.stdout.write('Считаем гаплотипы...')

            for sample in samples:
                key_parts = []

                for locus in sample.loci.all():
                    if locus.name in full_loci_list:
                        key_parts.append(
                            (locus.name, locus.coef1, locus.coef2)
                        )
                    elif locus.name in partial_loci_list:
                        key_parts.append(
                            (locus.name, locus.coef1, None)
                        )

                haplotype_key = frozenset(key_parts)

                count = sample.people_amount or 0

                haplotypes[haplotype_key]['total'] += count

                if sample.research_id == research_1.id:
                    haplotypes[haplotype_key]['r1'] += count
                else:
                    haplotypes[haplotype_key]['r2'] += count

            self.stdout.write('Готовим Excel...')

            rows = []

            for loci_set, data in haplotypes.items():
                haplotype_str = '-'.join(
                    f'{name}*{c1}:{c2}' if c2 else f'{name}*{c1}'
                    for name, c1, c2 in sorted(loci_set)
                )

                rows.append({
                    'Гаплотип': haplotype_str,
                    'Всего человек': data['total'],
                    f'Исследование {researches_list[0]}': data['r1'],
                    f'Исследование {researches_list[1]}': data['r2'],
                })

            df = pd.DataFrame(rows)
            df = df.sort_values('Всего человек', ascending=False)

            df.to_excel(f'results/{output}', index=False)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Готово! Файл сохранён как {output}'
                )
            )
