from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from django.db import transaction
from apps.chat.models import ChatChannel, ChannelParticipant

class Command(BaseCommand):
    help = 'Test creating a channel participant in bingo_travels schema'

    def handle(self, *args, **options):
        with schema_context('bingo_travels'):
            # Get the custom user model
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                # Find available users
                users = User.objects.all()
                self.stdout.write(self.style.SUCCESS(f'Found {users.count()} users:'))
                for user in users:
                    self.stdout.write(f"User ID: {user.id}, Email: {user.email}")
                
                if not users:
                    self.stdout.write(self.style.ERROR('No users found in the database'))
                    return
                
                # Try to get user with ID 2 (from the API request that failed)
                try:
                    user_id = 2
                    user = User.objects.get(id=user_id)
                    self.stdout.write(self.style.SUCCESS(f'Found requested user ID {user_id}: {user.email}'))
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'User with ID {user_id} does not exist'))
                    user = users.first()
                    self.stdout.write(self.style.SUCCESS(f'Using first available user instead: ID {user.id}, {user.email}'))
                
                # Create a test channel
                with transaction.atomic():
                    channel = ChatChannel.objects.create(
                        name="Test Direct Channel",
                        channel_type="direct",
                        created_by=user.id,
                        updated_by=user.id
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created channel: {channel.id}'))
                    
                    # Create a channel participant
                    participant = ChannelParticipant.objects.create(
                        channel=channel,
                        user=user,
                        created_by=user.id,
                        updated_by=user.id
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created participant: {participant.id}'))
                    
                    # Verify the participant
                    queried_participant = ChannelParticipant.objects.get(id=participant.id)
                    self.stdout.write(self.style.SUCCESS(f'Verified participant: Channel ID {queried_participant.channel.id}, User ID {queried_participant.user.id}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {e}'))
