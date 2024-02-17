import os
from dotenv import load_dotenv

load_dotenv()


print(f"CHECK STATUS : {os.getenv('CHECK_STATUS')}; TYPE: {type(os.getenv('CHECK_STATUS'))}")
print(f"CHECK FLOAT : {os.getenv('CHECK_FLOAT')}; TYPE: {type(os.getenv('CHECK_FLOAT'))}")