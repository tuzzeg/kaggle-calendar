FROM phusion/baseimage:0.9.15

VOLUME ["/logs"]

ENV HOME /root

# Install
#   Python
#   KyotoCabinet
RUN apt-get update && apt-get install -y \
  python \
  python-dev \
  python-pip \
  python-virtualenv \
  libkyotocabinet-dev
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN virtualenv /env
RUN /env/bin/pip install \
  beautifulsoup4 \
  protobuf \
  google-api-python-client \
  pycrypto

# Install Python bindings to KyotoCabinet
ENV KYOTOCABINET_VER 1.18
ENV KYOTOCABINET_TGZ kyotocabinet-python-legacy-${KYOTOCABINET_VER}
ENV TMP_KYOTOCABINET /tmp-kyotocabinet

RUN \
  mkdir -p ${TMP_KYOTOCABINET} && \
  curl -SL http://fallabs.com/kyotocabinet/pythonlegacypkg/${KYOTOCABINET_TGZ}.tar.gz | tar xz --strip-components=1 -C ${TMP_KYOTOCABINET} && \
  cd ${TMP_KYOTOCABINET} && \
  /env/bin/python setup.py build && \
  /env/bin/python setup.py install && \
  rm -rf ${TMP_KYOTOCABINET}

ADD . /app
ADD docker/crontab /config/crontab
ADD docker/r.sh /app/r.sh
ADD docker/logger.json /app/logger.json

RUN crontab /config/crontab
RUN \
  chmod 700 /app/r.sh

ENV PYTHONPATH /app:/app/gen

CMD ["/sbin/my_init"]
