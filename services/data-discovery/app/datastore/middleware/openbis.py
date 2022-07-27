"""
FastAPI middleware to ensure authentication with openBIS
"""

import string
from fastapi import Depends, FastAPI, Request

def login(user:string, password: string)

def verify_auth(req: Request) -> bool:
    """
    Middleware to verify if the request contains a valid
    openBIS token
    """