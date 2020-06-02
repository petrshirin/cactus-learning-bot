from webhook_handler.models import *
from telebot import TeleBot, types, apihelper
from django.db.models import Q
from django.utils import timezone
from .lang import ru


class StudentAction:

    def __init__(self, bot: TeleBot, message: types.Message, user: TelegramUser):
        self.bot = bot
        self.message = message
        self.user = user

    def welcome_student(self):
        message_text = ru.get('student_welcome_message')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('Мои группы', callback_data='my_groups'))
        markup.add(types.InlineKeyboardButton('Найти новую группу', callback_data='find_group'))
        markup.add(types.InlineKeyboardButton('Мои долги', callback_data='my_debts'))
        markup.add(types.InlineKeyboardButton('Настройки', callback_data='settings'))
        try:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                       reply_markup=markup, message_id=self.message.message_id)
        except apihelper.ApiException:
            self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def _delete_user_course(self, course_id):
        user_course = UserCourse.objects.filter(course__pk=course_id, user=self.user).first()
        if not user_course:
            return
        for part in user_course.course_parts.all():
            for task in part.tasks.all():
                task.delete()
            part.delete()
        user_course.delete()

    def _generate_user_course(self, course_id):
        self._delete_user_course(course_id)
        course = Course.objects.filter(pk=course_id).first()
        if not course:
            return
        user_course = UserCourse(course=course, user=self.user)
        user_course.save()
        for part in course.course_parts.all():
            user_part = UserPart(part=part, user=self.user)
            user_part.save()
            user_course.course_parts.add(user_part)
            if part.is_opened:
                for task in part.tasks.all():
                    user_task = UserTask(task=task, user=self.user)
                    user_task.save()
                    user_part.tasks.add(user_task)
            user_part.save()
        user_course.save()

    def my_groups(self):
        message_text = ru.get('student_my_groups')
        markup = types.InlineKeyboardMarkup(row_width=1)
        student_groups = StudentGroup.objects.filter(students__in=[self.user]).all()
        for student_group in student_groups:
            markup.add(types.InlineKeyboardButton(student_group.name, callback_data=f'group_{student_group.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'student_main_menu'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def find_group(self):
        message_text = ru.get('student_find_group')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.user.step = 21
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def add_student_to_group(self, code):
        student_group = StudentGroup.objects.filter(code=code).first()

        if not student_group:
            self.bot.send_message(chat_id=self.message.chat.id, text='Такого кода нет')
            self.welcome_student()
            return

        not_student = False
        for student in student_group.students.all():
            if student == self.user:
                not_student = True
                break
        if not_student:
            self.bot.send_message(chat_id=self.message.chat.id, text='Вы уже находитесь в этой группе')
            self.welcome_student()
            return
        self._generate_user_course(student_group.course)
        student_group.students.add(self.user)
        student_group.save()
        self.bot.send_message(chat_id=self.message.chat.id, text='Вы успешно добавлены в группу')
        self.group(student_group.pk)

    def my_debts(self):
        message_text = ru.get('student_my_debts')
        markup = types.InlineKeyboardMarkup(row_width=1)
        user_tasks = UserTask(user=self.user, mark=None).all()
        for user_task in user_tasks:
            markup.add(types.InlineKeyboardButton(user_task.task.name, callback_data=f'task_{user_task.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'student_main_menu'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def course_tasks(self, group_id):
        message_text = ru.get('student_course_tasks')
        markup = types.InlineKeyboardMarkup(row_width=1)
        user_tasks = UserTask(user=self.user).all()
        for user_task in user_tasks:
            markup.add(types.InlineKeyboardButton(f'{user_task.task.name} {"Завершено" if user_task.mark else ""}', callback_data=f'task_{user_task.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'group_{group_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def task(self, task_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        user_task = UserTask(pk=task_id).first()
        message_text = ru.get('student_task').format(user_task.task.name, user_task.task.decription)
        markup.add(types.InlineKeyboardButton('Теория курса', callback_data=f'tasktheory_{task_id}'))
        markup.add(types.InlineKeyboardButton('Пройти тест', callback_data=f'start_test_{task_id}'))
        if user_task.files:
            markup.add(types.InlineKeyboardButton('Файлы задания', callback_data=f'taskfiles_{task_id}'))

        if not user_task.mark:
            markup.add(types.InlineKeyboardButton('Приложить тектовый ответ', callback_data=f'textanswer_{task_id}'))
            markup.add(types.InlineKeyboardButton('Приложить Файл', callback_data=f'fileanswer_{task_id}'))
        markup.add(types.InlineKeyboardButton('На главную', callback_data=f'student_main_menu'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def task_files(self, task_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        message_text = ru.get('student_task_files')
        user_task = UserTask(pk=task_id).first()
        for file in user_task.task.files.all():
            markup.add(types.InlineKeyboardButton(file.filename, callback_data=f'downloadfile_{file.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'task_{task_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def task_theory(self, task_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        message_text = ru.get('student_task_theory')
        user_task = UserTask(pk=task_id).first()
        part = UserPart.objects.filter(tasks__in=[user_task]).first()
        for file in part.theory_files.all():
            markup.add(types.InlineKeyboardButton(file.filename, callback_data=f'downloadfile_{file.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'task_{task_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def text_answer(self, task_id):
        message_text = ru.get('student_text_answer')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.user.step = 31
        user_task = UserTask(pk=task_id).first()
        user_task.changed_user = True
        user_task.save()
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def file_answer(self, task_id):
        message_text = ru.get('student_file_answer')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.user.step = 32
        user_task = UserTask(pk=task_id).first()
        user_task.changed_user = True
        user_task.save()
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def download_file(self, file_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        file = UserFile(pk=file_id).first()
        self.bot.send_document(chat_id=self.message.chat.id, data=file.open(mode='rb'))

    def settings(self):
        message_text = ru.get('student_settings')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('Изменить ФИО', callback_data=f'change_my_fio'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'student_main_menu'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def change_my_fio(self):
        message_text = ru.get('change_my_fio')
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.user.step = 41
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def group(self, group_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        group = StudentGroup.objects.filter(pk=group_id).first()
        if not group:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой группы больше не существует', message_id=self.message.message_id)
            return

        user_course = UserCourse.objects.filter(course=group.course, user=self.user).first()
        if not user_course:
            self._generate_user_course(group.course)

        points = 0.0
        count_not_done_tasks = 0
        for user_part in user_course.course_parts.filter(part__is_opened=True).all():
            for user_task in user_part:
                if user_task.mark is not None:
                    points += user_task.mark
                else:
                    count_not_done_tasks += 1

        message_text = ru.get('student_group').format(group.name, points, count_not_done_tasks)

        markup.add(types.InlineKeyboardButton('Теория курса', callback_data=f'coursetheory_{group_id}'))
        markup.add(types.InlineKeyboardButton('Задания', callback_data=f'coursetasks_{group_id}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'my_groups'))

        try:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                       reply_markup=markup, message_id=self.message.message_id)
        except apihelper.ApiException:
            self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def course_theory(self, group_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        group = StudentGroup.objects.filter(pk=group_id).first()
        if not group:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой группы больше не существует', message_id=self.message.message_id)
            return

        for file in group.course.files.all():
            markup.add(types.InlineKeyboardButton(file.filename, callback_data=f'downloadfile_{file.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'task_{task_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)





