import urllib.request
import json
import math
import subprocess
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(REPO_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

USERNAME = "IntellectDaksh"
AVATAR_URL = "https://avatars.githubusercontent.com/u/296588924?u=535bf15d4c953b1362792d02dddaf82f30661b28&v=4"

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
    token = os.environ.get("GITHUB_TOKEN")
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
            description
            primaryLanguage {
              name
              color
            }
          }
        }
      }
    }
    """
    
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
        except Exception as e:
            print("GraphQL with token failed:", e)

    if not data:
        try:
            cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
        except Exception as e:
            print("Local gh cli failed:", e)

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
            "repos": repos
        }

    return {
        "contributions": 430,
        "prs": 11,
        "stars": 14,
        "streak": 6,
        "repos": [
            {"name": "Winsle", "stargazerCount": 5, "primaryLanguage": {"name": "TypeScript"}},
            {"name": "Dictator", "stargazerCount": 3, "primaryLanguage": {"name": "Python"}},
            {"name": "CashPulse", "stargazerCount": 1, "primaryLanguage": {"name": "TypeScript"}},
            {"name": "Bnb26_Terminal", "stargazerCount": 1, "primaryLanguage": {"name": "TypeScript"}},
        ]
    }

def generate_pixel_hud(contributions, prs, stars, streak):
    # Fetch base template to preserve exact crisp pixel labels
    url = f'https://www.gitskins.com/api/section/pixel-hud?username={USERNAME}&mode=dark'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        base_svg = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
    except Exception:
        # Fallback to local copy
        with open(os.path.join(ASSETS_DIR, "pixel-hud.svg"), "r", encoding="utf-8") as f:
            base_svg = f.read()

    # Extract all label rects (y >= 50)
    all_orig_rects = re.findall(r'<rect x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)" fill="([^"]+)"', base_svg)
    kept_label_rects = [
        f'<rect x="{r[0]}" y="{r[1]}" width="{r[2]}" height="{r[3]}" fill="{r[4]}"/>'
        for r in all_orig_rects if float(r[1]) >= 50 and r[4] != '#151b23'
    ]

    # Generate real pixel digits
    num_rects = []
    num_rects.extend(render_number_rects(str(contributions), 28))
    num_rects.extend(render_number_rects(str(prs), 246))
    num_rects.extend(render_number_rects(str(stars), 460))
    num_rects.extend(render_number_rects(f"{streak}D", 670))

    hud_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="880" height="84" viewBox="0 0 880 84" role="img" aria-label="COMMITS {contributions}, PULL REQS {prs}, STARS {stars}, BEST STREAK {streak}D"><style>@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}</style><rect x=".5" y=".5" width="879" height="83" rx="12" fill="#151b23" stroke="#262c36"/><g shape-rendering="crispEdges">
{''.join(num_rects)}
{''.join(kept_label_rects)}
</g></svg>"""
    return hud_svg

