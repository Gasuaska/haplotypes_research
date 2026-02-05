from collections import defaultdict
from data.models import Research, Sample, Locus

def group_haplotypes(samples, full_match, partial_match):

    haplotypes = defaultdict(int)

    for sample in samples:
        loci = sample.loci.all()

        key_parts = []

        for locus in loci:
            if locus.name in full_match:
                key_parts.append(
                    (locus.name, locus.coef1, locus.coef2)
                )
            elif locus.name in partial_match:
                key_parts.append(
                    (locus.name, locus.coef1, None)
                )

        haplotype_key = frozenset(key_parts)
        haplotypes[haplotype_key] += sample.people_amounth

    return haplotypes