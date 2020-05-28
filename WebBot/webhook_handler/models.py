from django.db import models
from random import randint
from django.utils.timezone import now


class TelegramUser(models.Model):
    user_id = models.IntegerField(u'Id Пользователя', primary_key=True)
    name = models.CharField(max_length=255)


def create_user_file_path(instance, filename):
    return f'user_files/{instance.user.user_id}/{filename}'


class UserFile(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL)
    file = models.FileField('Загруженный файл', upload_to=create_user_file_path)


class TestVariants(models.Model):
    text = models.CharField(max_length=40)
    is_true = models.BooleanField(default=False)


class TestQuestion(models.Model):
    question = models.TextField()
    file = models.ForeignKey(UserFile, on_delete=models.SET_NULL)
    variants = models.ManyToManyField(TestVariants, blank=False)


class Test(models.Model):
    creator = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    percent_normal = models.FloatField(default=0.60)
    percent_good = models.FloatField(default=0.70)
    percent_excellent = models.FloatField(default=0.85)
    tasks = models.ManyToManyField(TestQuestion, blank=True)


class CourseTask(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default=None, null=True, blank=True)
    files = models.ManyToManyField(UserFile, blank=True)


class CoursePart(models.Model):
    name = models.CharField(max_length=255, default='Тема без названия')
    description = models.TextField(default=None, null=True, blank=True)
    theory_files = models.ManyToManyField(UserFile, blank=True, related_name='theory_files')
    tasks = models.ManyToManyField(CourseTask, blank=True)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(default=now)
    date_closed = models.DateTimeField(default=None, null=True, blank=True)
    is_opened = models.BooleanField(default=False)


class Course(models.Model):
    creator = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='creator')
    name = models.CharField(max_length=255, default='Курс без имени')
    students = models.ManyToManyField(TelegramUser, related_name='students')
    code = models.CharField()
    course_parts = models.ManyToManyField(CoursePart, blank=True)

    def generate_course_code(self):
        self.code = str([chr(randint(65, 90)) for i in range(6)])



