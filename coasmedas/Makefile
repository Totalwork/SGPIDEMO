run:
	cd ../env38/bin && source activate && cd ../../SININCARIBEMAR && python3.8 manage.py runserver 0.0.0.0:8000;

run-prod:
	cd ../env/bin && source activate && cd ../../SININCARIBEMAR && nohup python3.8 manage.py runserver 0.0.0.0:8000 > nohup.log 2>&1 &;

static:
	cd ../env38/bin && source activate && cd ../../SININCARIBEMAR && python3.8 manage.py collectstatic;

static-prod:
	cd ../env/bin && source activate && cd ../../SININCARIBEMAR && python3.8 manage.py collectstatic;

shell:
	cd ../env38/bin && source activate && cd ../../SININCARIBEMAR && python3.8 manage.py shell;