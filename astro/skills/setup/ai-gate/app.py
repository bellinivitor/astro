#!/usr/bin/env python3
"""ai-gate — editor das regras do astro-gate (SQLite + UI web, só stdlib).

Uso:
  python3 app.py                # sobe a UI em http://127.0.0.1:8787
  python3 app.py --port 9000    # porta alternativa
  python3 app.py --generate     # inicializa o DB (seed) e gera o gate, sem UI

Fonte da verdade: ai-gate/rules.db. O gate (.claude/hooks/astro_gate.py) é um
artefato GERADO a partir das regras — edite aqui e clique em "Gerar gate".
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)  # ai-gate/ fica na raiz do projeto
DB_PATH = os.path.join(HERE, "rules.db")
TEMPLATE_PATH = os.path.join(HERE, "gate_template.py")
GATE_PATH = os.path.join(PROJECT_ROOT, ".claude", "hooks", "astro_gate.py")

# Barreiras padrão do astro:setup (regex). Semeiam o DB na primeira execução.
DEFAULT_RULES = [
    ("migrate_fresh_refresh_reset", r"migrate:(fresh|refresh|reset)",
     "recria/zera o banco (migrate:fresh/refresh/reset)"),
    ("db_wipe", r"db:wipe", "apaga todas as tabelas (db:wipe)"),
    ("queue_flush_clear", r"queue:(flush|clear)", "descarta jobs da fila (queue:flush/clear)"),
    ("rm_recursive", r"\brm\b[^\n;&|]*(\s-\w*r|\s--recursive)",
     "remoção recursiva de arquivos (rm -r/-rf/--recursive)"),
    ("git_push_force", r"git\s+push\b[^\n;&|]*(--force\b|--force-with-lease\b|\s-\w*f)",
     "reescrita forçada do remoto (git push --force/-f)"),
    ("composer_update", r"\bcomposer\s+update\b", "atualização fora do lockfile (composer update)"),
    ("npm_update", r"\bnpm\s+update\b", "atualização fora do lockfile (npm update)"),
    ("pnpm_update", r"\bpnpm\s+update\b", "atualização fora do lockfile (pnpm update)"),
    ("yarn_upgrade", r"\byarn\s+(upgrade|up)\b", "atualização fora do lockfile (yarn upgrade)"),
    ("truncate", r"\btruncate\b", "truncamento de tabela (TRUNCATE / ->truncate())"),
    ("force_delete", r"forceDelete\s*\(", "exclusão permanente (forceDelete())"),
    ("drop_db_table", r"\bdrop\s+(table|database|schema)\b", "DROP de tabela/banco/schema"),
]


# --------------------------------------------------------------------------- DB

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = connect()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS rules (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            slug        TEXT UNIQUE NOT NULL,
            pattern     TEXT NOT NULL,
            description TEXT NOT NULL,
            is_regex    INTEGER NOT NULL DEFAULT 1,
            enabled     INTEGER NOT NULL DEFAULT 1
        )"""
    )
    if conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO rules (slug, pattern, description, is_regex, enabled) "
            "VALUES (?,?,?,1,1)",
            DEFAULT_RULES,
        )
    conn.commit()
    conn.close()


