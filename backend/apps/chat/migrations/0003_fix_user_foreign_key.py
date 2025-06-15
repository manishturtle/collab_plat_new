from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_fix_foreign_keys'),
        ('shared', '0001_initial'),  # Make sure this points to your shared app's initial migration
    ]

    operations = [
        migrations.AlterField(
            model_name='channelparticipant',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='channel_participations',
                to='shared.TenantUserModel',
            ),
        ),
    ]
