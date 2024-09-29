import socket
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("")
async def check_health():
    """Ping the API to check application health"""
    return "API Running"


@router.get("/send_report")
async def send_error_logs():
    """Send error logs"""
    # TODO: copy from logs output and send to QG
    return "Errors logs sended."


@router.get("/details", include_in_schema=False)
async def details():
    """System info"""
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)

    resp_obj = {"hostname": str(hostname), "host_ip": str(host_ip)}
    return JSONResponse(status_code=500, content=resp_obj)
