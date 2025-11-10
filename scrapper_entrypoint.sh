#!/bin/bash


# Start Selenium services as a background job
echo "[*] SCRAPPER DOCKER STARTING ORIGINAL ENTRYPOINT..."
/opt/bin/entry_point.sh &


# Wait for Selenium WebDriver to become available
echo "[*] SCRAPPER DOCKER WAITING FOR SELENIUM SERVICES TO START..."
until curl -s http://localhost:4444/status | grep -q '"ready"[[:space:]]*:[[:space:]]*true'; do
  sleep 2
  echo "[*] SCRAPPER DOCKER WAITING FOR SELENIUM SERVICES..."
done



# Now run your script
echo "[*] SCRAPPER DOCKER STARTING PYTHON SCRAPPER..."
python3 /app/scrapper.py


# Optional: wait for background jobs or handle shutdown
wait