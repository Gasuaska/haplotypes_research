from django.core.management.base import BaseCommand
import pandas as pd

from data.models import Research, Sample


class Command(BaseCommand):
    help = 'Вырезает аллели A и B из первого исследования'

    def handle(self, *args, **options):
        LOCUS_ORDER = ['DRB1', 'DQA1', 'DQB1']
        research = Research.objects.get(number=1)
        samples = Sample.objects.filter(
            research=research).prefetch_related('loci')

        rows = []
        for sample in samples:
            loci = list(sample.loci.all())
            loci.sort(
                key=lambda locus: LOCUS_ORDER.index(locus.name)
                if locus.name in LOCUS_ORDER else 999
            )
            parts = []
            for locus in loci:
                if locus.name == 'A' or locus.name == 'B':
                    continue

                if locus.coef1 is None:
                    continue

                if locus.coef2:
                    parts.append(
                        f'{locus.name}*{locus.coef1}:{locus.coef2}'
                    )
                else:
                    parts.append(
                        f'{locus.name}*{locus.coef1}'
                    )

            haplotype_str = '-'.join(parts)

            rows.append({
                'haplotype': haplotype_str,
                'people_amount': sample.people_amount,
                'research': research.number,
            })

        df = pd.DataFrame(rows)

        df.to_excel(f'results/Research1WithoutAB.xlsx', index=False)

        self.stdout.write(
            self.style.SUCCESS(
                'Готово! Файл сохранён как Research1WithoutAB.xlsx'
            )
        )
