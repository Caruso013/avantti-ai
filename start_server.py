from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

port = os.getenv("APP_PORT", "8000")
subprocess.run(["gunicorn", "app:app", "--bind", f"0.0.0.0:{port}"])
