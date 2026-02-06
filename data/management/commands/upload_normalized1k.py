from django.core.management.base import BaseCommand
import pandas as pd
import os

from data.models import NormalizedHaplotype1k


class Command(BaseCommand):
    help = 'Выгружает нормализованные гаплотипы по Excel-заданию'

    def add_arguments(self, parser):
        parser.add_argument(
            'task_file',
            type=str,
            help='Путь к Excel-файлу с заданиями (research и format_code)'
        )

    def handle(self, *args, **options):
        task_file = options['task_file']

        try:
            tasks_df = pd.read_excel(task_file)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при чтении файла: {e}'))
            return

        os.makedirs('results', exist_ok=True)

        for idx, task in tasks_df.iterrows():
            research_number = int(task['research'])
            format_code = str(task['format_code']).strip()

            self.stdout.write(f'Обрабатываем исследование {research_number}, формат {format_code}')

            queryset = NormalizedHaplotype1k.objects.filter(
                research1k__number=research_number,
                format_code1k=format_code
            ).select_related('research1k')

            if not queryset.exists():
                self.stdout.write(self.style.WARNING(
                    f'Нет данных для исследования {research_number} и формата {format_code}'
                ))
                continue

            rows = []
            for nh in queryset:
                rows.append({
                    'haplotype': nh.haplotype_str1k,
                    'people_amount': nh.people_amount1k,
                    'research': nh.research1k.number,
                    'format_code': nh.format_code1k,
                })

            df = pd.DataFrame(rows)

            # Суммируем одинаковые гаплотипы
            df = df.groupby(['haplotype', 'research', 'format_code'], as_index=False) \
                   .agg({'people_amount': 'sum'})

            df = df.sort_values(['research', 'haplotype'])

            # Имя файла: Research_номер_формат.xlsx
            format_safe = format_code.replace('*', '').replace('-', '_')
            output_file = f'results/Research{research_number}_{format_safe}1k.xlsx'

            df.to_excel(output_file, index=False)
            self.stdout.write(self.style.SUCCESS(f'Файл сохранён как {output_file}'))