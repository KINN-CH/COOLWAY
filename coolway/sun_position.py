# coolway/sun_position.py

"""
태양의 고도(altitude)와 방위각(azimuth) 계산 모듈
"""

from datetime import datetime
from pvlib import solarposition
import pandas as pd
import pytz  # ← 추가

def get_sun_position(lat, lon, date_time=None):
    """
    위도, 경도, 날짜/시간을 받아 태양의 고도와 방위각을 계산합니다.
    :param lat: 위도
    :param lon: 경도
    :param date_time: datetime 객체 (기본값: 현재 시간)
    :return: (고도, 방위각) 튜플 (단위: 도)
    """
    if date_time is None:
        date_time = datetime.now()
    # 반드시 한국 시간대(Asia/Seoul)로 변환
    if date_time.tzinfo is None:
        date_time = pytz.timezone('Asia/Seoul').localize(date_time)
    else:
        date_time = date_time.astimezone(pytz.timezone('Asia/Seoul'))
    times = pd.DatetimeIndex([date_time])
    solpos = solarposition.get_solarposition(times, lat, lon)
    altitude = float(solpos['apparent_elevation'].iloc[0])
    azimuth = float(solpos['azimuth'].iloc[0])
    return altitude, azimuth
