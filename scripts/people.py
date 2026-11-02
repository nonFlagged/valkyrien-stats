"""Refresh public demo profiles and durable avatar files (no expiring CDN links)."""
import hashlib
import json
from pathlib import Path
import time
import urllib.request

OWNER = 1960518316
TRADERS = [96498234, 991697453, 80254, 5866753, 2207291, 5649499, 52040320, 291377849, 261]
IDS = [OWNER] + TRADERS
ROOT = Path(__file__).resolve().parents[1]
AVATARS = ROOT / 'avatars'
AVATARS.mkdir(exist_ok=True)


def request(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "valkyrien-stats"})
    return urllib.request.urlopen(req, timeout=30)


def get(url, data=None):
    with request(url, data) as r:
        return json.load(r)


users = {u["id"]: u for u in get("https://users.roblox.com/v1/users", json.dumps({"userIds": IDS, "excludeBannedUsers": False}).encode())["data"]}
shots = get("https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=" + ",".join(map(str, IDS)) + "&size=150x150&format=Png&isCircular=false")["data"]
heads = {s["targetId"]: s["imageUrl"] for s in shots if s.get("state") == "Completed"}
previous = json.loads((ROOT / 'people.json').read_text()) if (ROOT / 'people.json').exists() else {}
old = {p['id']: p for p in previous.get('people', [])}
people = []
for uid in IDS:
    u = users.get(uid)
    if not u:
        continue
    avatar = old.get(str(uid), {}).get('avatar', '')
    if uid in heads:
        try:
            with request(heads[uid]) as response:
                raw = response.read()
            (AVATARS / f'{uid}.png').write_bytes(raw)
            revision = hashlib.sha256(raw).hexdigest()[:12]
            avatar = f'https://raw.githubusercontent.com/nonFlagged/valkyrien-stats/main/avatars/{uid}.png?v={revision}'
        except Exception:
            if 'raw.githubusercontent.com' not in avatar:
                avatar = ''
    people.append({"id": str(uid), "name": u["name"], "display": u["displayName"], "avatar": avatar})

out = {"owner": str(OWNER), "people": people}
if all(previous.get(k) == out[k] for k in out):
    print('unchanged')
else:
    out['updated_at'] = int(time.time())
    (ROOT / 'people.json').write_text(json.dumps(out, indent=1) + '\n')
    print('updated', len(people))
