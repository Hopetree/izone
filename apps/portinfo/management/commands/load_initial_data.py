import json
import os
from django.core.management.base import BaseCommand
from portinfo.models import Port


class Command(BaseCommand):
    help = 'Load initial port data from ports.json'

    def handle(self, *args, **options):
        with open(os.path.join(os.path.dirname(__file__), 'ports.json'), 'r',
                  encoding='utf-8') as file:
            port_data = json.load(file)

        for entry in port_data:
            port_number = entry.get('port_number')
            protocol = entry.get('protocol')
            service_name = entry.get('service_name')
            description = entry.get('description')
            default_status = entry.get('default_status')
            common_usage = entry.get('common_usage')
            notes = entry.get('notes')

            port, created = Port.objects.update_or_create(
                port_number=port_number,
                protocol=protocol,
                service_name=service_name,
                defaults={
                    'description': description,
                    'default_status': default_status,
                    'common_usage': common_usage,
                    'notes': notes
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created port {port_number}/{protocol}'))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated port {port_number}/{protocol}'))

        self.stdout.write(self.style.SUCCESS('Successfully loaded port data'))
