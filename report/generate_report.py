import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RESULTS = ROOT / "data/results/batch_results.json"
ANALYTICS = ROOT / "data/results/analytics.json"
PRIORITIES = ROOT / "data/results/priorities.json"
OUTPUT = ROOT / "output/integration_atlas.html"


def load_json(path):
    if not path.exists():
        return []
    return json.loads(path.read_text())


def main():
    apps = load_json(RESULTS)
    analytics = load_json(ANALYTICS)
    priorities = load_json(PRIORITIES)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Embed research data directly into HTML so the report
    # works without a local web server.
    payload = json.dumps(
        {
            "apps": apps,
            "analytics": analytics,
            "priorities": priorities,
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>API Scout | Integration Atlas</title>

<style>
:root {{
    --bg: #0b1020;
    --panel: #131a2e;
    --panel2: #182139;
    --text: #edf2ff;
    --muted: #94a3b8;
    --accent: #60a5fa;
    --border: #29344d;
    --green: #34d399;
    --yellow: #fbbf24;
    --red: #f87171;
}}

* {{ box-sizing: border-box; }}

body {{
    margin: 0;
    font-family: Inter, system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
}}

header {{
    padding: 32px 5%;
    border-bottom: 1px solid var(--border);
}}

header h1 {{
    margin: 0;
    font-size: 30px;
}}

header p {{
    color: var(--muted);
}}

main {{
    padding: 30px 5%;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(180px,1fr));
    gap: 16px;
}}

.card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
}}

.card h3 {{
    color: var(--muted);
    font-size: 13px;
    font-weight: 500;
}}

.metric {{
    font-size: 30px;
    font-weight: 700;
}}

.section {{
    margin-top: 35px;
}}

.section h2 {{
    margin-bottom: 20px;
}}

input, select {{
    padding: 11px;
    background: var(--panel);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
}}

.controls {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 18px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--panel);
}}

th, td {{
    padding: 14px;
    border-bottom: 1px solid var(--border);
    text-align: left;
}}

th {{
    color: var(--muted);
    cursor: pointer;
}}

tr:hover {{
    background: var(--panel2);
}}

.badge {{
    display: inline-block;
    padding: 5px 9px;
    border-radius: 20px;
    font-size: 12px;
    background: var(--panel2);
}}

.build {{
    color: var(--green);
}}

.constrained {{
    color: var(--yellow);
}}

.blocked {{
    color: var(--red);
}}

a {{
    color: var(--accent);
}}

details {{
    padding: 10px;
    margin-top: 8px;
    background: var(--panel2);
    border-radius: 8px;
}}

.app-details {{
    padding: 20px;
    background: var(--panel);
    margin-top: 15px;
    border: 1px solid var(--border);
    border-radius: 10px;
}}

.muted {{
    color: var(--muted);
}}

@media(max-width:700px) {{
    main {{ padding: 20px; }}
    table {{ font-size: 12px; }}
    th,td {{ padding: 8px; }}
}}
</style>
</head>

<body>

<header>
    <h1>API Scout <span style="color:#60a5fa">/ Integration Atlas</span></h1>
    <p>Evidence-driven SaaS integration research and prioritization</p>
</header>

<main>

<div class="grid" id="metrics"></div>

<section class="section">
    <h2>Integration Priorities</h2>

    <div class="controls">
        <input id="search" placeholder="Search apps...">
        <select id="buildFilter">
            <option value="">All buildability</option>
            <option value="build">Build</option>
            <option value="build_with_constraints">With constraints</option>
            <option value="outreach_required">Outreach required</option>
            <option value="blocked">Blocked</option>
            <option value="unknown">Unknown</option>
        </select>
        <select id="apiFilter">
            <option value="">All API statuses</option>
            <option value="yes">API available</option>
            <option value="partial">Partial</option>
            <option value="no">No API</option>
            <option value="unknown">Unknown</option>
        </select>
    </div>

    <div style="overflow-x:auto">
        <table>
            <thead>
                <tr>
                    <th onclick="sortBy('rank')">Rank</th>
                    <th onclick="sortBy('app_name')">Application</th>
                    <th onclick="sortBy('category')">Category</th>
                    <th onclick="sortBy('priority_score')">Score</th>
                    <th>API</th>
                    <th>MCP</th>
                    <th>Buildability</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody id="ranking"></tbody>
        </table>
    </div>
</section>

<section class="section">
    <h2>Application Explorer</h2>
    <div id="explorer"></div>
</section>

<section class="section">
    <h2>Category Analysis</h2>
    <div id="categories" class="grid"></div>
</section>

</main>

<script>
const DATA = {payload};

const apps = DATA.apps || [];
const priorities = DATA.priorities || [];
const analytics = DATA.analytics || {{}};

const metrics = document.getElementById("metrics");

function pct(n,total) {{
    return total ? Math.round(n/total*100) + "%" : "0%";
}}