def generate_solar_system(repos_data):
    width = 880
    height = 520
    cx = 440
    cy = 270

    public_repos = [r for r in repos_data if r['name'] != USERNAME]
    if not public_repos:
        public_repos = repos_data

    display_repos = public_repos[:6]
    base_rx = 130
    base_ry = 65
    step_rx = 48
    step_ry = 24

    lang_colors = {
        'TypeScript': '#3178c6',
        'Python': '#3572a5',
        'Rust': '#dea584',
        'JavaScript': '#f1e05a',
        'Go': '#00add8',
        'HTML': '#e34c26',
        'CSS': '#563d7c'
    }

    import random
    rng = random.Random(42)
    stars_svg = []
    for _ in range(95):
        sx = rng.randint(15, width - 15)
        sy = rng.randint(15, height - 15)
        sr = round(rng.uniform(0.4, 1.4), 1)
        sop = round(rng.uniform(0.2, 0.85), 2)
        stars_svg.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="#fff" opacity="{sop}"/>')

    orbits_svg = []
    planets_svg = []
    angle_offsets = [0.25 * math.pi, 0.85 * math.pi, -0.35 * math.pi, -0.85 * math.pi, 0.1 * math.pi, -0.6 * math.pi]

    for idx, repo in enumerate(display_repos):
        rx = base_rx + idx * step_rx
        ry = base_ry + idx * step_ry

        orbits_svg.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#ffffff" stroke-opacity=".14" stroke-dasharray="3 6"/>'
        )

        angle = angle_offsets[idx % len(angle_offsets)]
        px = cx + rx * math.cos(angle)
        py = cy + ry * math.sin(angle)

        lang_name = repo.get('primaryLanguage', {}).get('name', 'Code') if repo.get('primaryLanguage') else 'Code'
        pcolor = lang_colors.get(lang_name, '#a78bfa')
        stars = repo.get('stargazerCount', 0)
        repo_name = repo['name']
        if len(repo_name) > 16:
            display_name = repo_name[:14] + '…'
        else:
            display_name = repo_name

        pradius = 16 if stars >= 3 else 12

        if math.cos(angle) >= 0:
            tx = px + pradius + 10
            anchor = "start"
        else:
            tx = px - pradius - 10
            anchor = "end"

        star_str = f" ★ {stars}" if stars > 0 else ""
        label_text = f"{display_name}{star_str}"

        planets_svg.append(f"""
    <!-- Planet: {repo_name} -->
    <g class="planet-group">
      <circle cx="{px:.1f}" cy="{py:.1f}" r="{pradius + 5}" fill="{pcolor}" opacity=".25" class="pulse"/>
      <circle cx="{px:.1f}" cy="{py:.1f}" r="{pradius}" fill="{pcolor}"/>
      <circle cx="{px - pradius*0.3:.1f}" cy="{py - pradius*0.3:.1f}" r="{pradius*0.35:.1f}" fill="#ffffff" opacity=".35"/>
      <text x="{tx:.1f}" y="{py - 2:.1f}" text-anchor="{anchor}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12" font-weight="700" fill="#ffffff" opacity=".95">{label_text}</text>
      <text x="{tx:.1f}" y="{py + 12:.1f}" text-anchor="{anchor}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="10" fill="{pcolor}" opacity=".85">{lang_name}</text>
    </g>""")

    comet_svg = """
    <!-- Shooting Comet representing recent pushes -->
    <g class="comet">
      <line x1="0" y1="0" x2="-80" y2="-20" stroke="#ffffff" stroke-opacity=".7" stroke-width="2"/>
      <circle r="3.5" fill="#fff"/>
      <text x="8" y="-6" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="10" fill="#ffffff" opacity=".85">recent push</text>
      <animateMotion dur="11s" repeatCount="indefinite" path="M100,-40 L800,420"/>
    </g>
    <g class="comet" style="animation-delay: 5.5s;">
      <line x1="0" y1="0" x2="-90" y2="-24" stroke="#58a6ff" stroke-opacity=".6" stroke-width="2"/>
      <circle r="3" fill="#58a6ff"/>
      <animateMotion dur="13s" begin="5.5s" repeatCount="indefinite" path="M-60,180 L950,380"/>
    </g>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Daksh's Solar System of Public Repositories">
  <style>
    .pulse {{ animation: pulse 4s ease-in-out infinite; }}
    @keyframes pulse {{ 50% {{ transform: scale(1.08); transform-origin: {cx}px {cy}px; }} }}
    .comet {{ opacity: 0; animation: cm 11s linear infinite; }}
    @keyframes cm {{ 0% {{ opacity: 0; }} 6% {{ opacity: 1; }} 65% {{ opacity: 1; }} 75% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>

  <defs>
    <clipPath id="space-clip">
      <rect width="{width}" height="{height}" rx="16"/>
    </clipPath>
    <radialGradient id="sunglow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffd36b" stop-opacity=".65"/>
      <stop offset="45%" stop-color="#ffd36b" stop-opacity=".25"/>
      <stop offset="100%" stop-color="#ffd36b" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="sun-avatar-clip">
      <circle cx="{cx}" cy="{cy}" r="35"/>
    </clipPath>
  </defs>

  <g clip-path="url(#space-clip)">
    <rect width="{width}" height="{height}" fill="#05070f"/>
    {''.join(stars_svg)}
    {''.join(orbits_svg)}
    {comet_svg}

    <!-- Central Sun (Daksh) -->
    <g>
      <circle cx="{cx}" cy="{cy}" r="115" fill="url(#sunglow)" class="pulse"/>
      <circle cx="{cx}" cy="{cy}" r="43" fill="#ffd36b" opacity=".35"/>
      <circle cx="{cx}" cy="{cy}" r="38" fill="#ffd36b"/>
      <image href="{AVATAR_URL}" x="{cx - 35}" y="{cy - 35}" width="70" height="70" clip-path="url(#sun-avatar-clip)"/>
    </g>

    {''.join(planets_svg)}

    <text x="24" y="34" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12" letter-spacing=".12em" font-weight="700" fill="#ffffff" opacity=".9">SOLAR SYSTEM • @INTELLECTDAKSH</text>
    <text x="{width - 24}" y="{height - 20}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" fill="#ffffff" opacity=".75" text-anchor="end">planets = public repos • comets = recent pushes</text>
  </g>
</svg>"""
    return svg

def fetch_and_clean_room():
    url = f'https://www.gitskins.com/api/section/pixel-room?username={USERNAME}&mode=dark'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    svg = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
    svg = re.sub(r'<text[^>]*>gitskins\.com</text>', '', svg)
    svg = re.sub(r'gitskins\.com', '', svg, flags=re.IGNORECASE)
    return svg

def main():
    print("Fetching real stats and repositories...")
    stats = get_real_stats_and_repos()

    print("Generating pixel-hud.svg with authentic pixel digits...")
    hud_svg = generate_pixel_hud(stats['contributions'], stats['prs'], stats['stars'], stats['streak'])
    with open(os.path.join(ASSETS_DIR, "pixel-hud.svg"), "w", encoding="utf-8") as f:
        f.write(hud_svg)

    print("Generating solar-orbits.svg with public repositories...")
    solar_svg = generate_solar_system(stats['repos'])
    with open(os.path.join(ASSETS_DIR, "solar-orbits.svg"), "w", encoding="utf-8") as f:
        f.write(solar_svg)

    print("Updating pixel-room.svg (watermark-free)...")
    try:
        room_svg = fetch_and_clean_room()
        with open(os.path.join(ASSETS_DIR, "pixel-room.svg"), "w", encoding="utf-8") as f:
            f.write(room_svg)
    except Exception as e:
        print("Could not refresh pixel-room:", e)

    print("Done! All assets generated.")

if __name__ == '__main__':
    main()
