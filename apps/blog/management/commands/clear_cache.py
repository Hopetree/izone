# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clears cache for specified keys or clears keys like views.*.statistics.* if none provided'

    def add_arguments(self, parser):
        parser.add_argument('keys', nargs='*', type=str, help='Keys to clear from cache')

    def handle(self, *args, **options):
        keys_to_clear = options['keys']

        if not keys_to_clear:
            # If no keys provided, clear keys matching the pattern
            keys_matching_pattern = cache.keys('views.*.statistics.*')

            if keys_matching_pattern:
                for key in keys_matching_pattern:
                    cache.delete(key)
                    self.stdout.write(
                        self.style.SUCCESS(f'Cache cleared successfully for key: {key}'))
            else:
                self.stdout.write(self.style.SUCCESS('No matching keys found to clear'))
        else:
            # Clear cache for each specified key
            for key in keys_to_clear:
                cache.delete(key)
                self.stdout.write(self.style.SUCCESS(f'Cache cleared successfully for key: {key}'))
