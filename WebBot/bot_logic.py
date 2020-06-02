from telebot import TeleBot, types

import os
import django
from django.db import Error

os.environ["DJANGO_SETTINGS_MODULE"] = 'WebBot.settings'
django.setup()

from webhook_handler.bot.common_logic import CommonAction
from webhook_handler.bot.teacher_logic import TeacherAction
from webhook_handler.bot.student_logic import StudentAction
from webhook_handler.models import *
from django.core.files import File
import logging


bot = TeleBot('686614144:AAEKIVMLl18RiNDGUlKHpFLZf9KoXTnRD98')
#bot.remove_webhook()


LOG = logging.getLogger(__name__)


@bot.message_handler(commands=['start'])
def welcome_message(message):
    user = TelegramUser.objects.filter(user_id=message.chat.id).first()
    if not user:
        user = TelegramUser(user_id=message.chat.id, name=message.from_user.first_name)
        user.save()
    action = CommonAction(bot, message, user)
    action.welcome_action()


@bot.message_handler(commands=['student'])
def switch_student(message):
    user = TelegramUser.objects.filter(user_id=message.chat.id).first()
    if not user:
        user = TelegramUser(user_id=message.chat.id, name=message.from_user.first_name)
        user.save()
    action = CommonAction(bot, message, user)
    action.switch_to_student()


@bot.message_handler(commands=['teacher'])
def switch_teacher(message):
    user = TelegramUser.objects.filter(user_id=message.chat.id).first()
    if not user:
        user = TelegramUser(user_id=message.chat.id, name=message.from_user.first_name)
        user.save()
    action = CommonAction(bot, message, user)
    action.switch_to_teacher()
    action = TeacherAction(bot, message, user)
    action.welcome_teacher()


@bot.message_handler(content_types=['document'])
def document_logic(message):
    user = TelegramUser.objects.filter(user_id=message.chat.id).first()
    if not user:
        user = TelegramUser(user_id=message.chat.id, name=message.from_user.first_name)
        user.save()
    try:
        if user.status == 2:
            if user.step != 10:
                bot.send_message(message.chat.id, text='Сейчас вы не можете загружать файлы< мы их проигнорировали')
                return
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_to_save = open('file', 'wb')
            file_to_save.write(downloaded_file)
            file_to_save.close()
            file_to_read = open('file', 'rb')
            file = File(file_to_read)
            user_file = UserFile(user=user)
            user_file.file.save(message.document.file_name, file, save=True)
            bot.send_message(message.chat.id, text=f'{message.document.file_name} Загружен')
        elif user.status == 1:
            if user.step != 31:
                bot.send_message(message.chat.id, text='Сейчас вы не можете загружать файлы< мы их проигнорировали')
                return
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_to_save = open('file', 'wb')
            file_to_save.write(downloaded_file)
            file_to_save.close()
            file_to_read = open('file', 'rb')
            file = File(file_to_read)
            user.step = 0
            user.save()
            user_file = UserFile(user=user)
            user_file.save()
            user_file.file.save(message.document.file_name, file, save=True)
            bot.send_message(message.chat.id, text=f'{message.document.file_name} Загружен')

    except Exception as err:
        LOG.error(err)
        bot.send_message(message.chat.id, text='При загрузке файла произошла ошибка')


