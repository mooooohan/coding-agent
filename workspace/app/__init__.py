from flask import Flask
import os

app = Flask(__name__)

# Load configuration
app.config.from_object('app.config.Config')

# Import routes after app is initialized
from app import routes