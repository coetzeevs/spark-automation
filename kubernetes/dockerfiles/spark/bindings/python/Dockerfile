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

############ Base Spark ############

FROM eu.gcr.io/superbalist-datascience/spark:v2.4.0

############ Python bindings ############

WORKDIR /
RUN mkdir ${SPARK_HOME}/python

# Run apk additions required to be able to install Python and other packages

RUN apk add --update curl make automake && \
    apk add --update --virtual scipy-runtime python3 py3-pip && \
    apk add --virtual freetype libgfortran libgcc libpng  libstdc++ musl openblas tcl tk && \
    apk add --virtual scipy-build && \
    apk add build-base python3-dev openblas-dev freetype-dev pkgconfig gfortran && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    pip install --no-cache-dir numpy && \
    pip install --no-cache-dir matplotlib && \
    pip install --no-cache-dir scipy && \
    pip install --no-cache-dir pandas && \
    apk del scipy-build && \
    rm -rf /var/cache/apk/* && \
    rm -r /root/.cache

ENV PYSPARK_PYTHON /usr/bin/python
COPY python/lib ${SPARK_HOME}/python/lib
WORKDIR /opt/spark/work-dir
ENTRYPOINT [ "/opt/entrypoint.sh" ]
