@echo on
title = Run Celery

celery -A DjangoMyStarMeow worker --pool=solo -l info

pause