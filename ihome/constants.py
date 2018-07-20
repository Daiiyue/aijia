# coding:utf-8

# 常量

IMAGE_CODE_REDIS_EXPIRES = 120 # 图片验证码在redis的保存时间
SMS_CODE_REDIS_EXPIRES = 300   # 短信验证码在redis的保存时间
QINIU_URL_DOMAIN = 'http://p7kohmjxl.bkt.clouddn.com/' # 七牛域名\
LOGIN_ERROR_MAX_NUM = 5
LOGIN_ERROR_FORBID_TIME = 600
AREA_INFO_REDIS_EXPIRES = 3600