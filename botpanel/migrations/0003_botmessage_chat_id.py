# Generated by Django 5.2.3 on 2025-06-29 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botpanel', '0002_alter_botmessage_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='botmessage',
            name='chat_id',
            field=models.BigIntegerField(default=0, help_text='ID канала, где опубликовано сообщение'),
            preserve_default=False,
        ),
    ]
