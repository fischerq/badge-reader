ARG BUILD_FROM
FROM $BUILD_FROM

# Set the working directory
WORKDIR /usr/src/app

# Copy the custom component files
COPY ../custom_components/badgereader ./custom_components/badgereader

# Install Python dependencies (if any are specified in requirements.txt)
# Assuming requirements.txt might be added later at the root or within the custom_component
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copy run.sh script
COPY run.sh /
RUN chmod a+x /run.sh

# Set the entrypoint
CMD [ "/run.sh" ]
