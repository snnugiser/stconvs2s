
import math

def solar_declination(doy, unit="degree"):
    """
    计算太阳赤纬
    unit: "degree" or "radius"
    """
    delta = -23.44 * math.cos(math.pi*2/365*(doy+10))
    if unit == "degree":
        pass
    else:
        delta = delta*math.pi/180
    return delta


if __name__ == "__main__":
    print(solar_declination(358))