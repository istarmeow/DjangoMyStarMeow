@echo off
title = Runserver
echo %username%
echo %computername%

if %computername% == LIURUI-HOMEPC (
	python3 manage.py runserver 0.0.0.0:8899 --insecure
) else (
	python manage.py runserver 0.0.0.0:8899 --insecure
)

pause