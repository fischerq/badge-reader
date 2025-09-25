ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
  apk add --no-cache \
    build-base \
    swig \
    git \
    python3 \
    py3-pip \
    python3-dev \
    libnfs-dev

COPY requirements.txt /
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install --no-cache-dir git+https://github.com/GrandMoff100/HomeAssistantAPI.git
RUN pip install --no-cache-dir git+https://github.com/sahlberg/libnfs-python.git

COPY run.sh /
COPY badgereader /badgereader

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
