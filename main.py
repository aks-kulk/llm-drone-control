from drone_controller import DroneController
from llm_interface import interpret_command
from validator import validate_command
from telemetry import print_telemetry

ACTION_MAP = {
    "arm": lambda d, p: d.arm(),
    "disarm": lambda d, p: d.disarm(),
    "takeoff": lambda d, p: d.takeoff(p.get("altitude")),
    "land": lambda d, p: d.land(),
    "rtl": lambda d, p: d.rtl(),
    "set_mode": lambda d, p: d.set_mode(p.get("mode")),
    "move_north": lambda d, p: d.move_relative("move_north", p.get("distance")),
    "move_south": lambda d, p: d.move_relative("move_south", p.get("distance")),
    "move_east": lambda d, p: d.move_relative("move_east", p.get("distance")),
    "move_west": lambda d, p: d.move_relative("move_west", p.get("distance")),
}

def main():
    print("=" * 60)
    print("LLM-Based Drone Control — SITL Prototype")
    print("=" * 60)

    drone = DroneController("tcp:127.0.0.1:5762")

    print("\nType a natural language command (or 'quit' to exit)")
    print("Examples: 'take off to 10 meters', 'move 20 meters north', 'land'\n")

    while True:
        user_input = input(">> ").strip()
        if user_input.lower() in ("quit", "exit"):
            print("Exiting.")
            break
        if not user_input:
            continue

        print("  [LLM] Interpreting command...")
        command = interpret_command(user_input)
        print(f"  [LLM Output] {command}")

        is_valid, message = validate_command(command)
        if not is_valid:
            print(f"  [Validation FAILED] {message}\n")
            continue

        print(f"  [Validation OK] Executing: {command['action']}")
        action_fn = ACTION_MAP.get(command["action"])
        if action_fn is None:
            print(f"  [Error] No handler for action: {command['action']}\n")
            continue

        success, result_msg = action_fn(drone, command.get("parameters", {}))
        status = "✓" if success else "✗"
        print(f"  [{status}] {result_msg}")

        print_telemetry(drone.master)
        print()

if __name__ == "__main__":
    main()
