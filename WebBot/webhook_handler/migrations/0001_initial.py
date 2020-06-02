# Generated by Django 3.0.6 on 2020-06-02 04:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import webhook_handler.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('name', models.CharField(default='Курс без имени', max_length=255)),
                ('is_changed_user', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CoursePart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Тема без названия', max_length=255)),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_closed', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_opened', models.BooleanField(default=False)),
                ('is_changed_user', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('user_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Id Пользователя')),
                ('name', models.CharField(max_length=255)),
                ('FIO', models.CharField(max_length=255)),
                ('status', models.IntegerField(default=1)),
                ('step', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TestVariants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=40)),
                ('is_true', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, default=True, null=True, upload_to=webhook_handler.models.create_user_file_path, verbose_name='Загруженный файл')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webhook_handler.TelegramUser')),
            ],
        ),
        migrations.CreateModel(
            name='UserTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_answer', models.TextField(blank=True, default=None, null=True)),
                ('mark', models.FloatField(blank=True, default=None, null=True)),
                ('changed_teacher', models.BooleanField(default=False)),
                ('changed_user', models.BooleanField(default=False)),
                ('answer_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webhook_handler.UserFile')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_handler.CoursePart')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_handler.TelegramUser')),
            ],
        ),
        migrations.CreateModel(
            name='UserPart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_handler.CoursePart')),
                ('tasks', models.ManyToManyField(blank=True, to='webhook_handler.UserTask')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_handler.TelegramUser')),
            ],
        ),
        migrations.CreateModel(
            name='UserCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_handler.Course')),
                ('course_parts', models.ManyToManyField(blank=True, to='webhook_handler.UserPart')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_handler.TelegramUser')),
            ],
        ),
        migrations.CreateModel(
            name='TestQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webhook_handler.UserFile')),
                ('variants', models.ManyToManyField(to='webhook_handler.TestVariants')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Тест без названия', max_length=255)),
                ('percent_normal', models.FloatField(default=0.6)),
                ('percent_good', models.FloatField(default=0.7)),
                ('percent_excellent', models.FloatField(default=0.85)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_handler.TelegramUser')),
                ('tasks', models.ManyToManyField(blank=True, to='webhook_handler.TestQuestion')),
            ],
        ),
        migrations.CreateModel(
            name='StudentGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Курс без имени', max_length=255)),
                ('code', models.CharField(blank=True, max_length=20, null=True)),
                ('is_changed_user', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhook_handler.Course')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_creator', to='webhook_handler.TelegramUser')),
                ('students', models.ManyToManyField(related_name='students', to='webhook_handler.TelegramUser')),
            ],
        ),
        migrations.CreateModel(
            name='CourseTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('is_changed_user', models.BooleanField(default=False)),
                ('files', models.ManyToManyField(blank=True, to='webhook_handler.UserFile')),
            ],
        ),
        migrations.AddField(
            model_name='coursepart',
            name='tasks',
            field=models.ManyToManyField(blank=True, to='webhook_handler.CourseTask'),
        ),
        migrations.AddField(
            model_name='coursepart',
            name='test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webhook_handler.Test'),
        ),
        migrations.AddField(
            model_name='coursepart',
            name='theory_files',
            field=models.ManyToManyField(blank=True, related_name='theory_files', to='webhook_handler.UserFile'),
        ),
        migrations.AddField(
            model_name='course',
            name='course_parts',
            field=models.ManyToManyField(blank=True, to='webhook_handler.CoursePart'),
        ),
        migrations.AddField(
            model_name='course',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_creator', to='webhook_handler.TelegramUser'),
        ),
    ]