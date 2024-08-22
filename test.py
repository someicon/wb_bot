import os
from dotenv import load_dotenv
load_dotenv()

admins = [int(admin_id) for admin_id in os.getenv("ADMINS_ID").split(",")]
id = 3906371231231

print(id in admins)
