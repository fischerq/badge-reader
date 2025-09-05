ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 \
    pip

# Copy source
COPY badgereader / 

# Install Python dependencies (if any are specified in requirements.txt)
# Assuming requirements.txt might be added later at the root or within the custom_component
 COPY requirements.txt /
 RUN pip install --no-cache-dir -r /requirements.txt

# Copy run.sh script
COPY run.sh /
RUN chmod a+x /run.sh

COPY server.py /
RUN chmod a+x /server.py

# Set the entrypoint
CMD [ "/run.sh" ]
