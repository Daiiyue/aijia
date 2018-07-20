# coding:utf-8

from . import api
from ihome.utils.commons import login_required
from flask import g,request,jsonify,current_app, session
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import User
from ihome import constants,db

@api.route("/users/avatar", methods=['POST'])
@login_required
def set_user_avatar():
    """设置用户头像"""
    # 获取参数
    user_id = g.user_id
    image_file = request.files.get('avatar')
    # 校验参数
    if image_file is None:
        return jsonify(errno=RET.PARAMERR,errmsg='未上传文件')
    # 保存头像数据
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
        # print (file_name)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='上传文件失败')

    # 将文件名信息保存到数据库中
    try:
        User.query.filter_by(id=user_id).update({'avatar_url': file_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存图像信息失败')
    # 返回值
    avatar_url= constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK,errmsg='保存头像成功',data={'avatar_url':avatar_url})

@api.route('/user/name',methods=['PUT'])
@login_required
def change_user_name():
    """修改用户名"""
    user_id = g.user_id
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    name = req_data.get('name') # 用户要设置的名字
    if not name:
        return jsonify(errno=RET.PARAMERR,errmsg='名字不能为空')

    # 保存用户昵称name,并同时判读name是否重复
    try:
        User.query.filter_by(id=user_id).update({"name":name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='设置用户错误')

    # 修改
    session['name'] = name
    return jsonify(errno=RET.OK,errmsg='OK',data={'name':name})

@api.route("/user",methods=['GET'])
@login_required
def get_user_profile():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取用户信息失败')
    if user is None:
        return jsonify(errno=RET.NODATA,errmsg='无效操作')
    return jsonify(errno=RET.OK,errmsg='OK',data=user.to_dict())

@api.route("/user/auth",methods=['GET'])
@login_required
def get_user_auth():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.loggger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取用户实名信息失败')
    if user is None:
        return jsonify(errno=RET.NODATA,errmsg='无效操作')

    return jsonify(errno=RET.OK,errmsg='OK',data=user.auth_to_dict())

@api.route("/user/auth",methods=['POST'])
@login_required
def set_user_auth():
    user_id = g.user_id
    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    real_name = req_data.get('real_name')
    id_card = req_data.get('id_card')

    if not all([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    try:
        User.query.filter_by(id=user_id,real_name=None,id_card=None).update({'real_name':real_name,'id_card':id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errnno=RET.DBERR, errmsg='保存用户实名信息失败')
    return jsonify(errno=RET.OK,errmsg='OK')

