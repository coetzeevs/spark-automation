help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "build - package"

all: default

default: clean dev_deps deps test lint build

.venv:
	if [ ! -e ".venv/bin/activate_this.py" ] ; then virtualenv --clear .venv ; fi

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr dist/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

deps: .venv
	. .venv/bin/activate && pip install -U -r requirements.txt -t ./src/libs

dev_deps: .venv
	. .venv/bin/activate && pip install -U -r dev_requirements.txt

lint:
	. .venv/bin/activate && pylint -r n src/main.py src/shared src/jobs tests

test:
	. .venv/bin/activate && nosetests ./tests/* --config=.noserc

pips:
	pip install -r requirements.txt -t ./src/libs

build: clean
	mkdir ./dist
	cp ./src/main.py ./dist
	cd ./src && zip -x main.py -x \*libs\* -r ../dist/jobs.zip . && cd ..
	cd ./src/libs && zip -r ../../dist/libs.zip . && cd ../..

sample:
	cd ./dist && ~/Devel/spark/spark.24/spark-2.4.0-bin-hadoop2.7/bin/spark-submit --py-files jobs.zip,libs.zip main.py --job wordcount && cd ..

prep:
	rm -fr ~/Devel/spark/spark.24/spark-2.4.0-bin-hadoop2.7/dist/
	mkdir ~/Devel/spark/spark.24/spark-2.4.0-bin-hadoop2.7/dist
	cp ./dist/* ~/Devel/spark/spark.24/spark-2.4.0-bin-hadoop2.7/dist/
	cd ~/Devel/spark/spark.24/spark-2.4.0-bin-hadoop2.7/ && docker build -t eu.gcr.io/superbalist-datascience/spark-py:v2.4.0 -f kubernetes/dockerfiles/spark/Dockerfile .
	cd ~/Devel/spark/spark.24/spark-2.4.0-bin-hadoop2.7/ && docker push eu.gcr.io/superbalist-datascience/spark-py:v2.4.0

submit:
	cd ./dist
	../bin/spark-submit --properties-file properties --deploy-mode cluster --master k8s://https://$KUBERNETES_MASTER_IP:443 --py-files local:///opt/spark/dist/jobs.zip,local:///opt/spark/dist/libs.zip local:///opt/spark/dist/main.py --job wordcount

echo:
	echo "It's working"