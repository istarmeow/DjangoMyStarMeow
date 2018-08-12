@echo off
title = Runserver
echo %username%
echo %computername%

if %computername% == LIURUI-HOMEPC (
	python3 manage.py runserver --insecure
) else (
	python manage.py runserver --insecure
)

pause