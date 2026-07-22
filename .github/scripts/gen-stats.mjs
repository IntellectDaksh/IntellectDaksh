// Generates a single custom-designed dashboard SVG (dark + light) from the
// GitHub GraphQL API instead of stitching together mismatched badge services.
import fs from "node:fs";

const USER = process.env.GH_USER;
const TOKEN = process.env.GH_TOKEN;

const query = `
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 5, orderBy: { field: SIZE, direction: DESC }) {
          edges { size node { name } }
        }
      }
    }
  }
}`;

const res = await fetch("https://api.github.com/graphql", {
  method: "POST",
  headers: {
    Authorization: `bearer ${TOKEN}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ query, variables: { login: USER } }),
});
const { data, errors } = await res.json();
if (errors) {
  console.error(errors);
  process.exit(1);
}

const u = data.user;
const totalStars = u.repositories.nodes.reduce((s, r) => s + r.stargazerCount, 0);
const totalRepos = u.repositories.totalCount;
const followers = u.followers.totalCount;
const totalContribs = u.contributionsCollection.contributionCalendar.totalContributions;

// Flatten contribution days, most recent last.
const days = u.contributionsCollection.contributionCalendar.weeks
  .flatMap((w) => w.contributionDays)
  .sort((a, b) => new Date(a.date) - new Date(b.date));

function computeStreaks(days) {
  let current = 0, longest = 0, run = 0;
  const today = new Date().toISOString().slice(0, 10);
  for (const d of days) {
    if (d.contributionCount > 0) {
      run += 1;
      longest = Math.max(longest, run);
    } else {
      run = 0;
    }
  }
  // current streak: walk backwards from today (or yesterday if today has 0 so far)
  for (let i = days.length - 1; i >= 0; i--) {
    const d = days[i];
    if (d.date > today) continue;
    if (d.contributionCount > 0) current += 1;
    else if (d.date === today) continue; // today can still be 0 without breaking streak
    else break;
  }
  return { current, longest };
}
const { current, longest } = computeStreaks(days);

// Aggregate language byte size across all repos.
const langTotals = {};
for (const r of u.repositories.nodes) {
  for (const e of r.languages.edges) {
    langTotals[e.node.name] = (langTotals[e.node.name] || 0) + e.size;
  }
}
const topLangs = Object.entries(langTotals)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 4);
const langMax = topLangs.length ? topLangs[0][1] : 1;

function svg(theme) {
  const dark = theme === "dark";
  const bg = dark ? "#0d1117" : "#ffffff";
  const card = dark ? "#161b22" : "#f6f8fa";
  const border = dark ? "#30363d" : "#d0d7de";
  const text = dark ? "#e6edf3" : "#1f2328";
  const muted = dark ? "#8b949e" : "#57606a";
  const accent = "#2f81f7";
  const font = "'Segoe UI', -apple-system, sans-serif";

  const W = 860, H = 320;
  const DIVIDER_X = 460;
  const stat = (x, y, value, label) => `
    <text x="${x}" y="${y}" font-family="${font}" font-size="28" font-weight="700" fill="${text}">${value}</text>
    <text x="${x}" y="${y + 20}" font-family="${font}" font-size="12" fill="${muted}" letter-spacing="0.5">${label.toUpperCase()}</text>`;

  // 2x2 grid, confined to the left panel (0..DIVIDER_X) so nothing crosses
  // into the languages column.
  const stats = [
    [totalRepos, "Repos"],
    [totalStars, "Stars"],
    [followers, "Followers"],
    [totalContribs, "Contributions / yr"],
  ]
    .map(([v, l], i) => stat(40 + (i % 2) * 220, 92 + Math.floor(i / 2) * 66, v, l))
    .join("");

  const bars = topLangs
    .map(([name, size], i) => {
      const y = 58 + i * 34;
      const w = Math.round((size / langMax) * 220);
      return `
      <text x="490" y="${y + 14}" font-family="${font}" font-size="13" fill="${text}">${name}</text>
      <rect x="620" y="${y}" width="220" height="10" rx="5" fill="${border}"/>
      <rect x="620" y="${y}" width="${Math.max(w, 6)}" height="10" rx="5" fill="${accent}"/>`;
    })
    .join("");

  return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="${W}" height="${H}" rx="12" fill="${bg}"/>
  <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="12" fill="none" stroke="${border}"/>
  <rect x="0" y="0" width="6" height="${H}" fill="${accent}"/>

  <text x="40" y="42" font-family="${font}" font-size="18" font-weight="700" fill="${text}">GitHub activity</text>
  <text x="40" y="62" font-family="${font}" font-size="13" fill="${muted}">@${USER}</text>

  ${stats}

  <line x1="${DIVIDER_X}" y1="30" x2="${DIVIDER_X}" y2="${H - 60}" stroke="${border}"/>

  <text x="490" y="42" font-family="${font}" font-size="13" fill="${muted}" letter-spacing="0.5">TOP LANGUAGES</text>
  ${bars}

  <line x1="40" y1="${H - 60}" x2="${W - 40}" y2="${H - 60}" stroke="${border}"/>
  <text x="40" y="${H - 25}" font-family="${font}" font-size="28" font-weight="700" fill="${accent}">${current}</text>
  <text x="40" y="${H - 8}" font-family="${font}" font-size="12" fill="${muted}">CURRENT STREAK (days)</text>
  <text x="240" y="${H - 25}" font-family="${font}" font-size="28" font-weight="700" fill="${text}">${longest}</text>
  <text x="240" y="${H - 8}" font-family="${font}" font-size="12" fill="${muted}">LONGEST STREAK (days)</text>
</svg>`;
}

fs.mkdirSync("dist", { recursive: true });
fs.writeFileSync("dist/stats-dark.svg", svg("dark"));
fs.writeFileSync("dist/stats-light.svg", svg("light"));
console.log(`repos=${totalRepos} stars=${totalStars} followers=${followers} contribs=${totalContribs} streak=${current}/${longest}`);
