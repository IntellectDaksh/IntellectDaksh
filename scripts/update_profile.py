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

# GitHub language colors
LANG_COLORS = {
    "TypeScript": {"fill": "#3178c6", "icon": "#lg-typescript"},
    "JavaScript": {"fill": "#f1e05a", "icon": "#lg-javascript"},
    "Python": {"fill": "#3572A5", "icon": "#lg-python"},
    "Rust": {"fill": "#dea584", "icon": "#lg-rust"},
    "HTML": {"fill": "#e34c26", "icon": "#lg-html5"},
    "CSS": {"fill": "#563d7c", "icon": "#lg-html5"},
    "C++": {"fill": "#f34b7d", "icon": "#lg-rust"},
    "Go": {"fill": "#00ADD8", "icon": "#lg-typescript"},
    "Shell": {"fill": "#89e051", "icon": "#lg-javascript"},
}

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

def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "Daksh-Profile-Updater"}
    if token:
        headers["Authorization"] = f"bearer {token}"
    return headers

def fetch_github_data():
    headers = get_headers()
    token = os.environ.get("GITHUB_TOKEN")
    
    # 1. Fetch public repositories
    repos = []
    try:
        req = urllib.request.Request(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=pushed", headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_repos = json.loads(resp.read().decode('utf-8'))
            for r in raw_repos:
                if not r.get("fork") and r.get("name") != USERNAME:
                    repos.append({
                        "name": r["name"],
                        "stars": r["stargazers_count"],
                        "language": r["language"] or "TypeScript",
                        "pushed_at": r["pushed_at"],
                        "description": r.get("description") or ""
                    })
    except Exception as e:
        print("Error fetching repos:", e)

    if not repos:
        repos = [
            {"name": "Winsle", "stars": 5, "language": "TypeScript", "pushed_at": "2026-11-08T20:09:39Z"},
            {"name": "Dictator", "stars": 3, "language": "Python", "pushed_at": "2026-11-08T20:07:05Z"},
            {"name": "Inkloom-AI-CodeTitans-2026", "stars": 1, "language": "JavaScript", "pushed_at": "2026-11-12T20:50:25Z"},
            {"name": "Bnb26_Terminal_maharashtra_round", "stars": 1, "language": "TypeScript", "pushed_at": "2026-10-03T22:13:53Z"},
            {"name": "Jugad.exe-CashPulse", "stars": 1, "language": "TypeScript", "pushed_at": "2026-09-17T07:22:21Z"},
        ]

    # 2. Fetch commits across top repos
    all_commits = []
    target_repos = [r["name"] for r in repos[:5]]
    for r_name in target_repos:
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{USERNAME}/{r_name}/commits?per_page=4", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                commits = json.loads(resp.read().decode('utf-8'))
                for c in commits:
                    msg = c['commit']['message'].split('\n')[0].strip()
                    date = c['commit']['committer']['date']
                    short_repo = r_name[:14]
                    all_commits.append({
                        "repo": short_repo,
                        "msg": msg,
                        "date": date
                    })
        except Exception:
            pass

    all_commits.sort(key=lambda x: x["date"], reverse=True)
    
    # 3. Fetch GraphQL stats (contributions, PRs, streak)
    stats = {
        "contributions": 438,
        "prs": 11,
        "stars": sum(r["stars"] for r in repos),
        "streak": 6
    }
    
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
      }
    }
    """
    if token:
        try:
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=json.dumps({"query": query}).encode('utf-8'),
                headers={"Authorization": f"bearer {token}", "User-Agent": "Daksh-Profile-Updater", "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as res:
                data = json.loads(res.read().decode('utf-8'))
                u = data.get("data", {}).get("user", {})
                cc = u.get("contributionsCollection", {})
                cal = cc.get("contributionCalendar", {})
                if cal.get("totalContributions"):
                    stats["contributions"] = cal["totalContributions"]
                    stats["prs"] = cc.get("totalPullRequestContributions", stats["prs"])
                    
                    # calculate streak
                    days = [d["contributionCount"] for w in cal.get("weeks", []) for d in w.get("contributionDays", [])]
                    streak, best = 0, 0
                    for c in days:
                        if c > 0:
                            streak += 1
                            if streak > best: best = streak
                        else:
                            streak = 0
                    stats["streak"] = max(best, 1)
        except Exception as e:
            print("GraphQL query skipped/failed:", e)

    return {
        "stats": stats,
        "repos": repos,
        "commits": all_commits
    }

def update_pixel_hud(stats):
    hud_path = os.path.join(ASSETS_DIR, "pixel-hud.svg")
    if not os.path.exists(hud_path):
        return
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
    print("✓ pixel-hud.svg updated successfully!")

def update_pixel_room(commits, repos):
    room_path = os.path.join(ASSETS_DIR, "pixel-room.svg")
    if not os.path.exists(room_path):
        return
    with open(room_path, "r", encoding="utf-8") as f:
        svg = f.read()

    # 1. Clean any watermark remnants
    svg = re.sub(r'<g aria-label="Pro preview:.*?<\/g>\s*<\/g>', '', svg, flags=re.DOTALL)
    svg = re.sub(r'gitskins\.com', '', svg, flags=re.IGNORECASE)

    # 2. Build 8 commit lines for the monitor
    formatted_lines = ["$ git log --oneline"]
    for c in commits:
        if len(formatted_lines) >= 9:
            break
        line_text = f"{c['repo']}: {c['msg']}"
        if len(line_text) > 42:
            line_text = line_text[:40] + ".."
        line_text = line_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        formatted_lines.append(line_text)

    default_commits = [
        "Winsle: docs: document workspaces.rs",
        "Dictator: feat: add local whisper transcription",
        "Inkloom-AI-Cod: rebrand: rename to AdSnitch",
        "Winsle: feat: dynamic island coding cockpit",
        "Bnb26_Terminal: update terminal round UI",
        "Jugad.exe-CashPulse: fix predictive score",
        "Dictator: docs: update quickstart guide",
        "Winsle: refactor: hotkey listener pipeline"
    ]
    for dc in default_commits:
        if len(formatted_lines) >= 9:
            break
        formatted_lines.append(dc)

    # Render lines with repeat for seamless infinite scroll
    line_y = 35.0
    text_elements = []
    for line in formatted_lines:
        color = "#c9d1d9" if line.startswith("$") else "#7ee787"
        text_elements.append(f'<text x="86" y="{line_y:.1f}" font-family="ui-monospace,SFMono-Regular,\'SF Mono\',Menlo,Consolas,monospace" font-size="2.6" fill="{color}">{line}</text>')
        line_y += 4.2

    for line in formatted_lines:
        color = "#c9d1d9" if line.startswith("$") else "#7ee787"
        text_elements.append(f'<text x="86" y="{line_y:.1f}" font-family="ui-monospace,SFMono-Regular,\'SF Mono\',Menlo,Consolas,monospace" font-size="2.6" fill="{color}">{line}</text>')
        line_y += 4.2

    scroll_h = -(len(formatted_lines) * 4.2)
    new_scroll_group = f'<g class="scroll" style="--h:{scroll_h:.1f}px">{"".join(text_elements)}</g>'

    svg = re.sub(r'<g class="scroll"[^>]*>.*?</g>', new_scroll_group, svg, flags=re.DOTALL)

    # 3. Update bookshelf book colors based on repos' top languages
    languages_seen = []
    for r in repos:
        lang = r.get("language")
        if lang and lang in LANG_COLORS and lang not in languages_seen:
            languages_seen.append(lang)
    while len(languages_seen) < 5:
        for fallback in ["TypeScript", "Python", "Rust", "JavaScript", "HTML"]:
            if fallback not in languages_seen:
                languages_seen.append(fallback)

    svg = re.sub(r'(<rect x="171" y="32" width="7" height="12" fill=")[^"]+(")', rf'\g<1>{LANG_COLORS[languages_seen[0]]["fill"]}\g<2>', svg)
    svg = re.sub(r'(<rect x="179" y="32" width="6" height="12" fill=")[^"]+(")', rf'\g<1>{LANG_COLORS[languages_seen[3]]["fill"]}\g<2>', svg)
    svg = re.sub(r'(<rect x="186" y="32" width="4" height="12" fill=")[^"]+(")', rf'\g<1>{LANG_COLORS[languages_seen[4]]["fill"]}\g<2>', svg)
    svg = re.sub(r'(<rect x="191" y="34" width="3" height="10" fill=")[^"]+(")', rf'\g<1>{LANG_COLORS[languages_seen[2]]["fill"]}\g<2>', svg)
    svg = re.sub(r'(<rect x="195" y="35" width="3" height="9" fill=")[^"]+(")', rf'\g<1>{LANG_COLORS[languages_seen[1]]["fill"]}\g<2>', svg)

    ET.fromstring(svg)
    with open(room_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("✓ pixel-room.svg updated successfully!")

def update_solar_orbits(repos):
    solar_path = os.path.join(ASSETS_DIR, "solar-orbits.svg")
    if not os.path.exists(solar_path):
        return
    with open(solar_path, "r", encoding="utf-8") as f:
        svg = f.read()

    # 1. Clean any watermark remnants
    svg = re.sub(r'<g aria-label="Pro preview:.*?<\/g>\s*<\/g>', '', svg, flags=re.DOTALL)
    svg = re.sub(r'gitskins\.com', '', svg, flags=re.IGNORECASE)

    # 2. Select 5 repositories for orbits
    planet_repos = [r for r in repos if r.get("name") != USERNAME][:5]
    defaults = [
        {"name": "Winsle", "stars": 5, "language": "TypeScript"},
        {"name": "Dictator", "stars": 3, "language": "Python"},
        {"name": "Inkloom-AI-CodeTitans-2026", "stars": 1, "language": "JavaScript"},
        {"name": "Bnb26_Terminal_maharashtra_round", "stars": 1, "language": "TypeScript"},
        {"name": "Jugad.exe-CashPulse", "stars": 1, "language": "TypeScript"},
    ]
    for d in defaults:
        if len(planet_repos) >= 5:
            break
        if not any(p["name"] == d["name"] for p in planet_repos):
            planet_repos.append(d)

    # 3. Update planet text labels & colors on orbits 0..4
    for idx, p in enumerate(planet_repos):
        name = p["name"]
        lang = p.get("language") or "TypeScript"
        lang_color = LANG_COLORS.get(lang, LANG_COLORS["TypeScript"])["fill"]
        
        # Replace orbit planet color and label
        pattern = rf'(<path id="orbit{idx}".*?<circle r="[\d.]+" fill=")[^"]+(".*?<text[^>]*>)[^<]+(</text>.*?<animateMotion)'
        match = re.search(pattern, svg, re.DOTALL)
        if match:
            svg = svg[:match.start()] + match.group(1) + lang_color + match.group(2) + name + match.group(3) + svg[match.end():]

    # 4. Update comets (recent pushes)
    comet_repos = [r["name"] for r in planet_repos[:3]]
    while len(comet_repos) < 3:
        comet_repos.append("Winsle")

    def replace_comet(match, count=[0]):
        idx = count[0]
        count[0] += 1
        raw_name = comet_repos[idx % len(comet_repos)]
        display_name = (raw_name[:16] + "..") if len(raw_name) > 18 else raw_name
        return f"{match.group(1)}{display_name}{match.group(3)}"

    svg = re.sub(r'(<g class="comet"[^>]*>.*?<text[^>]*>)([^<]+)(</text>)', replace_comet, svg, flags=re.DOTALL)

    # 5. Clean legend text
    svg = re.sub(r'>planets\s*=\s*languages[^<]*<', '>planets = public repos • moons = stars • comets = recent pushes<', svg)

    ET.fromstring(svg)
    with open(solar_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("✓ solar-orbits.svg updated successfully!")

def main():
    print("Fetching live data from GitHub API...")
    data = fetch_github_data()
    stats = data["stats"]
    repos = data["repos"]
    commits = data["commits"]
    
    print(f"Stats: {stats['contributions']} commits, {stats['prs']} PRs, {stats['stars']} stars, {stats['streak']}d streak")
    print(f"Public repos found: {[r['name'] for r in repos]}")
    print(f"Recent commits found: {len(commits)}")
    
    update_pixel_hud(stats)
    update_pixel_room(commits, repos)
    update_solar_orbits(repos)
    print("All profile assets updated cleanly with ZERO external dependencies!")

if __name__ == '__main__':
    main()
