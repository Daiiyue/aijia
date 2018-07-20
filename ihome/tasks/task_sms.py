# coding:utf-8

from celery import Celery
from ihome.libs.yuntongxun.sms import CCP

app = Celery("ihome",broker="redis://127.0.0.1:6379/5")

@app.task
def send_template_sms(to,dates,temp_id):
    """发送短信"""
    ccp = CCP()
    ccp.send_template_sms(to,dates,temp_id)
