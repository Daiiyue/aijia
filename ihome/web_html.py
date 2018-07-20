# coding:utf-8

from flask import Blueprint, current_app, make_response
from flask_wtf.csrf import generate_csrf

from ihome.utils.commons import login_required

html = Blueprint('html',__name__)

@html.route("/<re(r'.*'):file_name>")
def get_html_file(file_name):
    """提供html文件"""
    if not file_name:
        file_name = 'index.html'
    if file_name != 'favicon.ico':
        file_name = 'html/'+ file_name

    # 使用wtf的generate_csrf()生成csrf_token字符串
    csrf_token = generate_csrf()

    # 为客户设置cookie
    resp = make_response(current_app.send_static_file(file_name))
    resp.set_cookie('csrf_token',csrf_token)
    return resp
