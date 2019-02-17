#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

ARG base_image=eu.gcr.io/superbalist-datascience/spark-py:v2.4.0
FROM $base_image

############ Copy distributions ######
COPY requirements.txt /opt/spark/work-dir/
RUN python3 -m pip install --upgrade pip

RUN apk update && apk add libpq && \
	apk add --virtual .build-deps musl-dev postgresql-dev && \
	pip install -r /opt/spark/work-dir/requirements.txt && \
	apk del .build-deps

COPY dist/. ${SPARK_HOME}/work-dir/dist/
COPY src/sql/. ${SPARK_HOME}/work-dir/sql/
ENV PYTHONPATH ${SPARK_HOME}/python/lib/pyspark.zip:${SPARK_HOME}/python/lib/py4j-*.zip:${SPARK_HOME}/dist

############ GCS bindings ############

RUN rm $SPARK_HOME/jars/guava-14.0.1.jar
ADD http://central.maven.org/maven2/com/google/guava/guava/23.0/guava-23.0.jar $SPARK_HOME/jars
ADD https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-latest-hadoop2.jar $SPARK_HOME/jars

WORKDIR /opt/spark/work-dir
ENTRYPOINT [ "/opt/entrypoint.sh" ]
