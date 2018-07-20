# coding:utf-8

import re
from ihome import redis_store, db
from ihome.models import User
from . import api
from flask import request,jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome.utils.commons import login_required
from ihome import constants

@api.route("/users",methods=['post'])
def register():
    """用户注册"""
    # 接受参数,手机号\短信验证码\密码\json格式的数据
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')

    if not all([mobile,sms_code,password]):
        resp = {
            'errno': RET.PARAMERR,
            'errmsg': '参数不完整'
        }
        return jsonify(resp)


    if not re.match(r'1[34578]\d{9}', mobile):
        resp = {
            'errno': RET.DATAERR,
            'errmsg': '手机号格式错误'
        }
        return jsonify(resp)


    # 业务逻辑
    # 获取真实的短信验证码
    try:
        real_sms_code = redis_store.get('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': '查询短信验证码错误'
        }
        return jsonify(resp)

    if real_sms_code is None:
        resp = {
            'errno':RET.NODATA,
            'errmsg':'短信验证码过期'
        }
        return jsonify(resp)

    if real_sms_code != sms_code:
        resp = {
            'errno':RET.DATAERR,
            'errmsg':'短信验证码错误'
        }
        return jsonify(resp)

    # 删除验证码
    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)


    user = User(name=mobile,mobile=mobile)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        resp = {
            'errno' : RET.DATAEXIST,
            'errmsg': '用户手机号已经被注册'
        }
        return jsonify(resp)

    # 利用session记录用户的登陆状态
    session['user_id'] = user.id
    session['user_name'] = mobile
    session['mobile'] = mobile

    resp = {
        'errno': RET.OK,
        'errmsg':'注册成功'
    }
    return jsonify(resp)
    # 判断短信验证码是否过期
    # 判断用户输入的验证码是否正确
    # 判读手机号是否已经注册
    # 保存用户数据到数据库中
    # 记录用户的登陆状态
    # 返回值

@api.route("/sessions",methods=["post"])
def login():
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    # 校验参数
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')

    if not re.match(r"1[34578]\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式不正确')

    user_ip = request.remote_addr
    try:
        access_counts = redis_store.get("access_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_counts is not None and int(access_counts) >= constants.LOGIN_ERROR_MAX_NUM:
            return jsonify(errno=RET.REQERR,errmsg='登陆过于频繁')


    # 查询数据库,判断用户信息与密码
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg='查询用户信息异常')

    if user is None or not user.check_password(password):
        try:
            redis_store.incr("access_%s" % user_ip)
            redis_store.expire('access_%s' %user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.LOGINERR, errmsg='用户名或密码错误')

    # 登陆成功保存用户的登陆状态
    # 删除错误记录
    try:
        redis_store.delete("access_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)

    session['user_id'] = user.id
    session['user_name'] = user.name
    session['mobile'] = user.mobile
    return jsonify(errno=RET.OK, errmsg="用户登录成功")

@api.route('/session',methods=['GET'])
def check_login():
    name = session.get('user_name')
    if name is not None:
        return jsonify(errno=RET.OK, errmsg='true', data={'name':name})
    else:
        return jsonify(errno=RET.SESSIONERR,errmsg='false')

@api.route('/session',methods=['DELETE'])
def logout():
    session.pop('user_id')
    session.pop('user_name')
    session.pop('mobile')
    return jsonify(errno=RET.OK,errmsg='OK')

# @login_required
# def set_user_acatar():
#     pass