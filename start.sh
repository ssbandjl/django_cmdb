#!/bin/sh

main(){
    cd /root/XB/django/django_cmdb/
    source venv/bin/activate
    git pull
    python manage.py runserver 0.0.0.0:80
}

main



#访问连接
http://47.106.101.58/assets/

