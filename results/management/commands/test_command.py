from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger("general_manage_logs")


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
