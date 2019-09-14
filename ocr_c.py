import os
import subprocess

init = "activate django &&"
a = "celery worker -A Academic_Aggregation -l info -P eventlet -Q low_priority -c 4"
b = "celery worker -A Academic_Aggregation -l info -P eventlet -Q high_priority -c 8"
c = "python manage.py runserver"

child1 = subprocess.Popen(init + a,shell=True)
child2 = subprocess.Popen(init + b,shell=True)
child3 = subprocess.Popen(init + c,shell=True)

