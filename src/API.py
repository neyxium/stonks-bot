from dotenv import load_dotenv
import os

# Naloži spremenljivke iz .env datoteke
load_dotenv()

def getAPI_KEY():
    return os.getenv("API_KEY")

def getPass():
    return os.getenv("BOT_PASS")
