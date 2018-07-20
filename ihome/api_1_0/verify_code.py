# coding:utf-8
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET
from ihome.libs.yuntongxun.sms import CCP
import random
from ihome.models import User
from ihome.tasks.sms import tasks


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """提供图片验证码"""
    # 业务处理
    # 生成验证码图片
    name,text,image_data = captcha.generate_captcha()

    # 返回值
    # redis_store.set("image_code_%s" % image_code_id, text)
    # redis_store.expires("image_code_%s" % image_code_id, )

    # 在redis中存储验证码的编号和其对应的值
    # setex key seconds value 设置key的值为value并将其生存时间设置为seconds
    try:
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 在日记中记录异常
        current_app.logger.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg': 'save image code failed'
        }
        return jsonify(resp)

    # 返回验证码图片
    resp = make_response(image_data)
    resp.headers["Content-Type"] = 'image/jpg'
    return resp


@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def send_sms_code(mobile):
    image_code_id = request.args.get('image_code_id')
    image_code = request.args.get('image_code')
    if not all([image_code_id,image_code]):
        resp = {
            'errno':RET.PARAMERR,
            'errmsg':'参数不完整'
        }
        return jsonify(resp)

    # 业务处理
    # 取出真实的图片验证码
    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            'errno': RET.DBERR,
            'errmsg':'获取图片验证码失败'
        }
        return jsonify(resp)

    if real_image_code is None:
        resp = {
            'errno':RET.NODATA,
            'errmsg':"图片验证码过期"
        }
        return jsonify(resp)

    # 删除redis中的图片验证码,防止用户多次尝试同一个验证码
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    if real_image_code.lower() != image_code.lower():
        resp = {
            'errno':RET.DATAERR,
            'errmsg':'图片验证码有误'
        }
        return jsonify(resp)

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            resp = {
                'errno':RET.DATAEXIST,
                'errmsg':'用户手机号已被注册'
            }
            return jsonify(resp)

    sms_code = '%06d' % random.randint(0,999999)

    try:
        redis_store.setex('sms_code_%s'% mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        resp = {
            'errno':RET.DBERR,
            'errmsg':'保存短信验证码异常'
        }
        return jsonify(resp)


    # 使用celery发布任务
    # task_sms.send_template_sms.delay(mobile,[sms_code,str(constants.SMS_CODE_REDIS_EXPIRES/60)],1)
    # 返回异步结果对象,通过这个对象获取最终的结果
    result = tasks.send_template_sms.delay(mobile,[sms_code,str(constants.SMS_CODE_REDIS_EXPIRES/60)],1)
    print(result.id)
    # get方法帮助我们从backend中拿取执行结果,默认是阻塞的,可设置超时时间
    ret = result.get()
    print(ret)
    return jsonify(errno= RET.OK,errmsg='OK')


    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms(mobile,[sms_code,str(constants.SMS_CODE_REDIS_EXPIRES/60)],1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     resp = {
    #         'errno':RET.THIRDERR,
    #         'errmsg':'发送短信异常'
    #     }
    #     return jsonify(resp)
    #
    # if result == 0:
    #     resp = {
    #         'errno':RET.OK,
    #         'errmsg':'发送短信成功'
    #     }
    #
    #     return jsonify(resp)
    # else:
    #     resp = {
    #         'errno':RET.THIRDERR,
    #         'errmsg':'发送短信失败'
    #     }
    #
    #     return jsonify(resp)
    #
