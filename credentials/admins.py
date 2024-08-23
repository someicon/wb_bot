import os
from dotenv import load_dotenv
import logging

load_dotenv()

if os.getenv("ADMINS_ID"):
    admins_list = [int(admin_id) for admin_id in os.getenv("ADMINS_ID").split(",")]
else:
    admins_list = []
    logging.error("id Администраторы не указаны")
