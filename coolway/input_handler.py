from .utils import geocode_place

def is_lat_lon(input_str):
    try:
        parts = input_str.replace(' ', ',').split(',')
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) != 2:
            return False
        lat = float(parts[0])
        lon = float(parts[1])
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except:
        return False

def get_coords(input_str):
    if is_lat_lon(input_str):
        parts = input_str.replace(' ', ',').split(',')
        parts = [p.strip() for p in parts if p.strip()]
        lat, lon = float(parts[0]), float(parts[1])
        return lat, lon
    else:
        return geocode_place(input_str)
