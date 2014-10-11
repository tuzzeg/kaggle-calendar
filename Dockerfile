FROM dockerfile/python

ENV KYOTOCABINET_VER 1.18
ENV KYOTOCABINET_TGZ kyotocabinet-python-legacy-${KYOTOCABINET_VER}

RUN apt-get update && apt-get install -y \
  libkyotocabinet-dev

RUN virtualenv /env
RUN /env/bin/pip install \
  beautifulsoup4 \
  protobuf \
  google-api-python-client

ENV TMP_KYOTOCABINET /tmp-kyotocabinet

RUN \
  mkdir -p ${TMP_KYOTOCABINET} && \
  curl -SL http://fallabs.com/kyotocabinet/pythonlegacypkg/${KYOTOCABINET_TGZ}.tar.gz | tar xz --strip-components=1 -C ${TMP_KYOTOCABINET} && \
  cd ${TMP_KYOTOCABINET} && \
  /env/bin/python setup.py build && \
  /env/bin/python setup.py install && \
  rm -rf ${TMP_KYOTOCABINET}

ADD . /app

WORKDIR /app

ENV PYTHONPATH /app:/app/gen
CMD ["/env/bin/python", "/app/kaggle_down.py", "fetch-all", "-c", "/app/d/conf.pb", "--log-level=DEBUG"]
