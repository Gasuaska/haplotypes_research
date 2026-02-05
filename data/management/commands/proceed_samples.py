from django.core.management.base import BaseCommand
import re

from data.models import Locus, Sample


class Command(BaseCommand):
    help = 'Разбивает гаплотип на аллели'

    def handle(self, *args, **options):
        samples = Sample.objects.all()
        for sample in samples:
            haplotype = sample.haplotype
            alleles = re.findall(r'([A-Z0-9]+)\*([0-9:/]+)', haplotype)
            for allele in alleles:
                name = allele[0]
                raw_coeff = allele[1]

                if '/' in raw_coeff:
                    coef1 = None
                    coef2 = None
                else:
                    coef_splited = raw_coeff.split(':')
                    # левый коэф
                    if len(coef_splited[0]) > 2:  # 1 и 2 слиплись
                        coef1 = coef_splited[0][0:2]
                        coef2 = coef_splited[0][2:4]
                    else:
                        coef1 = coef_splited[0]
                        # правый коэф
                        if len(coef_splited) < 2 or coef_splited[1] == '':
                            coef2 = None
                        else:
                            if len(coef_splited[1]) > 2:  # 2 и 3 слиплись
                                coef2 = coef_splited[1][0:1]
                            else:
                                coef2 = coef_splited[1]

                locus = Locus.objects.create(
                    sample=sample,
                    name=name,
                    coef1=coef1,
                    coef2=coef2,
                    raw_coef=raw_coeff
                )
                self.stdout.write(self.style.SUCCESS('Обработка образцов завершена.'))