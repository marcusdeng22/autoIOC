import json
import os

s = set()

for file in os.listdir("data"):
	if file.endswith(".json"):
		with open(os.path.join("data", file), "r") as f:
			data = json.load(f)
			for x in data["objects"]:
				s.add(x["type"])

for x in s:
	print(x)
