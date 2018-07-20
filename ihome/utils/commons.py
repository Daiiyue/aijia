# coding:utf-8
from werkzeug.routing import BaseConverter
from flask import session, jsonify, g
from ihome.utils.response_code import RET
from functools import wraps

class RegexConverter(BaseConverter):
    """自定义的接受正则表达式的转换器"""
    def __init__(self, url_map, regex):
        super(RegexConverter,self).__init__(url_map)
        self.regex = regex


def login_required(view_func):
    """检验用户的登陆状态"""
    # 为了不改变原有函数名字和说明文档
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id')
        if user_id is not None:
            g.user_id = user_id
            return view_func(*args,**kwargs)
        else:
            resp = {
                'errno':RET.SESSIONERR,
                'errmsg':'用户未登陆'
            }
            return jsonify(resp)
    return wrapper