# /app/scripts/my_task.py
from datetime import datetime

with open("/var/log/cron.log", "a") as f:
    f.write(f"Cron job ran at {datetime.utcnow()} UTC\n")
