from django.core.management.base import BaseCommand

from nasdaqstat.utils import scraper


class Command(BaseCommand):
    help = 'My scraper'

    def add_arguments(self, parser):
        parser.add_argument(
            '-th',
            action='store',
            nargs=1,
            type=int,
            default=1,
        )

    def handle(self, *args, **options):
        threads = options['th'][0]
        scraper(threads)
