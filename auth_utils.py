# auth_utils.py

import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header, Depends

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Dependency to verify Firebase JWT token
async def get_current_user(authorization: str = Header(...)):
    try:
        id_token = authorization.split(" ")[1]
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token  # dict with user info: uid, email, name, etc
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")
