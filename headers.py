import json

with open("data/apt1.json", "r") as f:
	data = json.load(f)
	s = set()
	for x in data["objects"]:
		s.add(x["type"])

for x in s:
	print(x)