function renderMetrics() {{
    const total = apps.length;

    const api = apps.filter(a => a.public_api === "yes").length;
    const mcp = apps.filter(a => a.official_mcp === "yes").length;
    const build = apps.filter(a => a.buildability === "build").length;
    const review = apps.filter(a => a.human_review_required).length;

    const items = [
        ["Apps researched", total],
        ["Public APIs", api + " (" + pct(api,total) + ")"],
        ["Official MCP", mcp + " (" + pct(mcp,total) + ")"],
        ["Buildable", build + " (" + pct(build,total) + ")"],
        ["Human review", review]
    ];

    metrics.innerHTML = items.map(([title,value]) => `
        <div class="card">
            <h3>${{title}}</h3>
            <div class="metric">${{value}}</div>
        </div>
    `).join("");
}}

let sortKey = "priority_score";
let sortDirection = -1;

function sortBy(key) {{
    if (sortKey === key) {{
        sortDirection *= -1;
    }} else {{
        sortKey = key;
        sortDirection = key === "priority_score" ? -1 : 1;
    }}
    renderRanking();
}}

function badge(value) {{
    return `<span class="badge">${{value || "unknown"}}</span>`;
}}

function renderRanking() {{
    const search = document.getElementById("search").value.toLowerCase();
    const buildFilter = document.getElementById("buildFilter").value;
    const apiFilter = document.getElementById("apiFilter").value;

    const list = priorities.filter(a => {{
        return a.app_name.toLowerCase().includes(search)
            && (!buildFilter || a.buildability === buildFilter)
            && (!apiFilter || a.public_api === apiFilter);
    }}).sort((a,b) => {{
        if (sortKey === "rank") {{
            return sortDirection * (a.priority_score - b.priority_score);
        }}

        const av = a[sortKey];
        const bv = b[sortKey];

        if (typeof av === "number" && typeof bv === "number") {{
            return sortDirection * (av-bv);
        }}

        return sortDirection * String(av || "").localeCompare(String(bv || ""));
    }});

    document.getElementById("ranking").innerHTML = list.map((a,i) => `
        <tr>
            <td>${{i+1}}</td>
            <td>${{a.app_name}}</td>
            <td>${{a.category || "-"}}</td>
            <td><strong>${{a.priority_score}}</strong></td>
            <td>${{badge(a.public_api)}}</td>
            <td>${{badge(a.official_mcp)}}</td>
            <td class="${{a.buildability === 'build' ? 'build' :
                a.buildability === 'blocked' ? 'blocked' : 'constrained'}}">
                ${{a.buildability}}
            </td>
            <td>${{Math.round((a.confidence || 0)*100)}}%</td>
        </tr>
    `).join("");
}}

function renderExplorer() {{
    document.getElementById("explorer").innerHTML = apps.map(a => `
        <details>
            <summary>
                <strong>${{a.app_name}}</strong>
                — ${{a.category || "Uncategorized"}}
            </summary>

            <div class="app-details">
                <p>${{a.description || "No description available."}}</p>

                <p><strong>API:</strong> ${{a.public_api}}</p>
                <p><strong>Developer access:</strong> ${{a.developer_access}}</p>
                <p><strong>API breadth:</strong> ${{a.api_breadth}}</p>
                <p><strong>MCP:</strong> ${{a.official_mcp}}</p>
                <p><strong>Buildability:</strong> ${{a.buildability}}</p>
                <p><strong>Confidence:</strong> ${{Math.round((a.confidence || 0)*100)}}%</p>
                <p><strong>Blocker:</strong> ${{a.primary_blocker || "None recorded"}}</p>

                <h4>Evidence</h4>

                ${{(a.evidence || []).map(e => `
                    <details>
                        <summary>${{e.claim}}</summary>
                        <p>${{e.excerpt || ""}}</p>
                        <a href="${{e.url}}" target="_blank" rel="noopener">
                            View source
                        </a>
                    </details>
                `).join("") || "No evidence recorded."}}

                <h4>Sources</h4>

                ${{(a.sources || []).map(s => `
                    <p>
                        <a href="${{s.url}}" target="_blank" rel="noopener">
                            ${{s.title || s.url}}
                        </a>
                        <span class="muted">${{s.source_type || ""}}</span>
                    </p>
                `).join("") || "No sources."}}
            </div>
        </details>
    `).join("");
}}

function renderCategories() {{
    const data = analytics.category_analysis || {{}};

    document.getElementById("categories").innerHTML =
        Object.entries(data).map(([name,c]) => `
            <div class="card">
                <h3>${{name}}</h3>
                <div class="metric">${{c.total}}</div>
                <p>API: ${{c.api_available}}</p>
                <p>MCP: ${{c.mcp_available}}</p>
                <p>Build: ${{c.buildable}}</p>
                <p>Constrained: ${{c.constrained}}</p>
                <p>Outreach: ${{c.outreach_required}}</p>
                <p>Blocked: ${{c.blocked}}</p>
                <p>Unknown: ${{c.unknown}}</p>
                <p>Avg confidence: ${{Math.round(c.average_confidence*100)}}%</p>
            </div>
        `).join("");
}}

document.getElementById("search").addEventListener("input",renderRanking);
document.getElementById("buildFilter").addEventListener("change",renderRanking);
document.getElementById("apiFilter").addEventListener("change",renderRanking);

renderMetrics();
renderRanking();
renderExplorer();
renderCategories();
</script>

</body>
</html>
"""

    OUTPUT.write_text(html, encoding="utf-8")

    print(f"Integration Atlas generated: {OUTPUT}")


if __name__ == "__main__":
    main()