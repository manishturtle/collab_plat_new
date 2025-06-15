from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_final_fix_foreign_keys'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatchannel',
            name='created_by',
            field=models.IntegerField(blank=True, db_column='created_by', null=True),
        ),
        migrations.AddField(
            model_name='chatchannel',
            name='updated_by',
            field=models.IntegerField(blank=True, db_column='updated_by', null=True),
        ),
    ]
