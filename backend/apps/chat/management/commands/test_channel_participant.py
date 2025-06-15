from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from apps.chat.models import ChatChannel, ChannelParticipant

class Command(BaseCommand):
    help = 'Test creating a channel participant'

    def handle(self, *args, **options):
        with schema_context('turtlesoftware'):
            # Get the first user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                user = User.objects.first()
                if not user:
                    self.stdout.write(self.style.ERROR('No users found in the database'))
                    return
                
                self.stdout.write(self.style.SUCCESS(f'Found user: {user.email} (ID: {user.id})'))
                
                # Create a test channel if it doesn't exist
                channel, created = ChatChannel.objects.get_or_create(
                    name='Test Channel',
                    channel_type='group',
                    defaults={
                        'created_by': user.id,
                        'updated_by': user.id
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS('Created test channel'))
                else:
                    self.stdout.write(self.style.SUCCESS('Using existing test channel'))
                
                # Create a channel participant
                participant, created = ChannelParticipant.objects.get_or_create(
                    user=user,
                    channel=channel,
                    defaults={
                        'role': ChannelParticipant.Role.MEMBER,
                        'user_type': ChannelParticipant.UserType.INTERNAL
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS('Successfully created channel participant'))
                else:
                    self.stdout.write(self.style.SUCCESS('Channel participant already exists'))
                
                self.stdout.write(self.style.SUCCESS('Test completed successfully'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
