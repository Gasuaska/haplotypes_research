from django.core.management.base import BaseCommand
import pandas as pd

from data.models import Sample, Research


class Command(BaseCommand):
    help = 'Импортирует образцы из excel-файла'

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
                f'Файл {file_path} успешно прочитан. Строк: {len(df)}'))

        for index, row in df.iterrows():
            haplotype = row['haplotype']
            people_amounth = row['people_amounth']
            research = row['research']
            research_object = Research.objects.get(number=research)
            sample = Sample.objects.create(
                haplotype = haplotype,
                people_amounth=people_amounth,
                research = research_object
            )
        self.stdout.write(self.style.SUCCESS('Импорт данных завершён.'))