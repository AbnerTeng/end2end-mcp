import os

from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
CA_CERT_PATH = os.getenv("CA_CERT_PATH")
CA_PASSWORD = os.getenv("CA_PASSWORD")
