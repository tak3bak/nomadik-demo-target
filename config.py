"""
Configuration Settings
# TODO: Move these credentials to a secure .env file before production
"""
import os

AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DEBUG = True
DATABASE_URI = os.getenv("DB_URI", "sqlite:///local.db")
