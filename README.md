# LLM-Based Drone Control — SITL Prototype

A prototype that lets a user control an ArduPilot SITL drone using natural language. Commands are interpreted by an LLM (Groq / Llama-based), converted into structured JSON, validated, and executed through PyMAVLink.

## Architecture

```
Natural Language Command → LLM (Groq) → Structured JSON → Validation Layer → PyMAVLink → ArduPilot SITL
```

See `architecture_diagram.png` for the full visual flow.

## Demo Video

A full demo showing the complete workflow (connect → arm → takeoff → return to launch → land) is available at [`demo/drone_demo.mov`](demo/drone_demo.mov).

## Setup Instructions

### Prerequisites

- Python 3.9+
- ArduPilot SITL installed and buildable (see [ArduPilot SITL docs](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html))
- A free [Groq API key](https://console.groq.com)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/aks-kulk/llm-drone-control.git
cd llm-drone-control
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Groq API key:
```
GROQ_API_KEY=your_key_here
```

### Running the Prototype

1. Start ArduPilot SITL in a separate terminal:
```bash
cd /path/to/ardupilot/ArduCopter
../Tools/autotest/sim_vehicle.py -v ArduCopter --console --map
```

2. In this project's directory, run:
```bash
python3 main.py
```

3. Type natural language commands at the `>>` prompt. Examples:
```
take off to 15 meters
move 20 meters north
return to launch
land
```

Type `quit` to exit.

**Note:** The prototype connects to SITL on `tcp:127.0.0.1:5762` rather than the default `5760`, since MAVProxy's console/map already occupies port 5760. ArduCopter exposes multiple output ports by default, so this avoids a port conflict.

## Command Format

The LLM converts natural language into this JSON structure:

```json
{
  "action": "takeoff",
  "parameters": {
    "altitude": 15
  }
}
```

### Supported Actions

| Action | Parameters | Example Command |
|---|---|---|
| `arm` | none | "arm the drone" |
| `disarm` | none | "disarm" |
| `takeoff` | `altitude` (1-100m) | "take off to 15 meters" |
| `land` | none | "land the drone" |
| `rtl` | none | "return to launch" |
| `set_mode` | `mode` (GUIDED/STABILIZE/AUTO/LOITER/RTL/LAND) | "switch to guided mode" |
| `move_north` / `move_south` / `move_east` / `move_west` | `distance` (1-500m) | "move 20 meters north" |

## Validation Layer

Before any command reaches PyMAVLink, it passes through `validator.py`, which checks:
- The action is one of the recognized valid actions
- Takeoff altitude is a number between 1 and 100 meters
- Movement distance is a number between 1 and 500 meters
- Flight mode is one of the valid ArduCopter modes

The LLM never directly calls PyMAVLink — all structured output is validated first, and invalid commands are rejected with a clear error message instead of being executed.

## Project Structure

```
llm-drone-control/
├── main.py               # CLI loop
├── llm_interface.py      # Groq API call + prompt + JSON parsing
├── validator.py          # Validation layer between LLM and PyMAVLink
├── drone_controller.py   # PyMAVLink connection and drone control functions
├── telemetry.py          # Reads and prints altitude, mode, GPS position
├── requirements.txt
├── architecture_diagram.png
├── demo/
│   └── drone_demo.mov
└── README.md
```

## Sample Session

```
>> take off to 15 meters
  [LLM] Interpreting command...
  [LLM Output] {'action': 'takeoff', 'parameters': {'altitude': 15}}
  [Validation OK] Executing: takeoff
  [✓] Takeoff to 15m: accepted
  [Telemetry] Alt: 14.98m | Mode: GUIDED | Armed: True | Lat: -35.363262 | Lon: 149.165237

>> return to launch
  [LLM] Interpreting command...
  [LLM Output] {'action': 'rtl', 'parameters': {}}
  [Validation OK] Executing: rtl
  [✓] Mode set to RTL
  [Telemetry] Alt: 12.4m | Mode: RTL | Armed: True | Lat: -35.363251 | Lon: 149.165230
```

## Limitations

- Relative movement commands (`move_north`/`south`/`east`/`west`) execute without error but currently lack a follow-up telemetry check to confirm displacement, and require the drone to already be in GUIDED mode for the position target to take effect.
- Telemetry is polled on-demand after each command rather than streamed continuously.
- No persistent conversation memory — each command is interpreted independently, so multi-step natural language instructions (e.g. "take off and then move north") are not currently supported in a single input.
- Groq model availability changes over time; the model name in `llm_interface.py` may need to be updated periodically (see [Groq's model deprecation page](https://console.groq.com/docs/deprecations)).
- Tested only in SITL — not yet validated against real flight controller hardware.

## Future Improvements

- Add continuous telemetry streaming instead of on-demand polling
- Support multi-step compound commands in a single natural language input
- Add unit tests for the validation layer
- Support absolute GPS waypoint commands ("fly to latitude X, longitude Y") in addition to relative movement
- Add a safety geofence check in the validation layer before executing movement or takeoff commands
- Confirm GUIDED mode is active before allowing movement commands, with automatic mode-switching if needed

## Author

Akshay Kulkarni
