#!/usr/bin/env bash
FROM selenium/standalone-firefox:latest

# Install dependencies
RUN python3 -m pip install --no-cache-dir selenium selenium-wire requests dnspython 'blinker<1.8' 'setuptools<81' packaging

USER root
RUN mkdir -p /data && chown 1200:1200 /data
USER seluser

# Copy scripts
COPY scrapper.py /home/seluser/app/
COPY db.py /home/seluser/app/
COPY scrapper_entrypoint.sh /opt/bin/

# Run scrapper
CMD ["bash", "/opt/bin/scrapper_entrypoint.sh"]
