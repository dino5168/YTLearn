from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import geoip2.database
import geoip2.errors

# dino5168$AB


class IPGeoMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, geoip_db_path: str):
        super().__init__(app)
        self.reader = geoip2.database.Reader(geoip_db_path)

    async def dispatch(self, request: Request, call_next):
        x_forwarded_for = request.headers.get("x-forwarded-for")
        ip = (
            x_forwarded_for.split(",")[0].strip()
            if x_forwarded_for
            else request.client.host
        )

        geo_info = None
        try:
            response = self.reader.country(ip)
            geo_info = {
                "country_code": response.country.iso_code,
                "country_name": response.country.name,
            }
        except geoip2.errors.AddressNotFoundError:
            # IP 不在數據庫中
            pass
        except Exception as e:
            # 處理其他錯誤
            print(f"GeoIP lookup error: {e}")

        # 封鎖邏輯
        if geo_info and geo_info.get("country_code") in {"RU", "CN"}:
            return Response("Access Denied", status_code=403)

        request.state.client_ip = ip
        request.state.geo_info = geo_info

        response = await call_next(request)
        return response
