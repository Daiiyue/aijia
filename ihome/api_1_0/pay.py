# coding:utf-8
from ihome.models import Order
from ihome.utils.commons import login_required
from flask import g
from . import api


@api.route("/orders/<int:order_id>/payment",methods=['post'])
@login_required
def generate_order_payment(order_id):
    """生成支付宝的支付信息"""
    user_id = g.user_id
    # try:
    #   order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status="WAIT_PAYMENT").first()
    pass