FROM dockerfile/python

RUN \
  apt-get update && \
  apt-get install -y libkyotocabinet-dev protobuf-compiler

RUN virtualenv /env
RUN /env/bin/pip install beautifulsoup4 protobuf google-api-python-client

RUN \
  wget http://fallabs.com/kyotocabinet/pythonlegacypkg/kyotocabinet-python-legacy-1.18.tar.gz && \
  tar -xzvf kyotocabinet-python-legacy-1.18.tar.gz
WORKDIR kyotocabinet-python-legacy-1.18
RUN /env/bin/python setup.py build
RUN /env/bin/python setup.py install

ADD . /app

WORKDIR /app

ENV PYTHONPATH /app:/app/gen
CMD ["/env/bin/python", "/app/kaggle_down.py", "fetch-all", "-c", "/app/d/conf.pb", "--log-level=DEBUG"]
