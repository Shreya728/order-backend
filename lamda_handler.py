from mangum import Mangum
from fastapi import FastAPI
from main import app  # Import your existing FastAPI app

handler = Mangum(app)
