ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 \
    py3-pip

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
# Create a virtual environment
RUN python3 -m venv /opt/venv
# This "activates" the venv for all subsequent RUN, CMD, ENTRYPOINT instructions
ENV PATH="/opt/venv/bin:$PATH"

COPY badgereader / 

# Copy run.sh script
COPY run.sh /
RUN chmod a+x /run.sh

COPY server.py /
RUN chmod a+x /server.py

# Set the entrypoint
CMD [ "/run.sh" ]
