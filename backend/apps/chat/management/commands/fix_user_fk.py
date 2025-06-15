from django.core.management.base import BaseCommand
from apps.chat.api.services import fix_foreign_key_constraints


class Command(BaseCommand):
    help = 'Fix foreign key constraints for chat_channelparticipant table'

    def handle(self, *args, **options):
        result = fix_foreign_key_constraints()
        
        if result["status"] == "success":
            self.stdout.write(self.style.SUCCESS(result["message"]))
        else:
            self.stdout.write(self.style.ERROR(f"Error: {result['message']}"))
