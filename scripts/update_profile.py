import urllib.request
import json
import re
import os
import xml.etree.ElementTree as ET

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(REPO_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

USERNAME = "IntellectDaksh"
AVATAR_BASE64_URL = "https://www.gitskins.com/api/section/solar-orbits?username=intellectdaksh&avatar=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F296588924%3Fu%3D535bf15d4c953b1362792d02dddaf82f30661b28%26v%3D4&mode=dark"

DIGITS = {
    '0': [
        (4, 0, 12, 4), (0, 4, 4, 4), (16, 4, 4, 4), (0, 8, 4, 4), (16, 8, 4, 4),
        (0, 12, 4, 4), (16, 12, 4, 4), (0, 16, 4, 4), (16, 16, 4, 4),
        (0, 20, 4, 4), (16, 20, 4, 4), (4, 24, 12, 4)
    ],
    '1': [
        (4, 0, 4, 4), (0, 4, 8, 4), (4, 8, 4, 4), (4, 12, 4, 4),
        (4, 16, 4, 4), (4, 20, 4, 4), (0, 24, 12, 4)
    ],
    '2': [
        (4, 0, 12, 4), (0, 4, 4, 4), (16, 4, 4, 4), (16, 8, 4, 4),
        (12, 12, 4, 4), (8, 16, 4, 4), (4, 20, 4, 4), (0, 24, 20, 4)
    ],
    '3': [
        (0, 0, 16, 4), (16, 4, 4, 4), (12, 8, 4, 4), (4, 12, 12, 4),
        (16, 16, 4, 4), (16, 20, 4, 4), (0, 24, 16, 4)
    ],
    '4': [
        (12, 0, 4, 4), (8, 4, 4, 4), (4, 8, 4, 4), (0, 12, 4, 4),
        (0, 16, 20, 4), (12, 20, 4, 4), (12, 24, 4, 4)
    ],
    '5': [
        (0, 0, 20, 4), (0, 4, 4, 4), (0, 8, 16, 4), (16, 12, 4, 4),
        (16, 16, 4, 4), (16, 20, 4, 4), (0, 24, 16, 4)
    ],
    '6': [
        (8, 0, 8, 4), (4, 4, 4, 4), (0, 8, 4, 4), (0, 12, 16, 4),
        (0, 16, 4, 4), (16, 16, 4, 4), (0, 20, 4, 4), (16, 20, 4, 4), (4, 24, 12, 4)
    ],
    '7': [
        (0, 0, 20, 4), (16, 4, 4, 4), (12, 8, 4, 4), (8, 12, 4, 4),
        (4, 16, 4, 4), (4, 20, 4, 4), (4, 24, 4, 4)
    ],
    '8': [
        (4, 0, 12, 4), (0, 4, 4, 4), (16, 4, 4, 4), (4, 8, 12, 4),
        (0, 12, 4, 4), (16, 12, 4, 4), (0, 16, 4, 4), (16, 16, 4, 4),
        (0, 20, 4, 4), (16, 20, 4, 4), (4, 24, 12, 4)
    ],
    '9': [
        (4, 0, 12, 4), (0, 4, 4, 4), (16, 4, 4, 4), (0, 8, 4, 4), (16, 8, 4, 4),
        (4, 12, 16, 4), (16, 16, 4, 4), (12, 20, 4, 4), (4, 24, 8, 4)
    ],
    'D': [
        (0, 0, 16, 4), (0, 4, 4, 4), (16, 4, 4, 4), (0, 8, 4, 4), (16, 8, 4, 4),
        (0, 12, 4, 4), (16, 12, 4, 4), (0, 16, 4, 4), (16, 16, 4, 4),
        (0, 20, 4, 4), (16, 20, 4, 4), (0, 24, 16, 4)
    ]
}

def render_number_rects(text_str, start_x):
    rects = []
    curr_x = start_x
    for ch in text_str:
        if ch in DIGITS:
            char_width = 12 if ch == '1' else 20
            for rx, ry, w, h in DIGITS[ch]:
                rects.append(f'<rect x="{curr_x + rx}" y="{18 + ry}" width="{w}" height="{h}" fill="#f0f6fc"/>')
            curr_x += char_width + 4
        else:
            curr_x += 8
    return rects

def get_real_stats_and_repos():
    import subprocess
    query = """
    query {
      user(login: "IntellectDaksh") {
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
        repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER, orderBy: {field: STARGAZERS, direction: DESC}) {
          nodes {
            name
            stargazerCount
            primaryLanguage {
              name
              color
            }
          }
        }
      }
    }
    """
    token = os.environ.get("GITHUB_TOKEN")
    data = None
    if token:
        try:
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=json.dumps({"query": query}).encode('utf-8'),
                headers={
                    "Authorization": f"bearer {token}",
                    "User-Agent": "Profile-Updater",
                    "Content-Type": "application/json"
                }
            )
            res = urllib.request.urlopen(req, timeout=15)
            data = json.loads(res.read().decode('utf-8'))
        except Exception:
            pass

    if not data:
        try:
            cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
        except Exception:
            pass

    if data and "data" in data and data["data"]["user"]:
        u = data["data"]["user"]
        cal = u["contributionsCollection"]["contributionCalendar"]
        total_contributions = cal["totalContributions"]
        prs = u["contributionsCollection"]["totalPullRequestContributions"]
        repos = u["repositories"]["nodes"]
        total_stars = sum(r["stargazerCount"] for r in repos)
        days = []
        for w in cal["weeks"]:
            for d in w["contributionDays"]:
                days.append(d["contributionCount"])
        longest_streak = 0
        curr = 0
        for c in days:
            if c > 0:
                curr += 1
                if curr > longest_streak:
                    longest_streak = curr
            else:
                curr = 0

        return {
            "contributions": total_contributions,
            "prs": prs,
            "stars": total_stars,
            "streak": longest_streak,
            "repos": [r['name'] for r in repos if r['name'] != USERNAME]
        }

    return {
        "contributions": 430,
        "prs": 11,
        "stars": 14,
        "streak": 6,
        "repos": ["Winsle", "Dictator", "Jugad.exe-Manipal-Hackathon-CashPulse", "Bnb26_Terminal_maharashtra_round"]
    }

