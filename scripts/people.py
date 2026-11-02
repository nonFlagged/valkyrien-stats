import json
import urllib.request

OWNER = 1960518316
TRADERS = [89171402, 96498234, 308941007, 991697453, 343780622, 2512162544, 418138350]
IDS = [OWNER] + TRADERS


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "valkyrien-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


users = {u["id"]: u for u in get("https://users.roblox.com/v1/users", json.dumps({"userIds": IDS, "excludeBannedUsers": False}).encode())["data"]}
shots = get("https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=" + ",".join(map(str, IDS)) + "&size=150x150&format=Png&isCircular=false")["data"]
heads = {s["targetId"]: s["imageUrl"] for s in shots if s.get("state") == "Completed"}

people = []
for uid in IDS:
    u = users.get(uid)
    if not u:
        continue
    people.append({"id": str(uid), "name": u["name"], "display": u["displayName"], "avatar": heads.get(uid, "")})

out = {"owner": str(OWNER), "people": people}
try:
    with open("people.json") as f:
        if json.load(f) == out:
            print("unchanged")
            raise SystemExit(0)
except FileNotFoundError:
    pass

with open("people.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print("updated", len(people))
