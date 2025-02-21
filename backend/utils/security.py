from datetime import datetime, timedelta
def hash_password(password: str) -> str:
    return password 

def verify_password(password: str, hashed: str) -> bool:
    return password == hashed  

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
  
    token_data = {
        **data,
        "exp": (datetime.utcnow() + expires_delta).isoformat()
    }
    return str(token_data)  

def decode_access_token(token: str):
    try:
        token_data = eval(token)  
        return token_data.get("sub")
    except:
        return None