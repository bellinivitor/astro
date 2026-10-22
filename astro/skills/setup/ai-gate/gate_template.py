#!/usr/bin/env python3
"""astro-gate — barreira de execução.

GERADO por ai-gate/app.py a partir de ai-gate/rules.db. **Não edite à mão** —
edite as regras no app (`python3 ai-gate/app.py`) e clique em "Gerar gate".

Fail-closed: na dúvida, ou em regra inválida, bloqueia. Dois modos, detectados
automaticamente:

1. Hook PreToolUse do Claude Code — recebe o JSON do evento no stdin, inspeciona
   `tool_input.command` e bloqueia com exit 2 (razão no stderr).
2. CLI / wrapper — comando por argumento ou stdin; libera com exit 0, barra com
   exit 2:  python3 astro_gate.py "$CMD" && eval "$CMD"
"""
from __future__ import annotations

import json
import re
import sys

# Regras embutidas (geradas a partir de ai-gate/rules.db).
RULES = __RULES__

BLOCK_EXIT = 2  # exit 2 barra tanto no hook (PreToolUse) quanto no `&&` do shell.


def compiled_rules() -> list[tuple[re.Pattern[str], str]]:
    out: list[tuple[re.Pattern[str], str]] = []
    for rule in RULES:
        try:
            out.append((re.compile(rule["pattern"], re.IGNORECASE), rule["desc"]))
        except re.error as exc:
            # Fail-closed: uma regra inválida bloqueia tudo até ser corrigida no app.
            print(f"🚫 astro-gate: regra inválida {rule.get('slug')!r}: {exc}", file=sys.stderr)
            sys.exit(BLOCK_EXIT)
    return out


def first_violation(text: str, rules: list[tuple[re.Pattern[str], str]]):
    for regex, desc in rules:
        match = regex.search(text)
        if match:
            return desc, match.group(0).strip()
    return None


def read_input() -> str:
    """Comando a inspecionar: argv (CLI) > JSON de hook (tool_input.command) > stdin."""
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])

    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return ""

    if raw.lstrip()[:1] in "{[":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return raw
        if isinstance(data, dict) and ("tool_input" in data or "tool_name" in data
                                       or "hook_event_name" in data):
            tool_input = data.get("tool_input") or {}
            command = tool_input.get("command") if isinstance(tool_input, dict) else None
            return command if isinstance(command, str) else ""
    return raw


def main() -> int:
    rules = compiled_rules()
    text = read_input()
    if not text.strip():
        return 0

    violation = first_violation(text, rules)
    if violation is None:
        return 0

    desc, matched = violation
    print(
        "🚫 astro-gate: execução bloqueada — comando contém padrão proibido: "
        f"{desc} (casou: {matched!r}). Barreira do astro:setup; se for intencional, "
        "rode manualmente fora do gate.",
        file=sys.stderr,
    )
    return BLOCK_EXIT


if __name__ == "__main__":
    sys.exit(main())
