"""Hook do MkDocs que desenha o quadro Kanban do GitHub Projects nas páginas.

Onde a página tiver o marcador <!-- kanban -->, ele é trocado pelo quadro.
Os dados são buscados na API do GitHub na hora do build, porque o projeto é
privado e o site é estático (não dá para guardar token no navegador).

Token (primeiro que existir):
  1. variável de ambiente KANBAN_TOKEN (usada no GitHub Actions)
  2. variável GH_TOKEN ou GITHUB_TOKEN
  3. `gh auth token` (para quem tem o GitHub CLI logado na máquina)
Sem token, o marcador vira um aviso com link para o quadro e o build continua.

O projeto é configurado no mkdocs.yml:

    extra:
      kanban:
        org: team-titans-unb   # dono do projeto (organização)
        project: 17            # número que aparece na URL .../projects/17
"""

import html
import logging
import os
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone

import requests

MARKER = "<!-- kanban -->"
CACHE_SECONDS = 300  # no `mkdocs serve`, evita bater na API a cada salvamento

# Nome de logger fora de "mkdocs." para que avisos não derrubem o build --strict
log = logging.getLogger("kanban")

QUERY = """
query($org: String!, $number: Int!, $after: String) {
  organization(login: $org) {
    projectV2(number: $number) {
      title
      field(name: "Status") {
        ... on ProjectV2SingleSelectField { options { id name color } }
      }
      items(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isArchived
          type
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue { optionId }
          }
          content {
            ... on DraftIssue { title }
            ... on Issue {
              title number url state
              assignees(first: 5) { nodes { login avatarUrl(size: 40) } }
              labels(first: 6) { nodes { name color } }
            }
            ... on PullRequest {
              title number url state
              assignees(first: 5) { nodes { login avatarUrl(size: 40) } }
              labels(first: 6) { nodes { name color } }
            }
          }
        }
      }
    }
  }
}
"""

# Cores dos status no GitHub Projects -> hex
COLORS = {
    "GRAY": "#8b949e",
    "BLUE": "#2f81f7",
    "GREEN": "#3fb950",
    "YELLOW": "#d29922",
    "ORANGE": "#e8681c",
    "RED": "#f85149",
    "PINK": "#db61a2",
    "PURPLE": "#a371f7",
}

_cache = {"time": 0.0, "html": None}
_cfg = {"org": None, "project": None, "url": None}


