from pymavlink import mavutil

def get_telemetry(master):
    data = {"altitude": None, "mode": None, "lat": None, "lon": None, "armed": None}

    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=False)
    if msg:
        data["altitude"] = msg.relative_alt / 1000.0
        data["lat"] = msg.lat / 1e7
        data["lon"] = msg.lon / 1e7

    heartbeat = master.recv_match(type='HEARTBEAT', blocking=False)
    if heartbeat:
        data["mode"] = mavutil.mode_string_v10(heartbeat)
        data["armed"] = bool(heartbeat.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)

    return data

def print_telemetry(master):
    t = get_telemetry(master)
    print(f"  [Telemetry] Alt: {t['altitude']}m | Mode: {t['mode']} | Armed: {t['armed']} | Lat: {t['lat']} | Lon: {t['lon']}")
