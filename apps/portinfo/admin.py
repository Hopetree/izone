from django.contrib import admin
from .models import Port


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ['port_number', 'protocol', 'service_name', 'description']
    list_filter = ('protocol',)
    search_fields = ['port_number', 'protocol', 'service_name']
