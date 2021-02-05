import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('HOST', 'localhost')
port = int(os.getenv('PORT', 6789))

db_name = os.getenv('DB_NAME', 'my_file.db')
