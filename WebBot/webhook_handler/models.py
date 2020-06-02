from django.db import models
from random import randint
from django.utils.timezone import now


class TelegramUser(models.Model):
    """
    status:
        0 - admin
        1 - student
        2 - teacher
    """
    user_id = models.IntegerField(u'Id Пользователя', primary_key=True)
    name = models.CharField(max_length=255)
    FIO = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    step = models.IntegerField(default=0)


def create_user_file_path(instance, filename):
    return f'user_files/{instance.user.user_id}/{filename}'


class UserFile(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField('Загруженный файл', upload_to=create_user_file_path, null=True, blank=True, default=None)


class TestVariants(models.Model):
    text = models.CharField(max_length=40)
    is_true = models.BooleanField(default=False)


class TestQuestion(models.Model):
    question = models.TextField()
    file = models.ForeignKey(UserFile, on_delete=models.SET_NULL, null=True, blank=True)
    variants = models.ManyToManyField(TestVariants, blank=False)


class Test(models.Model):
    creator = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='Тест без названия')
    percent_normal = models.FloatField(default=0.60)
    percent_good = models.FloatField(default=0.70)
    percent_excellent = models.FloatField(default=0.85)
    tasks = models.ManyToManyField(TestQuestion, blank=True)


class CourseTask(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default=None, null=True, blank=True)
    files = models.ManyToManyField(UserFile, blank=True)
    is_changed_user = models.BooleanField(default=False)


class CoursePart(models.Model):
    name = models.CharField(max_length=255, default='Тема без названия')
    description = models.TextField(default=None, null=True, blank=True)
    theory_files = models.ManyToManyField(UserFile, blank=True, related_name='theory_files')
    tasks = models.ManyToManyField(CourseTask, blank=True)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(default=now)
    date_closed = models.DateTimeField(default=None, null=True, blank=True)
    is_opened = models.BooleanField(default=False)
    is_changed_user = models.BooleanField(default=False)


class Course(models.Model):
    creator = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='course_creator')
    description = models.TextField(default=None, null=True, blank=True)
    name = models.CharField(max_length=255, default='Курс без имени')
    course_parts = models.ManyToManyField(CoursePart, blank=True)
    is_changed_user = models.BooleanField(default=False)


class StudentGroup(models.Model):
    creator = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='student_creator')
    name = models.CharField(max_length=255, default='Группа без имени')
    students = models.ManyToManyField(TelegramUser, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=None, null=True, blank=True)
    code = models.CharField(max_length=20, null=True, blank=True)
    is_changed_user = models.BooleanField(default=False)

    def generate_course_code(self):
        self.code = str([chr(randint(65, 90)) for i in range(6)])


class UserTask(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    task = models.ForeignKey(CoursePart, on_delete=models.CASCADE)
    answer_file = models.ForeignKey(UserFile, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(default=None, null=True, blank=True)
    mark = models.FloatField(default=None, null=True, blank=True)
    changed_teacher = models.BooleanField(default=False)
    changed_user = models.BooleanField(default=False)


class UserPart(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    part = models.ForeignKey(CoursePart, on_delete=models.CASCADE)
    tasks = models.ManyToManyField(UserTask, blank=True)


class UserCourse(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_parts = models.ManyToManyField(UserPart, blank=True)





