# Generated by Django 5.2.3 on 2025-07-23 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_broadcast', '0008_alter_broadcast_is_video_note_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broadcast',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Текст сообщения, для ссылки используйте запись: \n[нажми сюда](https://example.com)\nВсе виды записей: https://core.telegram.org/bots/api#formatting-options:~:text=MarkdownV2%20style,the%20expandability%20mark%7C%7C'),
        ),
    ]
