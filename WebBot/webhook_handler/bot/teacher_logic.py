from webhook_handler.models import *
from telebot import TeleBot, types, apihelper
from django.db.models import Q
from django.utils import timezone
from .lang import ru


class TeacherAction:

    def __init__(self, bot: TeleBot, message: types.Message, user: TelegramUser):
        self.bot = bot
        self.message = message
        self.user = user

    def welcome_teacher(self):
        message_text = ru.get('teacher_welcome_message')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('Мои курсы', callback_data='my_courses'))
        markup.add(types.InlineKeyboardButton('Мои Группы', callback_data='my_groups'))
        markup.add(types.InlineKeyboardButton('Создать новый курс', callback_data='create_course'))
        markup.add(types.InlineKeyboardButton('Загрузить файлы на сервер', callback_data='upload_files'))
        markup.add(types.InlineKeyboardButton('Настройки', callback_data='settings'))

        try:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                       reply_markup=markup, message_id=self.message.message_id)
        except apihelper.ApiException:
            self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def my_courses(self):
        message_text = ru.get('my_courses')
        markup = types.InlineKeyboardMarkup(row_width=1)
        courses = Course.objects.filter(creator=self.user).all()
        for course in courses:
            markup.add(types.InlineKeyboardButton(course.name, callback_data=f'course_{course.pk}'))
        markup.add(types.InlineKeyboardButton("Назад", callback_data=f'teachermainmenu'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def course(self, course_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        course = Course.objects.filter(creator=self.user, pk=course_id).first()
        message_text = ru.get('course').format(course.name, course.description)

        markup.add(types.InlineKeyboardButton("Редактировать курс", callback_data=f'editcourse_{course.pk}'))
        markup.add(types.InlineKeyboardButton("Назад", callback_data=f'my_courses'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def my_groups(self):
        message_text = ru.get('my_groups')
        markup = types.InlineKeyboardMarkup(row_width=1)
        groups = StudentGroup.objects.filter(creator=self.user).all()
        markup.add(types.InlineKeyboardButton("Создать новую группу", callback_data=f'create_new_group'))
        for group in groups:
            markup.add(types.InlineKeyboardButton(group.name, callback_data=f'group_{group.pk}'))
        markup.add(types.InlineKeyboardButton("Назад", callback_data=f'teachermainmenu'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def group(self, group_id=None, not_edited=False):
        markup = types.InlineKeyboardMarkup(row_width=1)

        if group_id is None:
            group = StudentGroup(creator=self.user)
            group.generate_course_code()
            group.save()
        else:
            group = StudentGroup.objects.filter(creator=self.user, pk=group_id).first()

        message_text = ru.get('group').format(group.name)

        if group.course:
            markup.add(types.InlineKeyboardButton("Переназначить курс для группы", callback_data=f'changecourseforgroup_{group.pk}'))
            markup.add(types.InlineKeyboardButton("Темы курса", callback_data=f'courseparts_{group.course.pk}'))
            markup.add(types.InlineKeyboardButton("Редактировать курс группы", callback_data=f'editcourse_{group.course.pk}'))
        else:
            markup.add(types.InlineKeyboardButton("Назначить курс для группы", callback_data=f'changecourseforgroup_{group.pk}'))

        markup.add(types.InlineKeyboardButton("Получить код группы", callback_data=f'getcoursecode_{group.pk}'))
        markup.add(types.InlineKeyboardButton("Список студентов", callback_data=f'studentlist_{group.pk}'))
        markup.add(types.InlineKeyboardButton("Написать сообщение студентам", callback_data=f'sendmessagetostudent_{group.pk}'))
        markup.add(types.InlineKeyboardButton("Назад", callback_data=f'my_courses'))

        if not_edited:
            self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)
            return
        try:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                       reply_markup=markup, message_id=self.message.message_id)
        except apihelper.ApiException:
            self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def send_message_to_students(self, group_id):
        group = StudentGroup.objects.filter(group_id).first()
        if not group:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой группы больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('send_message_to_students')
        self.user.step = 71
        self.user.save()
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def get_course_code(self, group_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        group = StudentGroup.objects.filter(creator=self.user, pk=group_id).first()

        message_text = ru.get('get_course_code').format(group.name, group.code)
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'group_{group_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def student_list(self, group_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        group = StudentGroup.objects.filter(creator=self.user, pk=group_id).first()
        message_text = ru.get('student_list').format(group.name)
        markup.add(types.InlineKeyboardButton('Отчет об успеваемости', callback_data=f'teacherreport_{group_id}'))
        for student in group.students.all():
            markup.add(types.InlineKeyboardButton(student.FIO, callback_data=f'student_{group_id}_{student.pk}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def student(self, student_id, group_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        group = StudentGroup.objects.filter(creator=self.user, pk=group_id).first()
        student = TelegramUser.objects.filter(pk=student_id).first()
        user_course = UserCourse.objects.filter(user=self.user, course=group.course).first()
        if not user_course:
            self.bot.send_message(chat_id=self.message.chat.id, text='"Этот ученик не имеет доступа к этому курсу')
            return
        parts = user_course.course_parts.all()
        all_tasks = 0
        sum_marks = 0.0
        count_parts = 0
        count_completed_part = 0
        completed_task = 0
        for part in parts:
            if part.part.is_openned:
                count_parts += 1
                is_completed = True
                tasks = part.tasks.all()
                for task in tasks:
                    all_tasks += 1
                    if task.mark:
                        sum_marks += task.mark
                        completed_task += 1
                    else:
                        is_completed = False
                if is_completed:
                    count_completed_part += 1

        message_text = ru.get('student').format(student.FIO, f'{count_completed_part}/{count_parts}',
                                                f'{completed_task}/{all_tasks}', sum_marks)
        markup.add(types.InlineKeyboardButton('Написать студенту', callback_data=f'sendmessagestudent_{student.pk}'))
        markup.add(types.InlineKeyboardButton('Удалить студента с курса', callback_data=f'blockstudent_{group_id}_{student.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'studentlist_{group.pk}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def block_student(self, group_id, student_id):
        group = StudentGroup.objects.filter(creator=self.user, pk=group_id).first()
        student = TelegramUser.objects.filter(pk=student_id).first()
        user_course = UserCourse.objects.filter(user=self.user, course=group.course).first()
        if not user_course:
            self.bot.send_message(chat_id=self.message.chat.id, text='Этот ученик не имеет доступа к этому курсу')
            return
        for part in user_course.course_parts.all():
            for task in part.tasks.all():
                task.delete()
            part.delete()
        user_course.delete()
        self.bot.send_message(chat_id=self.message.chat.id, text='Ученик удален')
        self.group(group_id)

    def change_course_group(self, group_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        group = StudentGroup.objects.filter(creator=self.user, pk=group_id).first()
        message_text = ru.get('change_course_group')
        courses = Course.objects.filter(creator=self.user).all()
        for course in courses:
            markup.add(types.InlineKeyboardButton(course.name, callback_data=f'courseforgroup_{group_id}_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'group_{group.pk}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def course_for_group(self, group_id, course_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        group = StudentGroup.objects.filter(creator=self.user, pk=group_id).first()
        message_text = ru.get('course_for_group')
        course = Course.objects.filter(pk=course_id).first()
        markup.add(types.InlineKeyboardButton("Добавить этот курс", callback_data=f'addthiscourse_{group_id}_{course_id}'))
        markup.add(types.InlineKeyboardButton("Добавить этот курс как новый", callback_data=f'addcourseasnew_{group_id}_{course_id}'))
        markup.add(types.InlineKeyboardButton("Назад", callback_data=f'changecourseforgroup_{group.pk}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def add_course_to_group(self, group_id, course_id, this=False):
        group = StudentGroup.objects.filter(creator=self.user, pk=group_id).first()
        course = Course.objects.filter(pk=course_id).first()
        message_text = ru.get('add_this_course').format(course.name, group.name)
        if this:
            group.course = course
            group.save()
            self.bot.send_message(chat_id=self.message.chat.id, text=message_text)
            return
        else:
            new_course = Course(creator=course.creator, description=course.description, name=course.name + f' ({group.name})')
            new_course.save()

            # add parts
            for part in course.course_parts.all():
                new_part = CoursePart(name=part.name, description=part.description, test=part.test, date_closed=part.date_closed,
                                      is_opened=part.is_opened)
                new_part.save()

                # add theory to part
                for file in part.theory_files.all():
                    new_part.theory_files.add(file)

                # add tasks
                for task in part.tasks:
                    new_task = CourseTask(name=task.name + f' ({group.name})', description=task.description)
                    new_task.save()

                    # add files to task
                    for file in task.files.all():
                        new_task.files.add(file)
                    new_task.save()

                new_part.save()
                new_course.course_parts.add(new_part)
            new_course.save()
            message_text = ru.get('add_course_as_new').format(course.name, group.name)
            self.bot.send_message(chat_id=self.message.chat.id, text=message_text)
        self.group(group_id)

    def create_new_course(self):
        message_text = ru.get('create_new_course')
        markup = types.InlineKeyboardMarkup(row_width=1)
        course = Course(creator=self.user)
        course.save()

        markup.add(types.InlineKeyboardButton('Изменить название', callback_data=f'changecoursename_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Изменить описание', callback_data=f'changecoursedescription_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Темы курса', callback_data=f'courseparts_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Добавить дополнительную литературу к курсу', callback_data=f'additionalliterature_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'teachermainmenu'))

        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def upload_files(self):
        message_text = ru.get('upload_files')
        #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #markup.add(types.KeyboardButton('Завершить загрузку'))
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text)
        self.user.step = 10
        self.user.save()

    def view_files(self, course_id=None, part_id=None, task_id=None):
        markup = types.InlineKeyboardMarkup(row_width=1)
        files = UserFile.objects.filter(user=self.user).all()
        for file in files:
            if course_id:
                markup.add(types.InlineKeyboardButton(file.file.name, callback_data=f'addfilecourse_{course_id}'))
            elif part_id:
                markup.add(types.InlineKeyboardButton(file.file.name, callback_data=f'addfilepart_{course_id}'))
            elif task_id:
                markup.add(types.InlineKeyboardButton(file.file.name, callback_data=f'addfiletask_{course_id}'))
        return markup

    def settings(self):
        message_text = ru.get('settings')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('Изменить ФИО', callback_data='change_my_fio'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data='teachermainmenu'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def edit_course(self, course_id):

        course = Course.objects.filter(pk=course_id).first()
        if not course:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Курс больше не существует', message_id=self.message.message_id)
            return
        desc = course.description if course.description else ''
        message_text = ru.get('edit_course').format(course.name, desc)
        markup = types.InlineKeyboardMarkup(row_width=1)

        markup.add(types.InlineKeyboardButton('Изменить название', callback_data=f'changecoursename_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Изменить описание', callback_data=f'changecoursedescription_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Темы курса', callback_data=f'courseparts_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Добавить новые файлы к курсу', callback_data=f'additionalliterature_{course.pk}'))
        markup.add(types.InlineKeyboardButton('Назад к курсам', callback_data='my_courses'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def change_course_name(self, course_id):
        course = Course.objects.filter(pk=course_id).first()
        if not course:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Курс больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('change_course_name')
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        course.is_changed_user = True
        self.user.step = 21
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def change_course_description(self, course_id):
        course = Course.objects.filter(pk=course_id).first()
        if not course:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Курс больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('change_course_description')
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.user.step = 22
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def additional_literature(self, course_id):
        course = Course.objects.filter(pk=course_id).first()
        if not course:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Курс больше не существует', message_id=self.message.message_id)
            return
        self.bot.send_message(chat_id=self.message.chat.id, text='В разработке')

    def course_parts(self, course_id):
        course = Course.objects.filter(pk=course_id).first()
        if not course:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Курс больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('course_parts')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(f'Создать новую тему', callback_data=f'createnewpart_{course.pk}'))
        for part in course.course_parts.all():
            markup.add(types.InlineKeyboardButton(f'{"🔓" if part.is_opened else "🔒"}{part.name} {"{Открыта}" if part.is_opened else ""}', callback_data=f'coursepart_{course.pk}_{part.pk}'))

        markup.add(types.InlineKeyboardButton(f'Назад к курсам', callback_data='my_courses'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def course_part(self, course_id, part_id):
        part = CoursePart.objects.filter(part_id).first()
        if not part:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой темы больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('course_part').format(f'{"🔓" if part.is_opened else "🔒"}{part.name} {"{Открыта}" if part.is_opened else ""}')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(f'{"Закрыть" if part.is_opened else "Открыть"} тему', callback_data=f'changepartstatus_{course_id}_{part.pk}'))
        if part.is_opened:
            markup.add(types.InlineKeyboardButton(f'{"Проверить домашнюю работу"} тему', callback_data=f'checkhomeworkperpart_{course_id}_{part.pk}'))
        markup.add(types.InlineKeyboardButton(f'{"Редактировать информацию"} тему', callback_data=f'editpart_{course_id}_{part.pk}'))
        markup.add(types.InlineKeyboardButton(f'Назад', callback_data=f'courseparts_{course_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def edit_part(self, part_id=None, course_id=None):
        if course_id and not part_id:
            course = Course.objects.filter(pk=course_id).first()
            if not course:
                self.bot.edit_message_text(chat_id=self.message.chat.id, text='Курс больше не существует', message_id=self.message.message_id)
                return
            part = CoursePart()
            part.save()
            course.course_parts.add(part)
        else:
            part = CoursePart.objects.filter(pk=part_id).first()

        if not part:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой темы больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('edit_part').format(part.name)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('Изменить имя', callback_data=f'changepartname_{course_id}_{part.pk}'))
        markup.add(types.InlineKeyboardButton('Выбрать теорию', callback_data=f'addtheoryforpart_{course_id}_{part.pk}'))
        markup.add(types.InlineKeyboardButton('Задания к теме', callback_data=f'tasks_{course_id}_{part.pk}'))
        markup.add(types.InlineKeyboardButton('Тест к теме', callback_data=f'add_tests_{course_id}_{part.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'coursepart_{course_id}_{part.pk}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def change_part_name(self, part_id):
        part = CoursePart.objects.filter(pk=part_id).first()
        if not part:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой темы больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('change_part_name')
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.user.step = 31
        self.user.save()
        part.is_changed_user = True
        part.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)
        
    def change_part_status(self, course_id, part_id):
        part = CoursePart.objects.filter(part_id).first()
        if not part:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой темы больше не существует', message_id=self.message.message_id)
            return
        part.is_opened = not part.is_opened
        part.save()
        self.course_part(course_id, part_id)

    def check_home_work_per_part(self, course_id, part_id):
        user_part = UserPart.objects.filter(part__pk=part_id).first()
        markup = types.InlineKeyboardMarkup(row_width=1)
        message_text = ru.get('check_home_work_per_part')
        for user_task in user_part.tasks.filter(~Q(text_answer=None)| ~Q(answer_file=None)).all():
            markup.add(types.InlineKeyboardButton(f'{user_task.name} {user_task.user.FIO}', callback_data=f'useranswer_{course_id}_{part_id}_{user_task.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'coursepart_{course_id}_{part_id}'))

        try:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                       reply_markup=markup, message_id=self.message.message_id)
        except apihelper.ApiException:
            self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def user_answer(self, course_id, part_id, user_task_id):
        user_task = UserTask.objects.filter(pk=user_task_id).first()
        markup = types.InlineKeyboardMarkup(row_width=1)
        message_text = ru.get('user_answer').format(user_task.user.FIO, f'{user_task.text_answer if user_task.text_answer else ""}')

        markup.add(types.InlineKeyboardButton('Поставить оценку', callback_data=f'putmark_{user_task_id}'))
        markup.add(types.InlineKeyboardButton('Написать отзыв', callback_data=f'writefeedback_{user_task_id}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'checkhomeworkperpart_{course_id}_{part_id}'))

        if user_task.answer_file:
            self.bot.send_document(chat_id=self.message.chat.id, caption=message_text, data=user_task.answer_file.open(mode="rb"))
        else:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                       reply_markup=markup, message_id=self.message.message_id)

    def put_mark(self, user_task_id):
        user_task = UserTask.objects.filter(pk=user_task_id).first()
        user_task.changed_teacher = True
        self.user.step = 51
        message_text = ru.get('put_mark').format(user_task.task.name, user_task.user.FIO)
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text)
        user_task.save()
        self.user.save()

    def write_feedback(self, user_task_id):
        user_task = UserTask.objects.filter(pk=user_task_id).first()
        user_task.changed_teacher = True
        self.user.step = 61
        message_text = ru.get('write_feedback').format(user_task.task.name, user_task.user.FIO)
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text)
        user_task.save()
        self.user.save()

    def add_theory_part(self, course_id, part_id):
        message_text = ru.get('add_theory_part')
        markup = self.view_files(part_id=part_id)
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'editpart_{course_id}_{part_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def tasks(self, course_id, part_id):
        part = CoursePart.objects.filter(pk=part_id).first()
        if not part:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой темы больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('tasks')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('Создать новое задание', callback_data=f'createnewtask_{part_id}'))
        tasks = CourseTask.objects.filter(creator=self.user).all()
        for task in tasks:
            markup.add(types.InlineKeyboardButton(task.name, callback_data=f'task_{course_id}_{part_id}_{task.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'editpart_{course_id}_{part_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def task(self, course_id, part_id, task_id=None):
        if not task_id:
            task = CourseTask()
            task.save()
            part = CoursePart.objects.filter(pk=part_id).first()
            if not part:
                self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой темы больше не существует', message_id=self.message.message_id)
                return
            part.tasks.add(task)
        else:
            task = CourseTask.objects.filter(pk=task_id).first()

        if not task:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такого задания больше не существует', message_id=self.message.message_id)
            return

        message_text = ru.get('task').format(task.name, task.description)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('Изменить имя', callback_data=f'changetaskname_{task.pk}'))
        markup.add(types.InlineKeyboardButton('Изменить описание', callback_data=f'changetaskdescription_{task.pk}'))
        markup.add(types.InlineKeyboardButton('Добавить файлы с заданием', callback_data=f'addtaskfiles_{course_id}_{part_id}_{task.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'tasks_{course_id}_{part_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def change_task_name(self, task_id):
        task = CourseTask.objects.filter(pk=task_id).first()
        if not task:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такого задания больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('change_task_name')
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.user.step = 41
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def change_task_description(self, task_id):
        task = CourseTask.objects.filter(pk=task_id).first()
        if not task:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такого задания больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('change_task_description')
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Отмена'))
        self.user.step = 42
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text, reply_markup=markup)

    def add_files_task(self, course_id, part_id, task_id):
        message_text = ru.get('add_files_task')
        markup = self.view_files(task_id=task_id)
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'task_{course_id}_{part_id}_{task_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)

    def add_tests(self, part_id):
        part = CoursePart.objects.filter(pk=part_id).first()
        if not part:
            self.bot.edit_message_text(chat_id=self.message.chat.id, text='Такой темы больше не существует', message_id=self.message.message_id)
            return
        message_text = ru.get('tests')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('Создать новый тест', callback_data=f'create_new_test'))
        tests = Test.objects.filter(creator=self.user).all()
        for test in tests:
            markup.add(types.InlineKeyboardButton(test.name, callback_data=f'addtest_{part_id}_{test.pk}'))
        markup.add(types.InlineKeyboardButton('Назад', callback_data=f'editpart_{part_id}'))
        self.bot.edit_message_text(chat_id=self.message.chat.id, text=message_text,
                                   reply_markup=markup, message_id=self.message.message_id)
