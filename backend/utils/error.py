from fastapi import HTTPException

def error_handler(status_code: int, message: str):
    raise HTTPException(status_code=status_code, detail=message)
