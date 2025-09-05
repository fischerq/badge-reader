ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
  apk add --no-cache \
    python3 \
    py3-pip

COPY requirements.txt /
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r /requirements.txt

COPY badgereader / 
COPY run.sh /
COPY server.py /

RUN chmod a+x /run.sh
RUN chmod a+x /server.py

CMD [ "/run.sh" ]