def _token():
    for var in ("KANBAN_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(var):
            return os.environ[var]
    if shutil.which("gh"):
        try:
            out = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True, timeout=10
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def _fetch(token):
    items, after, project = [], None, None
    while True:
        resp = requests.post(
            "https://api.github.com/graphql",
            json={
                "query": QUERY,
                "variables": {"org": _cfg["org"], "number": _cfg["project"], "after": after},
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errors"):
            raise RuntimeError(data["errors"][0].get("message", "erro na API"))
        project = data["data"]["organization"]["projectV2"]
        if project is None:
            raise RuntimeError("projeto não encontrado ou sem permissão")
        page = project["items"]
        items.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    return project, items


def _card(item):
    c = item.get("content") or {}
    title = html.escape(c.get("title") or "(sem título)")
    if c.get("url"):
        head = (
            f'<a class="kanban-card__title" href="{html.escape(c["url"])}" '
            f'target="_blank" rel="noopener">{title}</a>'
        )
    else:
        head = f'<span class="kanban-card__title">{title}</span>'

    meta = []
    if c.get("number"):
        kind = "PR" if item["type"] == "PULL_REQUEST" else "Issue"
        meta.append(f'<span class="kanban-card__num">{kind} #{c["number"]}</span>')
    elif item["type"] == "DRAFT_ISSUE":
        meta.append('<span class="kanban-card__num">Rascunho</span>')

    labels = "".join(
        f'<span class="kanban-label" style="--label:#{html.escape(l["color"])}">'
        f'{html.escape(l["name"])}</span>'
        for l in (c.get("labels") or {}).get("nodes", [])
    )
    people = "".join(
        f'<img class="kanban-avatar" src="{html.escape(a["avatarUrl"])}" '
        f'alt="{html.escape(a["login"])}" title="{html.escape(a["login"])}" '
        f'width="20" height="20" loading="lazy">'
        for a in (c.get("assignees") or {}).get("nodes", [])
    )
    foot = "".join(meta) + (f'<span class="kanban-card__people">{people}</span>' if people else "")
    return (
        f'<li class="kanban-card">{head}'
        + (f'<div class="kanban-card__labels">{labels}</div>' if labels else "")
        + (f'<div class="kanban-card__foot">{foot}</div>' if foot else "")
        + "</li>"
    )


def _render(project, items):
    options = (project.get("field") or {}).get("options") or []
    columns = {o["id"]: [] for o in options}
    no_status = []
    for item in items:
        if item.get("isArchived"):
            continue
        opt = (item.get("fieldValueByName") or {}).get("optionId")
        columns.get(opt, no_status).append(item)

    cols = []
    if no_status:
        cols.append(("Sem status", "GRAY", no_status))
    cols += [(o["name"], o["color"], columns[o["id"]]) for o in options]

    parts = []
    for name, color, col_items in cols:
        cards = "".join(_card(i) for i in col_items) or '<li class="kanban-empty">Vazio</li>'
        parts.append(
            f'<section class="kanban-col" style="--status:{COLORS.get(color, COLORS["GRAY"])}">'
            f'<header class="kanban-col__head"><span class="kanban-dot"></span>'
            f'{html.escape(name)}<span class="kanban-count">{len(col_items)}</span></header>'
            f'<ul class="kanban-list">{cards}</ul></section>'
        )

    # Horário de Brasília (UTC-3)
    now = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
    return (
        '<div class="kanban" markdown="0">'
        f'<div class="kanban-board">{"".join(parts)}</div>'
        f'<p class="kanban-foot">Atualizado em {now} · '
        f'<a href="{_cfg["url"]}" target="_blank" rel="noopener">Abrir no GitHub Projects</a></p>'
        "</div>"
    )


def _fallback(reason):
    link = (
        f' <a href="{_cfg["url"]}" target="_blank" rel="noopener">Abrir no GitHub Projects</a>.'
        if _cfg["url"]
        else ""
    )
    return (
        '<div class="admonition info"><p class="admonition-title">Quadro Kanban</p>'
        f"<p>Não foi possível carregar o quadro ({html.escape(reason)}).{link}</p></div>"
    )


def _board_html():
    if not _cfg["url"]:
        return _fallback("configure extra.kanban no mkdocs.yml")
    if _cache["html"] and time.time() - _cache["time"] < CACHE_SECONDS:
        return _cache["html"]
    token = _token()
    if not token:
        log.info("kanban: sem token do GitHub, mostrando só o link do quadro")
        return _fallback("sem token do GitHub no build")
    try:
        board = _render(*_fetch(token))
    except Exception as exc:  # o site não pode deixar de ser gerado por causa do quadro
        log.warning("kanban: falha ao buscar o projeto: %s", exc)
        return _fallback("erro ao acessar a API do GitHub")
    _cache.update(time=time.time(), html=board)
    return board


def on_config(config):
    kanban = (config.get("extra") or {}).get("kanban") or {}
    org, project = kanban.get("org"), kanban.get("project")
    try:
        project = int(project)
    except (TypeError, ValueError):
        project = None
    if org and project:
        _cfg.update(
            org=org, project=project, url=f"https://github.com/orgs/{org}/projects/{project}"
        )
    else:
        _cfg.update(org=None, project=None, url=None)
    return config


def on_page_content(html_content, page, config, files):
    if MARKER not in html_content:
        return html_content
    return html_content.replace(MARKER, _board_html())
