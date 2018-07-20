# coding:utf-8

import redis
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config_dict
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from utils.commons import RegexConverter

# 什么时候有app什么时候初始化
db = SQLAlchemy()
redis_store = None
# 仅提供了验证功能
csrf = CSRFProtect()


logging.basicConfig(level=logging.DEBUG)
file_log_handler = RotatingFileHandler("logs/log",maxBytes=1024*1024*100,backupCount=10)
formatter = logging.Formatter('%(levelname)s %(filename)s %(message)s')
file_log_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_log_handler)

# 工厂模式
# 用哪个类的配置文件就导入哪个类的
def create_app(config_name):
    app = Flask(__name__)

    conf = config_dict[config_name]
    # 设置flask的配置信息
    app.config.from_object(conf)

    # 初始化数据库db
    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=conf.REDIS_HOST, port=conf.REDIS_PORT)

    csrf.init_app(app)

    # 改变flask的默认session机制到redis中
    Session(app)

    app.url_map.converters['re'] = RegexConverter
    # 延时导入
    import api_1_0
    app.register_blueprint(api_1_0.api ,url_prefix='/api/v1_0')

    import web_html
    app.register_blueprint(web_html.html)

    return app