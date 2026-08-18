from pymavlink import mavutil
import time
import math

class DroneController:
    def __init__(self, connection_string="tcp:127.0.0.1:5760"):
        print(f"Connecting to {connection_string}...")
        self.master = mavutil.mavlink_connection(connection_string)
        self.master.wait_heartbeat()
        print(f"Connected. System {self.master.target_system}, Component {self.master.target_component}")

    def arm(self):
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 0, 0, 0, 0, 0, 0
        )
        return self._wait_ack("Arming")

    def disarm(self):
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 0, 0, 0, 0, 0, 0, 0
        )
        return self._wait_ack("Disarming")

    def set_mode(self, mode_name):
        mode_id = self.master.mode_mapping().get(mode_name)
        if mode_id is None:
            return False, f"Unknown mode: {mode_name}"
        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )
        time.sleep(1)
        return True, f"Mode set to {mode_name}"

    def takeoff(self, altitude):
        self.set_mode("GUIDED")
        time.sleep(1)
        self.arm()
        time.sleep(1)
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, altitude
        )
        return self._wait_ack(f"Takeoff to {altitude}m")

    def land(self):
        self.master.mav.command_long_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0, 0, 0, 0, 0, 0, 0, 0
        )
        return self._wait_ack("Landing")

    def rtl(self):
        return self.set_mode("RTL")

    def move_relative(self, direction, distance):
        """Move relative to current position using local NED coordinates."""
        offsets = {
            "move_north": (distance, 0, 0),
            "move_south": (-distance, 0, 0),
            "move_east": (0, distance, 0),
            "move_west": (0, -distance, 0),
        }
        dx, dy, dz = offsets[direction]

        self.master.mav.set_position_target_local_ned_send(
            0,
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED,
            0b0000111111111000,
            dx, dy, dz,
            0, 0, 0,
            0, 0, 0,
            0, 0
        )
        return True, f"Moving {direction.replace('move_', '')} {distance}m"

    def _wait_ack(self, action_name, timeout=5):
        ack = self.master.recv_match(type='COMMAND_ACK', blocking=True, timeout=timeout)
        if ack is None:
            return False, f"{action_name}: no acknowledgment received"
        if ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            return True, f"{action_name}: accepted"
        return False, f"{action_name}: rejected (result={ack.result})"
