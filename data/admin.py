from django.contrib import admin
from .models import Research, Sample, Locus

class LocusInline(admin.TabularInline):
    model = Locus
    extra = 0
    readonly_fields = ('name', 'coef1', 'coef2', 'raw_coef')

class SampleInline(admin.TabularInline):
    model = Sample
    extra = 0
    readonly_fields = ('haplotype', 'people_amount')
    inlines = [LocusInline]

@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ('number', 'people_amount', 'sample_count')
    inlines = [SampleInline]

    def sample_count(self, obj):
        return obj.samples.count()
    sample_count.short_description = "Кол-во образцов"

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('haplotype', 'research', 'people_amount', 'locus_count')
    list_filter = ('research',)
    search_fields = ('haplotype',)

    inlines = [LocusInline]

    def locus_count(self, obj):
        return obj.loci.count()
    locus_count.short_description = "Кол-во локусов"

@admin.register(Locus)
class LocusAdmin(admin.ModelAdmin):
    list_display = (
        'sample',
        'name',
        'sample__research',
        'coef1',
        'coef2',
        'raw_coef',)
    list_filter = ('name',)
    search_fields = ('sample__haplotype', 'name')
    ordering = ('id',)