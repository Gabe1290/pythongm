#!/usr/bin/env python3
import json

with open('Projects/Sokoban_test/project.json', 'r') as f:
    data = json.load(f)
    rooms = data.get('assets', {}).get('rooms', {})
    print(f"Room order from direct JSON load: {list(rooms.keys())}")