def slugify(text: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "regra"
    conn = connect()
    slug, n = base, 2
    while conn.execute("SELECT 1 FROM rules WHERE slug=?", (slug,)).fetchone():
        slug, n = f"{base}_{n}", n + 1
    conn.close()
    return slug


# -------------------------------------------------------------------- generator

def effective_pattern(pattern: str, is_regex: int) -> str:
    return pattern if is_regex else re.escape(pattern)


def generate_gate() -> tuple[str, int]:
    """Lê as regras habilitadas e reescreve o gate standalone. Fail-closed."""
    with open(TEMPLATE_PATH, encoding="utf-8") as fh:
        template = fh.read()

    conn = connect()
    rows = conn.execute("SELECT * FROM rules WHERE enabled=1 ORDER BY id").fetchall()
    conn.close()

    rules = []
    for row in rows:
        pattern = effective_pattern(row["pattern"], row["is_regex"])
        re.compile(pattern)  # valida antes de gerar; erro sobe e aborta a geração
        rules.append({"slug": row["slug"], "pattern": pattern, "desc": row["description"]})

    literal = json.dumps(rules, ensure_ascii=False, indent=4)
    output = template.replace("__RULES__", literal)

    os.makedirs(os.path.dirname(GATE_PATH), exist_ok=True)
    with open(GATE_PATH, "w", encoding="utf-8") as fh:
        fh.write(output)
    os.chmod(GATE_PATH, 0o755)
    return GATE_PATH, len(rules)


# -------------------------------------------------------------------------- web

PAGE = """<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>astro-gate · regras</title>
<style>
  :root {
    color-scheme: light dark;
    --paper:#f4f4f2; --surface:#fff; --surface-2:#faf9f7;
    --ink:#18181b; --muted:#71717a; --line:#e5e4e0;
    --accent:#4738c8; --accent-ink:#fff; --accent-weak:#edebfb;
    --code-bg:#eeecfb; --code-ink:#352c86; --danger:#b42318; --radius:10px;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --paper:#131316; --surface:#1b1b20; --surface-2:#202026;
      --ink:#ededf2; --muted:#9a9aa5; --line:#2c2c34;
      --accent:#8b7dff; --accent-ink:#15121f; --accent-weak:#241f3a;
      --code-bg:#20203a; --code-ink:#b9b2ff; --danger:#f0776b;
    }
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--paper); color:var(--ink);
         font:15px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
  .wrap { max-width:860px; margin:0 auto; padding:2.5rem 1.25rem 4rem; }
  .mono,code { font-family:ui-monospace,"SF Mono","JetBrains Mono",Menlo,monospace; }
  .top { display:flex; align-items:flex-start; justify-content:space-between; gap:1.5rem; }
  .top h1 { margin:0 0 .35rem; font-size:1.5rem; letter-spacing:-.01em; }
  .top .sub { margin:0; color:var(--muted); font-size:.9rem; max-width:52ch; }
  .top .sub code { color:var(--ink); background:var(--code-bg); padding:.05em .35em; border-radius:5px; font-size:.85em; }
  .btn { font:inherit; font-weight:550; border:1px solid var(--line); background:var(--surface);
         color:var(--ink); padding:.5rem .95rem; border-radius:8px; cursor:pointer; white-space:nowrap; }
  .btn:hover { border-color:var(--ink); }
  .btn--primary { background:var(--accent); color:var(--accent-ink); border-color:var(--accent); }
  .btn--primary:hover { filter:brightness(1.08); border-color:var(--accent); }
  .btn--ghost { padding:.35rem .7rem; font-size:.85rem; color:var(--muted); background:none; border-color:transparent; }
  .btn--ghost:hover { color:var(--ink); border-color:var(--line); }
  .meta { display:flex; align-items:center; gap:.5rem; color:var(--muted); font-size:.82rem; margin:1.25rem 0; }
  .dot { width:7px; height:7px; border-radius:50%; background:var(--accent); display:inline-block; }
  .banner { padding:.6rem .85rem; border-radius:8px; margin:0 0 1.25rem; font-size:.88rem; border:1px solid; }
  .banner.ok { background:var(--accent-weak); border-color:var(--accent); color:var(--ink); }
  .banner.err { background:#b4231814; border-color:var(--danger); color:var(--danger); }
  .rules { display:flex; flex-direction:column; gap:.6rem; }
  .rule { display:grid; grid-template-columns:auto 1fr auto; gap:1rem; align-items:start;
          background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--accent);
          border-radius:var(--radius); padding:.9rem 1rem; }
  .rule.off { border-left-color:var(--line); opacity:.6; }
  .rule form { margin:0; }
  .rule__head { display:flex; align-items:center; gap:.5rem; margin-bottom:.5rem; }
  .rule__slug { font-size:.92rem; font-weight:600; }
  .badge { font-size:.68rem; color:var(--muted); border:1px solid var(--line); border-radius:999px; padding:.05rem .5rem; }
  .field { display:block; margin:.4rem 0; }
  .field__label { display:block; font-size:.72rem; color:var(--muted); margin-bottom:.2rem; }
  input[type=text] { width:100%; font:inherit; color:var(--ink); background:var(--surface-2);
                     border:1px solid var(--line); border-radius:7px; padding:.42rem .55rem; }
  input[type=text]:focus { outline:2px solid var(--accent); outline-offset:-1px; border-color:transparent; }
  input.code { font-family:ui-monospace,"SF Mono","JetBrains Mono",Menlo,monospace; font-size:.86rem;
               background:var(--code-bg); color:var(--code-ink); }
  .rule__foot { display:flex; align-items:center; gap:.9rem; margin-top:.55rem; }
  .checkline { display:inline-flex; align-items:center; gap:.4rem; font-size:.82rem; color:var(--muted); }
  .switch { position:relative; display:inline-block; width:38px; height:22px; }
  .switch input { opacity:0; width:0; height:0; }
  .switch .track { position:absolute; inset:0; background:var(--line); border-radius:999px; transition:.15s; cursor:pointer; }
  .switch .track::before { content:""; position:absolute; width:16px; height:16px; left:3px; top:3px;
                           background:#fff; border-radius:50%; transition:.15s; box-shadow:0 1px 2px rgba(0,0,0,.25); }
  .switch input:checked + .track { background:var(--accent); }
  .switch input:checked + .track::before { transform:translateX(16px); }
  .switch input:focus-visible + .track { outline:2px solid var(--accent); outline-offset:2px; }
  .icon-btn { border:none; background:none; color:var(--muted); cursor:pointer; font-size:.95rem;
              padding:.3rem .45rem; border-radius:6px; line-height:1; }
  .icon-btn:hover { color:var(--danger); background:#b4231814; }
  .add { margin-top:2rem; background:var(--surface-2); border:1px dashed var(--line); border-radius:var(--radius); padding:1.1rem 1.15rem; }
  .add h2 { margin:0 0 .75rem; font-size:1rem; }
  .add__foot { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-top:.75rem; flex-wrap:wrap; }
  .note { margin:1.75rem 0 0; color:var(--muted); font-size:.8rem; }
  @media (max-width:560px) {
    .top { flex-direction:column; }
    .rule { grid-template-columns:auto 1fr; }
    .rule__del { grid-column:1 / -1; justify-self:end; }
  }
</style></head><body>
<div class="wrap">
<header class="top">
  <div>
    <h1>Regras do gate</h1>
    <p class="sub">Comandos que o <code>astro-gate</code> bloqueia na execução. Edite abaixo e clique em Gerar gate: o SQLite é a fonte da verdade e o <code>__GATEREL__</code> é gerado a partir dele.</p>
  </div>
  <form method="post" action="/generate"><button class="btn btn--primary" type="submit">Gerar gate</button></form>
</header>
<p class="meta"><span class="dot"></span>__STAT__</p>
__BANNER__
<div class="rules">
__ROWS__
</div>
<section class="add">
  <h2>Nova regra</h2>
  <form method="post" action="/add">
    <div class="field"><span class="field__label">slug (opcional)</span><input type="text" name="slug" placeholder="gerado da descrição"></div>
    <div class="field"><span class="field__label">bloqueia o padrão</span><input class="code" type="text" name="pattern" required placeholder="ex.: chmod\\s+-R\\s+777"></div>
    <div class="field"><span class="field__label">por quê bloquear</span><input type="text" name="description" required placeholder="o motivo, em uma linha"></div>
    <div class="add__foot">
      <label class="checkline"><input type="checkbox" name="is_regex" checked> tratar como regex (desmarque = texto literal)</label>
      <button class="btn btn--primary" type="submit">Adicionar regra</button>
    </div>
  </form>
</section>
<p class="note">O script <code>__GATEREL__</code> é artefato gerado — não edite à mão. Ajuste as regras aqui e gere de novo.</p>
</div>
</body></html>"""


def render_rows(conn: sqlite3.Connection) -> str:
    parts = []
    for row in conn.execute("SELECT * FROM rules ORDER BY id").fetchall():
        checked = "checked" if row["enabled"] else ""
        regex_checked = "checked" if row["is_regex"] else ""
        off = "" if row["enabled"] else " off"
        rtype = "regex" if row["is_regex"] else "texto literal"
        parts.append(
            f"""<article class="rule{off}">
  <form class="rule__sw" method="post" action="/toggle">
    <input type="hidden" name="id" value="{row['id']}">
    <label class="switch"><input type="checkbox" onchange="this.form.submit()" {checked}><span class="track"></span></label>
  </form>
  <form class="rule__body" method="post" action="/save">
    <input type="hidden" name="id" value="{row['id']}">
    <div class="rule__head"><span class="rule__slug mono">{html.escape(row['slug'])}</span><span class="badge">{rtype}</span></div>
    <div class="field"><span class="field__label">bloqueia o padrão</span><input class="code" type="text" name="pattern" value="{html.escape(row['pattern'])}"></div>
    <div class="field"><span class="field__label">por quê</span><input type="text" name="description" value="{html.escape(row['description'])}"></div>
    <div class="rule__foot">
      <label class="checkline"><input type="checkbox" name="is_regex" {regex_checked}> regex</label>
      <button class="btn btn--ghost" type="submit">salvar</button>
    </div>
  </form>
  <form class="rule__del" method="post" action="/delete" onsubmit="return confirm('Remover esta regra?')">
    <input type="hidden" name="id" value="{row['id']}">
    <button class="icon-btn" title="remover regra" type="submit">&#10005;</button>
  </form>
</article>"""
        )
    return "\n".join(parts)


def render_page(msg: str = "", err: str = "") -> bytes:
    banner = ""
    if msg:
        banner = f'<div class="banner ok">{html.escape(msg)}</div>'
    elif err:
        banner = f'<div class="banner err">{html.escape(err)}</div>'
    conn = connect()
    total = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM rules WHERE enabled=1").fetchone()[0]
    rows = render_rows(conn)
    conn.close()
    gate_rel = os.path.relpath(GATE_PATH, PROJECT_ROOT)
    stat = f"{active} de {total} regras ativas"
    page = (
        PAGE.replace("__STAT__", html.escape(stat))
        .replace("__BANNER__", banner)
        .replace("__ROWS__", rows)
        .replace("__GATEREL__", html.escape(gate_rel))
    )
    return page.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):  # silencioso
        pass

    def _redirect(self, **params):
        query = ("?" + urlencode(params)) if params else ""
        self.send_response(303)
        self.send_header("Location", "/" + query)
        self.end_headers()

    def _form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        return {k: v[0] for k, v in parse_qs(body, keep_blank_values=True).items()}

    def do_GET(self):  # noqa: N802
        if urlparse(self.path).path != "/":
            self.send_error(404)
            return
        params = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
        page = render_page(params.get("msg", ""), params.get("err", ""))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self):  # noqa: N802
        path = urlparse(self.path).path
        form = self._form()
        try:
            if path == "/add":
                self._add(form)
            elif path == "/save":
                self._save(form)
            elif path == "/toggle":
                self._toggle(form)
            elif path == "/delete":
                self._delete(form)
            elif path == "/generate":
                gate, n = generate_gate()
                self._redirect(msg=f"Gate regenerado: {os.path.relpath(gate, PROJECT_ROOT)} ({n} regras ativas).")
                return
            else:
                self.send_error(404)
                return
        except (re.error, sqlite3.Error, ValueError) as exc:
            self._redirect(err=str(exc))
            return
        self._redirect(msg="Salvo. Clique em Gerar gate para aplicar ao script.")

    # ---- ações
    def _add(self, form):
        pattern = (form.get("pattern") or "").strip()
        description = (form.get("description") or "").strip()
        if not pattern or not description:
            raise ValueError("padrão e descrição são obrigatórios.")
        is_regex = 1 if form.get("is_regex") else 0
        if is_regex:
            re.compile(pattern)  # valida
        slug = (form.get("slug") or "").strip() or slugify(description)
        slug = re.sub(r"[^a-zA-Z0-9_]+", "_", slug).strip("_") or slugify(description)
        conn = connect()
        try:
            conn.execute(
                "INSERT INTO rules (slug, pattern, description, is_regex, enabled) "
                "VALUES (?,?,?,?,1)",
                (slug, pattern, description, is_regex),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"slug já existe: {slug}")
        finally:
            conn.close()

    def _save(self, form):
        rid = int(form["id"])
        pattern = (form.get("pattern") or "").strip()
        description = (form.get("description") or "").strip()
        if not pattern or not description:
            raise ValueError("padrão e descrição são obrigatórios.")
        is_regex = 1 if form.get("is_regex") else 0
        if is_regex:
            re.compile(pattern)  # valida
        conn = connect()
        conn.execute(
            "UPDATE rules SET pattern=?, description=?, is_regex=? WHERE id=?",
            (pattern, description, is_regex, rid),
        )
        conn.commit()
        conn.close()

    def _toggle(self, form):
        rid = int(form["id"])
        conn = connect()
        conn.execute("UPDATE rules SET enabled = 1 - enabled WHERE id=?", (rid,))
        conn.commit()
        conn.close()

    def _delete(self, form):
        rid = int(form["id"])
        conn = connect()
        conn.execute("DELETE FROM rules WHERE id=?", (rid,))
        conn.commit()
        conn.close()


def serve(port: int) -> None:
    init_db()
    httpd = HTTPServer(("127.0.0.1", port), Handler)
    print(f"ai-gate em http://127.0.0.1:{port}  (Ctrl+C para sair)")
    print(f"gate gerado em: {GATE_PATH}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\ntchau.")


def main() -> int:
    parser = argparse.ArgumentParser(description="ai-gate — editor das regras do astro-gate")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--generate", action="store_true",
                        help="inicializa o DB e gera o gate, sem abrir a UI")
    args = parser.parse_args()

    if args.generate:
        init_db()
        gate, n = generate_gate()
        print(f"DB: {DB_PATH}")
        print(f"gate gerado: {gate} ({n} regras ativas)")
        return 0

    serve(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