@bot.message_handler(content_types=['text'])
def text_logic(message):
    user = TelegramUser.objects.filter(user_id=message.chat.id).first()
    if not user:
        user = TelegramUser(user_id=message.chat.id, name=message.from_user.first_name)
        user.save()
    user_text = message.text.strip().lower()
    if user.status == 1:
        action = StudentAction(bot, message, user)
        if user_text == 'отмена':
            if user.step == 21:
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_student()
            if user.step == 31:
                user_task = UserTask.objects.filter(changed_user=True).first()
                if not user_task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали курс', reply_markup=types.ReplyKeyboardRemove())
                    return
                user_task.changed_user = False
                user_task.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_student()
            if user.step == 32:
                user_task = UserTask.objects.filter(changed_user=True).first()
                if not user_task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали курс', reply_markup=types.ReplyKeyboardRemove())
                    return
                user_task.changed_user = False
                user_task.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_student()
            if user.step == 41:
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_student()
        else:
            if user.step == 21:
                user.step = 0
                user.save()
                action.add_student_to_group(message.text)
            if user.step == 31:
                user_task = UserTask.objects.filter(changed_user=True).first()
                if not user_task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали курс', reply_markup=types.ReplyKeyboardRemove())
                    return

                user_task.text_answer = message.text
                user_task.changed_user = False
                user_task.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_student()
            if user.step == 41:
                user.step = 0
                user.FIO = message.text
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_student()

    elif user.status == 2:
        action = TeacherAction(bot, message, user)
        if user_text == 'отмена':
            if user.step == 21:
                course = Course.objects.filter(is_changed_user=True).first()
                if not course:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали курс', reply_markup=types.ReplyKeyboardRemove())
                    return
                course.is_changed_user = False
                course.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()
            elif user.step == 22:
                course = Course.objects.filter(is_changed_user=True).first()
                if not course:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали курс', reply_markup=types.ReplyKeyboardRemove())
                    return
                course.is_changed_user = False
                course.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.edit_course(course.pk)
            elif user.step == 31:
                part = CoursePart.objects.filter(is_changed_user=True).first()
                if not part:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали тему курса', reply_markup=types.ReplyKeyboardRemove())
                    return
                part.is_changed_user = False
                part.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            elif user.step == 41:
                task = CourseTask.objects.filter(is_changed_user=True).first()
                if not task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали задание курса', reply_markup=types.ReplyKeyboardRemove())
                    return
                task.is_changed_user = False
                task.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            elif user.step == 42:
                task = CourseTask.objects.filter(is_changed_user=True).first()
                if not task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали задание курса', reply_markup=types.ReplyKeyboardRemove())
                    return
                task.is_changed_user = False
                task.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            elif user.step == 51:
                task = UserTask.objects.filter(changed_teacher=True).first()
                if not task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали задание для проверки', reply_markup=types.ReplyKeyboardRemove())
                    return
                task.is_changed_user = False
                task.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()
            elif user.step == 61:
                task = UserTask.objects.filter(changed_teacher=True).first()
                if not task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали задание для проверки', reply_markup=types.ReplyKeyboardRemove())
                    return
                task.is_changed_user = False
                task.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            elif user.step == 71:
                group = StudentGroup.objects.filter(is_changed_user=True).first()
                if not group:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали группу для сообщения', reply_markup=types.ReplyKeyboardRemove())
                    return
                group.is_changed_user = False
                group.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            elif user.step == 71:
                group = StudentGroup.objects.filter(is_changed_user=True).first()
                if not group:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали группу', reply_markup=types.ReplyKeyboardRemove())
                    return
                group.is_changed_user = False
                group.save()
                user.step = 0
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Действие отмнено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            else:
                action.welcome_teacher()

        else:
            if user.step == 21:
                course = Course.objects.filter(is_changed_user=True).first()
                if not course:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали курс', reply_markup=types.ReplyKeyboardRemove())
                    return
                course.is_changed_user = False
                user.step = 0
                user.save()
                course.name = message.text
                course.save()
                bot.send_message(chat_id=message.chat.id, text='Имя изменено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()
            elif user.step == 22:
                course = Course.objects.filter(is_changed_user=True).first()
                if not course:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали курс', reply_markup=types.ReplyKeyboardRemove())
                    return
                course.is_changed_user = False
                user.step = 0
                user.save()
                course.description = message.text
                course.save()
                bot.send_message(chat_id=message.chat.id, text='Описание изменено', reply_markup=types.ReplyKeyboardRemove())
                action.edit_course(course.pk)
            elif user.step == 31:
                part = CoursePart.objects.filter(is_changed_user=True).first()
                if not part:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали тему курса', reply_markup=types.ReplyKeyboardRemove())
                    return
                part.is_changed_user = False
                user.step = 0
                user.save()
                part.name = message.text
                part.save()
                bot.send_message(chat_id=message.chat.id, text='Имя изменено', reply_markup=types.ReplyKeyboardRemove())
                action.edit_part()

            elif user.step == 41:
                task = CourseTask.objects.filter(is_changed_user=True).first()
                if not task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали задание курса', reply_markup=types.ReplyKeyboardRemove())
                    return
                task.is_changed_user = False
                user.step = 0
                user.save()
                task.name = message.text
                task.save()
                bot.send_message(chat_id=message.chat.id, text='Имя изменено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            elif user.step == 42:
                task = CourseTask.objects.filter(is_changed_user=True).first()
                if not task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали задание курса', reply_markup=types.ReplyKeyboardRemove())
                    return
                task.is_changed_user = False
                user.step = 0
                task.description = message.text
                task.save()
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Описание изменено', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            elif user.step == 51:
                task = UserTask.objects.filter(changed_teacher=True).first()
                if not task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали задание для проверки', reply_markup=types.ReplyKeyboardRemove())
                    return
                task.is_changed_user = False
                user.step = 0
                try:
                    mark = float(message.text)
                except ValueError:
                    bot.send_message(chat_id=message.chat.id, text='Неккорректное число', reply_markup=types.ReplyKeyboardRemove())
                    return

                task.mark = mark
                task.save()
                user.save()
                bot.send_message(chat_id=message.chat.id, text='Оценка поставлена', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()
            elif user.step == 61:
                task = UserTask.objects.filter(changed_teacher=True).first()
                if not task:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали задание для проверки', reply_markup=types.ReplyKeyboardRemove())
                    return
                task.is_changed_user = False
                user.step = 0

                task.save()
                user.save()
                report_bone = f'Отзыв прподавателя на задание: {task.task.name}\n\n{message.text}'
                bot.send_message(chat_id=task.user.user_id, text=report_bone, reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(chat_id=message.chat.id, text='Отзыв отправлен', reply_markup=types.ReplyKeyboardRemove())
                action.welcome_teacher()

            elif user.step == 71:
                group = StudentGroup.objects.filter(is_changed_user=True).first()
                if not group:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали группу для сообщения', reply_markup=types.ReplyKeyboardRemove())
                    return
                group.is_changed_user = False
                user.step = 0
                bot.send_message(chat_id=message.chat.id, text='Сообщение отправлено', reply_markup=types.ReplyKeyboardRemove())
                for student in group.students.all():
                    message_to_send = f'''{user.FIO}(Преподаватель) отправил группе сообщение:

{message.text}'''
                    bot.send_message(chat_id=message.chat.id, text=message_to_send, reply_markup=types.ReplyKeyboardRemove())
                group.save()
                user.save()
                action.welcome_teacher()

            elif user.step == 81:
                group = StudentGroup.objects.filter(is_changed_user=True).first()
                if not group:
                    bot.send_message(chat_id=message.chat.id, text='Вы не выбрали группу', reply_markup=types.ReplyKeyboardRemove())
                    return
                group.is_changed_user = False
                user.step = 0
                group.name = message.text
                group.save()
                user.save()
                action.group(group.pk, not_edited=True)

            else:
                action.welcome_teacher()

    elif user.status == 1:
        action = TeacherAction(bot, message, user)
        pass


@bot.callback_query_handler(func=lambda c: True)
def inline_logic(c):
    print(c.data)
    user = TelegramUser.objects.get(user_id=c.message.chat.id)

    if user.status == 1:
        action = StudentAction(bot, c.message, user)

        if 'student_main_menu' == c.data:
            action.welcome_student()

        elif 'my_groups' == c.data:
            action.my_groups()

        elif 'find_group' == c.data:
            action.find_group()

        elif 'my_debts' == c.data:
            action.my_debts()

        elif 'settings' == c.data:
            action.settings()

        elif 'change_my_fio' == c.data:
            action.change_my_fio()

        elif 'group_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.group(group_id)

        elif 'coursetheory_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            bot.send_message(chat_id=c.message.chat.id, text='В разработке')
            # action.course_theorygroup_id()

        elif 'coursetasks_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.course_tasks(task_id)

        elif 'tasktheory_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.task_theory(task_id)

        elif 'taskfiles_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.task_files(task_id)

        elif 'fileanswer_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.file_answer(task_id)

        elif 'textanswer_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.text_answer(task_id)

        elif 'task_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.task(task_id)

        elif 'downloadfile_' in c.data:
            try:
                param = c.data.split('_')
                file_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.download_file(file_id)



    elif user.status == 2:
        action = TeacherAction(bot, c.message, user)

        if 'teachermainmenu' in c.data:
            action.welcome_teacher()

        elif 'my_courses' == c.data:
            action.my_courses()

        elif 'my_groups' == c.data:
            action.my_groups()

        elif 'create_course' == c.data:
            action.create_new_course()

        elif 'upload_files' == c.data:
            action.upload_files()

        elif 'settings' == c.data:
            action.settings()

        elif 'change_my_fio' == c.data:
            action.change_my_fio()

        elif 'changegroupname_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.change_group_name(group_id)

        elif 'addfilecourse_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                file_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            bot.send_message(chat_id=c.message.chat.id, text='В разработке')

        elif 'addfilepart_' in c.data:
            try:
                param = c.data.split('_')
                part_id = int(param[1])
                file_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.add_file_to_part(part_id, file_id)

        elif 'addfiletask_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
                file_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.add_file_to_task(task_id, file_id)

        elif 'addtaskfiles_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
                task_id = int(param[3])
            except Exception as err:
                LOG.error(err)
                return
            action.add_files_task(course_id, part_id, task_id)

        elif 'editcourse_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.edit_course(course_id)

        elif 'addthiscourse_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
                course_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.add_course_to_group(group_id, course_id, this=True)

        elif 'addcourseasnew_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
                course_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.add_course_to_group(group_id, course_id, this=False)

        elif 'changecoursename_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.change_course_name(course_id)

        elif 'changecoursedescription_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.change_course_description(course_id)

        elif 'additionalliterature_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.additional_literature(course_id)

        elif 'course_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.course(course_id)

        elif 'create_new_group' == c.data:
            action.group()

        elif 'teacherreport_' == c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.teacher_group_report(group_id)

        elif 'changecourseforgroup_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.change_course_group(group_id)

        elif 'courseparts_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.course_parts(course_id)

        elif 'getcoursecode_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.get_course_code(group_id)

        elif 'studentlist_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.student_list(group_id)

        elif 'sendmessagetostudent_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.send_message_to_students(group_id)

        elif 'courseforgroup_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
                course_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.course_for_group(group_id, course_id)

        elif 'changegroupname_' in c.data:
            pass

        elif 'group_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.group(group_id)



        elif 'sendmessagestudent_' in c.data:
            pass

        elif 'blockstudent_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
                student_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.block_student(group_id, student_id)

        elif 'student_' in c.data:
            try:
                param = c.data.split('_')
                group_id = int(param[1])
                student_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.student(group_id, student_id)

        elif 'createnewpart_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.edit_part(course_id=course_id)

        elif 'courseparts_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.course_parts(course_id)

        elif 'editpart_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.edit_part(part_id, course_id)

        elif 'changepartname_' in c.data:
            try:
                param = c.data.split('_')
                part_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.change_part_name(part_id)

        elif 'addtheoryforpart_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.add_theory_part(course_id, part_id)

        elif 'tasks_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.tasks(course_id, part_id)

        elif 'createnewtask_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.task(course_id, part_id)

        elif 'task_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
                task_id = int(param[3])
            except Exception as err:
                LOG.error(err)
                return
            action.task(course_id, part_id, task_id)

        elif 'changetaskname_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.change_task_name(task_id)

        elif 'changetaskdescription_' in c.data:
            try:
                param = c.data.split('_')
                task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.change_task_description(task_id)

        elif 'changepartstatus_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.change_part_status(course_id, part_id)

        elif 'checkhomeworkperpart_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.check_home_work_per_part(course_id, part_id)

        elif 'useranswer_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
                user_task_id = int(param[3])
            except Exception as err:
                LOG.error(err)
                return
            action.user_answer(course_id, part_id, user_task_id)

        elif 'putmark_' in c. data:
            try:
                param = c.data.split('_')
                user_task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.put_mark(user_task_id)

        elif 'writefeedback_' in c.data:
            try:
                param = c.data.split('_')
                user_task_id = int(param[1])
            except Exception as err:
                LOG.error(err)
                return
            action.write_feedback(user_task_id)

        elif 'add_tests_' in c.data:
            bot.send_message(chat_id=c.message.chat.id, text='В разработке')

        elif 'coursepart_' in c.data:
            try:
                param = c.data.split('_')
                course_id = int(param[1])
                part_id = int(param[2])
            except Exception as err:
                LOG.error(err)
                return
            action.course_part(course_id, part_id)


bot.polling()

















