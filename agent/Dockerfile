#!/bin/bash
FROM selenium/standalone-firefox:latest

# Install dependencies
RUN python3 -m pip install --no-cache-dir selenium requests dnspython

# Copy scripts
COPY scrapper.py /home/seluser/app/
COPY scrapper_entrypoint.sh /opt/bin/

# Run scrapper
CMD ["bash", "/opt/bin/scrapper_entrypoint.sh"]
