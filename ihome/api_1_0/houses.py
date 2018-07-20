# coding:utf-8


from ihome import redis_store, db
from ihome.utils.commons import login_required
from . import api
from ihome.models import Area, House, Facility, HouseImage
from flask import current_app,jsonify, request, g
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
import json
from ihome import constants


@api.route("/areas")
def get_area_info():

    # 先尝试从redis中读取缓存数据
    try:
        areas_json = redis_store.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
        areas_json = None

    # 查询数据库,获取城区信息
    if areas_json is None:
        try:
            areas_list = Area.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='查询城区信息异常')

        areas = []
        for area in areas_list:
            areas.append(area.to_dict())

        areas_json = json.dumps(areas)
        try:
            redis_store.setex("area_info",constants.AREA_INFO_REDIS_EXPIRES,areas_json)
        except Exception as e:
            current_app.logger.error(e)
    else:
        current_app.logger.info('hit redis cache area info')

    return '{"errno": 0, "errmsg": "查询城区信息成功", "data":{"areas": %s}}' % areas_json, 200, \
           {"Content-Type": "application/json"}


@api.route("/houses/info",methods=['post'])
@login_required
def save_house_info():
    house_data = request.get_json()
    if house_data is  None:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    if not all([title,price,area_id,address,room_count,acreage,unit,capacity,beds,deposit,min_days,max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    try:
        price = int(float(price)*100)
        deposit = int(float(deposit)*100)

    except Exception as e:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    user_id = g.user_id
    house = House(
        user_id = user_id,
        area_id = area_id,
        title = title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 处理房屋的设施信息
    facility_id_list = house_data.get('facility')
    if facility_id_list:
        # 表示用户勾选了房屋设施
        # 过滤用户传送的不合理的设施id
        try:
            facility_list = Facility.query.filter(Facility.id.in_(facility_id_list)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库异常')
        # !!!为房屋添加设施信息
        if facility_list:
            house.facilities=facility_list

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')

    return jsonify(errno=RET.OK,errmsg='保存成功',data={"house_id":house.id})


@api.route("/houses/image",methods=['post'])
@login_required
def save_house_image():
    # 直接以form方式获取
    house_id=request.form.get("house_id")
    # 得到的是文件对象
    image_file = request.files.get("house_image")

    if not all([house_id,image_file]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA,errmsg='数据库异常')

    if house is None:
        return jsonify(errno=RET.NODATA,errmsg='房屋不存在')

    # 上传文件  需要二进制文件
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='保存房屋图片失败')

    house_image = HouseImage(
        house_id=house_id,
        url=file_name,
    )
    db.session.add(house_image)
    # 处理房屋基本信息中的主图片
    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存房屋图片信息失败')
    image_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK,errmsg='保存图片成功',data={"image_url":image_url})



# /api/v1_0/houses?sd=xxxx-xx-xx&ed=xxxx-xx-xx&aid-xx&sk=new&p=1
@api.route("/houses",methods=['GET'])
def get_house_list():
    """获取房屋列表信息"""
    pass
