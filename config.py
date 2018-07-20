# coding:utf-8
import redis

class Config(object):
    SECRET_KEY = 'jdi4o9u%6BN4KJ^#55)kda12&i%hjkh26pop#'


    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask_session用到的配置信息
    SESSION_TYPE = 'redis'
    # 加密session_id
    SESSION_USER_SIGNER = True
    SECRRT_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 86400


class DevelopmentConfig(Config):
    """开发模式config"""
    DEBUG = True

class ProductionConfig(Config):
    """生产模式config"""
    pass


config_dict = {
    "develop":DevelopmentConfig,
    "product":ProductionConfig
}
