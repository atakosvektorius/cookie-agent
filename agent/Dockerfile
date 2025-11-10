#!/bin/bash
FROM selenium/standalone-chrome:142.0-chromedriver-142.0

# Install dependencies
RUN python3 -m pip install --no-cache-dir selenium requests dnspython

# Copy scripts
COPY scrapper.py /app/
COPY scrapper_entrypoint.sh /opt/bin/

# Run scrapper
CMD ["bash", "/opt/bin/scrapper_entrypoint.sh"]
