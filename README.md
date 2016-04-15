安装virtualenv:

	sudo pip install virtualenv

创建虚拟环境:

	virtualenv wechat_env

# 激活虚拟环境
	
    source wechat_env/bin/activate

# 安装依赖包
	
    pip install -r requirements.txt

# 直接运行
	
    python manage.py runserver

# 生产环境下supervisor + gunicorn + ngix

参考
[http://beiyuu.com/vps-config-python-vitrualenv-flask-gunicorn-supervisor-nginx/](http://beiyuu.com/vps-config-python-vitrualenv-flask-gunicorn-supervisor-nginx/)

+ 配置appId， appsecret， Token
+ 按微信官方教程配置服务器地址
+ 配置Debug
+ 配置logger
+ 配置STATICFILES_DIRS， TEMPLATES
+ 此处没有涉及数据保存，生产环境下要配置好MySql,Redis等
