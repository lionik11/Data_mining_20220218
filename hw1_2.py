# Mapbox Raster Tiles API (https://docs.mapbox.com/api/maps/raster-tiles/)
# Генерирует растровые тайлы спутникового изображения

import requests
import math


# перевод абсолютных координат в систему координат тайлов сервиса Mapbox
# (https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python)
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


my_headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/96.0.4664.174 Safari/537.36'}
# ключ доступа
access_token = "pk.eyJ1IjoibGlvbmlrIiwiYSI6ImNrendrOGlicDF2cWsybnBrbzMwZGJhZjAifQ._27IBHycf-XPGbTElfkJQw"

# переменные api
endpoint = "mapbox.places"
zoom = 14
coordinates = [55.707189, 37.471011]
xy = deg2num(coordinates[0], coordinates[1], zoom)
x = xy[0]
y = xy[1]
tileset_id = "mapbox.satellite"
my_format = ".png"

# созданнынй url для запроса тайла через api
my_url = f"https://api.mapbox.com/v4/{tileset_id}/{zoom}/{x}/{y}@2x{my_format}?access_token={access_token}"
print(my_url)

# запрос
my_request = requests.get(my_url, my_headers)
print(my_request)

# сохранение файла изображения
with open("my_tile.png", "wb") as outfile:
    outfile.write(my_request.content)
