from django.core.management.base import BaseCommand
import pandas as pd

from data.models import Research, Sample, NormalizedHaplotype1k


class Command(BaseCommand):
    help = 'Нормализует исследования по format_code и сохраняет в NormalizedHaplotype1k'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Excel-файл с колонками research, format_code'
        )

    def handle(self, *args, **options):
        df = pd.read_excel(options['excel_file'])

        for _, row in df.iterrows():
            research_number1k = int(row['research'])
            format_code1k = row['format_code'].strip()
            locus_order = format_code1k.split('-')

            self.stdout.write(
                f'Нормализуем исследование {research_number1k} → {format_code1k}'
            )

            research = Research.objects.get(number=research_number1k)

            samples = Sample.objects.filter(research=research).prefetch_related('loci')

            rows = []

            for sample in samples:
                loci_map = {}
                for locus in sample.loci.all():
                    if locus.name not in locus_order:
                        continue
                    if locus.raw_coef and '/' in locus.raw_coef:
                        loci_map[locus.name] = f'{locus.name}*{locus.raw_coef}'
                    elif locus.coef1:
                        if locus.name == 'DRB1':
                            loci_map[locus.name] = f'{locus.name}*{locus.coef1}'
                        else:
                            if locus.coef2:
                                loci_map[locus.name] = f'{locus.name}*{locus.coef1}:{locus.coef2}'
                            else:
                                loci_map[locus.name] = f'{locus.name}*{locus.coef1}'
                if not loci_map:
                    continue
                haplotype_str = '-'.join([loci_map[name] for name in locus_order if name in loci_map])
                rows.append({
                    'haplotype_str': haplotype_str,
                    'people_amount': sample.people_amount or 0,
                })

            if not rows:
                continue

            df_tmp = pd.DataFrame(rows)
            grouped = df_tmp.groupby('haplotype_str', as_index=False).agg({'people_amount': 'sum'})

            for _, r in grouped.iterrows():
                obj, created = NormalizedHaplotype1k.objects.get_or_create(
                    research1k=research,
                    format_code1k=format_code1k,
                    haplotype_str1k=r['haplotype_str'],
                    defaults={'people_amount1k': int(r['people_amount'])}
                )
                if not created:
                    obj.people_amount1k += int(r['people_amount'])
                    obj.save()