from django.core.management.base import BaseCommand
import pandas as pd

from data.models import Research


class Command(BaseCommand):
    help = 'Импортирует данные по исследованиям из excel-файла'

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
            study_number = row['research']
            people_amounth = row['people_amounth']

            study, created = Research.objects.get_or_create(
                number=study_number,
                defaults={'people_amounth': people_amounth}
            )
            if not created:
                study.people_amounth = people_amounth
                study.save()
                self.stdout.write(f'Обновлено исследование {study_number}')
            else:
                self.stdout.write(f'Создано исследование {study_number}')

        self.stdout.write(self.style.SUCCESS('Импорт исследований завершён.'))