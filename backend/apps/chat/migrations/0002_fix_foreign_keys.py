from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0001_initial'),
    ]
    
    # This migration will fix the foreign key references to use the correct user model
    operations = [
        migrations.AlterField(
            model_name='channelparticipant',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='channel_participations',
                to=settings.AUTH_USER_MODEL,
                db_constraint=True,
            ),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='chat_messages',
                to=settings.AUTH_USER_MODEL,
                db_constraint=True,
            ),
        ),
        migrations.AlterField(
            model_name='device',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notification_devices',
                to=settings.AUTH_USER_MODEL,
                db_constraint=True,
            ),
        ),
        migrations.AlterField(
            model_name='messagereadstatus',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='message_reads',
                to=settings.AUTH_USER_MODEL,
                db_constraint=True,
            ),
        ),
        migrations.AlterField(
            model_name='userchannelstate',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='chat_channel_states',
                to=settings.AUTH_USER_MODEL,
                db_constraint=True,
            ),
        ),
    ]
