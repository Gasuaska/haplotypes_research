from django.core.management.base import BaseCommand
from collections import defaultdict
import pandas as pd

from data.models import Research, Sample


class Command(BaseCommand):
    help = 'Автоматически сравнивает гаплотипы между двумя исследованиями'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Путь к excel-файлу с заданиями'
        )

    def handle(self, *args, **options):
        EXCLUDED_LOCI = {'A', 'B'}

        file_path = options['excel_file']

        try:
            df_tasks = pd.read_excel(file_path, sheet_name=0)
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Ошибка при чтении файла: {e}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Файл {file_path} прочитан. Задач: {len(df_tasks)}'
            )
        )

        for _, row in df_tasks.iterrows():
            researches = row['researches']
            output = row['output']

            researches_list = [
                int(float(x))
                for x in str(researches).split('.')
                if str(x).lower() != 'nan'
            ]

            if len(researches_list) != 2:
                self.stderr.write(
                    self.style.ERROR('Нужно указать ровно 2 исследования')
                )
                continue

            research_1 = Research.objects.get(number=researches_list[0])
            research_2 = Research.objects.get(number=researches_list[1])

            self.stdout.write(
                f'Сравниваем исследования {research_1.number} и {research_2.number}'
            )

            samples = Sample.objects.filter(
                research__in=[research_1, research_2]
            ).prefetch_related('loci')

            # ---------- 1. собираем данные по локусам ----------
            locus_data = {
                research_1.id: defaultdict(set),
                research_2.id: defaultdict(set),
            }

            for sample in samples:
                for locus in sample.loci.all():
                    if locus.name in EXCLUDED_LOCI:
                        continue

                    locus_data[sample.research_id][locus.name].add(
                        (locus.coef1, locus.coef2)
                    )

            # ---------- 2. определяем full / partial ----------
            full_loci = set()
            partial_loci = set()

            for locus_name in locus_data[research_1.id]:
                set1 = locus_data[research_1.id][locus_name]
                set2 = locus_data[research_2.id].get(locus_name, set())

                if not set2:
                    continue

                if set1 == set2:
                    full_loci.add(locus_name)
                else:
                    coef1_1 = {c1 for c1, _ in set1}
                    coef1_2 = {c1 for c1, _ in set2}

                    if coef1_1 & coef1_2:
                        partial_loci.add(locus_name)

            self.stdout.write(
                f'FULL локусы: {", ".join(sorted(full_loci))}'
            )
            self.stdout.write(
                f'PARTIAL локусы: {", ".join(sorted(partial_loci))}'
            )

            # ---------- 3. считаем гаплотипы ----------
            haplotypes = defaultdict(lambda: {
                'total': 0,
                'r1': 0,
                'r2': 0
            })

            for sample in samples:
                key_parts = []

                for locus in sample.loci.all():
                    if locus.name in EXCLUDED_LOCI:
                        continue
                    if locus.name in full_loci:
                        key_parts.append(
                            (locus.name, locus.coef1, locus.coef2)
                        )
                    elif locus.name in partial_loci:
                        key_parts.append(
                            (locus.name, locus.coef1, None)
                        )

                if not key_parts:
                    continue

                haplotype_key = frozenset(key_parts)
                count = sample.people_amount or 0

                haplotypes[haplotype_key]['total'] += count

                if sample.research_id == research_1.id:
                    haplotypes[haplotype_key]['r1'] += count
                else:
                    haplotypes[haplotype_key]['r2'] += count

            # ---------- 4. готовим Excel ----------
            rows = []

            for loci_set, data in haplotypes.items():
                haplotype_str = '-'.join(
                    f'{name}*{c1}:{c2}' if c2 else f'{name}*{c1}'
                    for name, c1, c2 in sorted(loci_set)
                )

                rows.append({
                    'Гаплотип': haplotype_str,
                    'Всего человек': data['total'],
                    f'Исследование {research_1.number}': data['r1'],
                    f'Исследование {research_2.number}': data['r2'],
                })

            result_df = pd.DataFrame(rows)
            result_df = result_df.sort_values(
                'Всего человек', ascending=False
            )

            result_df.to_excel(f'results/{output}', index=False)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Готово! Файл сохранён как results/{output}'
                )
            )
