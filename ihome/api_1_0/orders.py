# coding:utf-8
import datetime

from ihome.models import House
from . import api
from flask import request, jsonify, current_app,g
from ihome.utils.response_code import RET
from ihome.utils.commons import login_required

@api.route("/orders",methods=['post'])
@login_required
def save_order():
    user_id = g.user_id

    order_data = request.get_json()
    if not order_data:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    house_id = order_data.get("house_id")
    start_date_str = order_data.get("start_date")
    end_date_str = order_data.get("end_date")

    if not all((house_id,start_date_str,end_date_str)):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    try:
        start_date = datetime.datetime.strftime(start_date_str,"%Y-%m-%d")
        end_date = datetime.datetime.strftime(end_date_str,"%Y-%m-%d")
        assert start_date <= end_date
        days = (end_date-start_date).days + 1

    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.PARAMERR,errmsg="日期格式错误")

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取房屋信息失败')
    if not house:
        return jsonify(errno=RET.NODATA,errmsg='房屋不存在')

    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR,errmsg='不能预定自己的房屋')
