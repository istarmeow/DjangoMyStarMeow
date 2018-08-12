@echo off
title = Shell
if %computername% == LIURUI-HOMEPC (
	echo '家里的电脑'
	python3 manage.py shell
) else (
	echo '公司的电脑'
	python manage.py shell
)

pause