from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.apps import apps

class Command(BaseCommand):
    help = 'Fix foreign key references to use the correct user model'

    def handle(self, *args, **options):
        # Get the user model
        User = apps.get_model(settings.AUTH_USER_MODEL)
        
        # Get the first user (you might need to adjust this based on your setup)
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
                
            if not admin_user:
                self.stdout.write(self.style.ERROR('No users found in the database. Please create a user first.'))
                return
                
            self.stdout.write(f'Using user {admin_user.email} (ID: {admin_user.id}) for fixing references')
            
            # Fix ChannelParticipant
            from apps.chat.models import ChannelParticipant
            
            # Update any null user references to the admin user
            updated = ChannelParticipant.objects.filter(user__isnull=True).update(user=admin_user)
            if updated > 0:
                self.stdout.write(self.style.SUCCESS(f'Updated {updated} ChannelParticipant records with null user'))
            
            # Check for any remaining invalid user references
            invalid_participants = ChannelParticipant.objects.exclude(
                user__in=User.objects.all()
            )
            
            if invalid_participants.exists():
                self.stdout.write(self.style.WARNING(
                    f'Found {invalid_participants.count()} ChannelParticipant records with invalid user references. '
                    'These will be deleted.'
                ))
                deleted_count, _ = invalid_participants.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} invalid ChannelParticipant records'))
            
            self.stdout.write(self.style.SUCCESS('Successfully fixed foreign key references'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fixing foreign keys: {str(e)}'))
            raise
