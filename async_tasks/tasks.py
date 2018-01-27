# -*- coding: utf-8 -*-

from corelib.mail import send_mail
from async_tasks.mq import task_mq

@task_mq.task
def send_mail_task(mail, title, content):
    return send_mail(mail, title, content)
