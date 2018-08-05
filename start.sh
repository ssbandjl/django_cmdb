#!/bin/sh

main(){
    cd /root/XB/django/django_cmdb/
    source venv/bin/activate
    git pull
    python manage.py runserver 0.0.0.0:80
}

main