def update_pixel_hud(stats):
    hud_path = os.path.join(ASSETS_DIR, "pixel-hud.svg")
    with open(hud_path, "r", encoding="utf-8") as f:
        base_svg = f.read()

    all_orig_rects = re.findall(r'<rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)" fill="([^"]+)"', base_svg)
    kept_label_rects = [
        f'<rect x="{r[0]}" y="{r[1]}" width="{r[2]}" height="{r[3]}" fill="{r[4]}"/>'
        for r in all_orig_rects if float(r[1]) >= 50 and r[4] != '#151b23'
    ]

    num_rects = []
    num_rects.extend(render_number_rects(str(stats['contributions']), 28))
    num_rects.extend(render_number_rects(str(stats['prs']), 246))
    num_rects.extend(render_number_rects(str(stats['stars']), 460))
    num_rects.extend(render_number_rects(f"{stats['streak']}D", 670))

    hud_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="880" height="84" viewBox="0 0 880 84" role="img" aria-label="COMMITS {stats['contributions']}, PULL REQS {stats['prs']}, STARS {stats['stars']}, BEST STREAK {stats['streak']}D"><style>@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}</style><rect x=".5" y=".5" width="879" height="83" rx="12" fill="#151b23" stroke="#262c36"/><g shape-rendering="crispEdges">
{''.join(num_rects)}
{''.join(kept_label_rects)}
</g></svg>"""
    ET.fromstring(hud_svg)
    with open(hud_path, "w", encoding="utf-8") as f:
        f.write(hud_svg)
    print("pixel-hud.svg updated successfully!")

def update_solar_orbits(stats):
    solar_path = os.path.join(ASSETS_DIR, "solar-orbits.svg")
    try:
        req = urllib.request.Request(AVATAR_BASE64_URL, headers={'User-Agent': 'Mozilla/5.0'})
        svg = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
    except Exception:
        with open(solar_path, "r", encoding="utf-8") as f:
            svg = f.read()

    svg = re.sub(r'<text[^>]*>gitskins\.com</text>', '', svg)
    svg = re.sub(r'planets\s*=\s*languages[^<]*', 'planets = public repos • moons = stars • comets = recent pushes', svg)

    repo_names = stats['repos']
    defaults = ['Winsle', 'Dictator', 'CashPulse', 'Bnb26_Terminal', 'IntellectDaksh']
    final_repos = (repo_names + defaults)[:5]

    svg = re.sub(r'>TypeScript \d+%<', f'>{final_repos[0]}<', svg)
    svg = re.sub(r'>Rust \d+%<', f'>{final_repos[1]}<', svg)
    svg = re.sub(r'>Python \d+%<', f'>{final_repos[2]}<', svg)
    svg = re.sub(r'>JavaScript \d+%<', f'>{final_repos[3]}<', svg)
    svg = re.sub(r'>CSS \d+%<', f'>{final_repos[4]}<', svg)

    ET.fromstring(svg)
    with open(solar_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("solar-orbits.svg updated successfully with public repos!")

def update_pixel_room():
    room_path = os.path.join(ASSETS_DIR, "pixel-room.svg")
    url = f'https://www.gitskins.com/api/section/pixel-room?username={USERNAME}&mode=dark'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        svg = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        svg = re.sub(r'<text[^>]*>gitskins\.com</text>', '', svg)
        ET.fromstring(svg)
        with open(room_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print("pixel-room.svg refreshed successfully!")
    except Exception as e:
        print("pixel-room fetch skipped:", e)

def main():
    stats = get_real_stats_and_repos()
    print("Real stats:", stats)
    update_pixel_hud(stats)
    update_solar_orbits(stats)
    update_pixel_room()
    print("All profile assets updated cleanly!")

if __name__ == '__main__':
    main()
