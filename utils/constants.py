import os
from dotenv import load_dotenv

load_dotenv()

port = int(os.getenv('SOCKET_PORT', 6789))
