from typing import Union

from fastapi import HTTPException

def post_error(detail: Union[str, Exception] = ""):
    if isinstance(detail, Exception):
        return {"error_message": f"Произошла непредвиденная ошибка: {detail}"}
    return {"error_message": detail}

def get_error(detail: Union[str, Exception], status_code = 404):
    if isinstance(detail, Exception):
        return HTTPException(status_code=status_code, detail= f"Произошла непредвиденная ошибка: {detail}")
    return HTTPException(status_code=status_code, detail=detail)
