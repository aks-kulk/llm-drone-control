import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a drone command interpreter. Convert natural language commands into structured JSON.

Valid actions: arm, disarm, takeoff, land, rtl, set_mode, move_north, move_south, move_east, move_west

Output ONLY valid JSON in this exact format, nothing else:
{"action": "<action>", "parameters": {<relevant params>}}

Examples:
"take off to 10 meters" -> {"action": "takeoff", "parameters": {"altitude": 10}}
"arm the drone" -> {"action": "arm", "parameters": {}}
"move 20 meters north" -> {"action": "move_north", "parameters": {"distance": 20}}
"return to launch" -> {"action": "rtl", "parameters": {}}
"land the drone" -> {"action": "land", "parameters": {}}
"switch to guided mode" -> {"action": "set_mode", "parameters": {"mode": "GUIDED"}}

If the command doesn't match any valid action, respond with:
{"action": "unknown", "parameters": {}}
"""

def interpret_command(user_input: str) -> dict:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"action": "error", "parameters": {"raw_output": raw}}
