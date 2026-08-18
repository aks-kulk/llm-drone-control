VALID_ACTIONS = {
    "arm", "disarm", "takeoff", "land", "rtl", "set_mode",
    "move_north", "move_south", "move_east", "move_west"
}

VALID_MODES = {"GUIDED", "STABILIZE", "AUTO", "LOITER", "RTL", "LAND"}

def validate_command(command: dict) -> tuple[bool, str]:
    action = command.get("action")
    params = command.get("parameters", {})

    if action not in VALID_ACTIONS:
        return False, f"Invalid or unrecognized action: {action}"

    if action == "takeoff":
        alt = params.get("altitude")
        if not isinstance(alt, (int, float)) or not (1 <= alt <= 100):
            return False, "Altitude must be a number between 1 and 100 meters"

    if action in ("move_north", "move_south", "move_east", "move_west"):
        dist = params.get("distance")
        if not isinstance(dist, (int, float)) or not (1 <= dist <= 500):
            return False, "Distance must be a number between 1 and 500 meters"

    if action == "set_mode":
        mode = params.get("mode")
        if mode not in VALID_MODES:
            return False, f"Invalid flight mode: {mode}"

    return True, "OK"
