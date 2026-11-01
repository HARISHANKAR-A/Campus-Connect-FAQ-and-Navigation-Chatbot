from urllib.parse import urlencode


def _point(loc):
    if loc.get("lat") is not None and loc.get("lng") is not None:
        return f"{loc['lat']},{loc['lng']}"
    return f"{loc['name']}, VIT Vellore, Tamil Nadu"


def directions_url(dest, origin=None, mode="walking"):
    params = {"api": "1", "destination": _point(dest), "travelmode": mode}
    if origin:
        params["origin"] = _point(origin)
    return "https://www.google.com/maps/dir/?" + urlencode(params, safe=",")
