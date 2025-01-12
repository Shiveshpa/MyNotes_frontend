from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from .error import error_handler  # assuming error_handler is in the error.py file
from dotenv import load_dotenv
import os 

# Define OAuth2PasswordBearer to extract token from headers or cookies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
load_dotenv()

# Get the secret key from the environment
SECRET_KEY = os.getenv("SECRET_KEY")

def verify_token(request: Request):
    print(request)
    token = request.headers.get("Authorization")
    print(token)

    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = token[7:]  # Remove the "Bearer " prefix

    try:
        # Decode the JWT token (ensure the secret matches the one used in signing)
        user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.state.user = user  # Attach the user information to the request
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Forbidden")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Forbidden")

    return user['id']  # Return the user_id
