"""token-reserve: keeps a reserve of your Claude Code plan limit for emergencies.

Subcommands:
  statusline   reads the status line JSON (stdin), shows 5h/7d usage and writes the cache
  hook         UserPromptSubmit hook: injects a RESERVE MODE warning once usage crosses the limit
  setup        installs the status line and writes the config (--reserve N --urgent "a;b;c")
  remove       restores the previous status line
  status       shows the config and the last known usage
"""
import argparse, json, os, shutil, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")

CLAUDE_DIR = os.path.expanduser("~/.claude")
DATA = os.path.join(CLAUDE_DIR, "token-reserve")
CONFIG = os.path.join(DATA, "config.json")
CACHE = os.path.join(DATA, "usage.json")
SETTINGS = os.path.join(CLAUDE_DIR, "settings.json")

DEFAULTS = {
    "reserve": 20,
    "warning": 15,
    "urgent": ["production incidents", "systems down or unavailable"],
    "previous_statusline": None,
}
WINDOWS = {"five_hour": "5-hour window", "seven_day": "weekly limit"}


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def config():
    return {**DEFAULTS, **(read_json(CONFIG, {}) or {})}


def statusline():
    raw = sys.stdin.read()
    try:
        d = json.loads(raw)
    except Exception:
        d = {}
    cfg = config()
    limit = 100 - cfg["reserve"]

    def color(p):
        if p >= limit:
            return "\033[1;97;41m"
        if p >= limit - cfg["warning"]:
            return "\033[1;30;43m"
        return "\033[2m"

    rl = d.get("rate_limits") or {}
    usage, parts = {}, []
    for key, label in (("five_hour", "5h"), ("seven_day", "7d")):
        window = rl.get(key) or {}
        p = window.get("used_percentage")
        if isinstance(p, (int, float)):
            usage[key] = {"used": p, "resets_at": window.get("resets_at")}
            parts.append(f"{color(p)} {label} {p:.0f}% \033[0m")
    if usage:
        usage["updated"] = time.time()
        try:
            write_json(CACHE, usage)
        except Exception:
            pass

    base = ""
    if cfg.get("previous_statusline"):
        try:
            r = subprocess.run(cfg["previous_statusline"], shell=True, input=raw,
                               capture_output=True, text=True, encoding="utf-8", timeout=3)
            base = r.stdout.rstrip("\n")
        except Exception:
            base = ""
    if not base:
        base = (d.get("model") or {}).get("display_name", "")
    print("  ".join(x for x in (base, " ".join(parts)) if x))


def hook():
    usage = read_json(CACHE)
    if not usage:
        return
    cfg = config()
    limit = 100 - cfg["reserve"]
    now = time.time()
    over = []
    for key, name in WINDOWS.items():
        w = usage.get(key)
        if not isinstance(w, dict) or w.get("used", 0) < limit:
            continue
        reset = w.get("resets_at")
        if isinstance(reset, (int, float)) and now >= reset:
            continue  # window already reset
        if not reset and now - usage.get("updated", 0) > 5 * 3600:
            continue  # stale cache
        over.append(f"{name} at {w['used']:.0f}%")
    if over:
        print(
            f"[TOKEN RESERVE MODE] Plan usage: {', '.join(over)}. "
            f"The last {cfg['reserve']}% is reserved for: {'; '.join(cfg['urgent'])}. "
            "Follow the token-reserve skill: if the request is NOT one of these urgent cases, tell the "
            "user and ask for confirmation before proceeding; if it is urgent, work in economy mode."
        )


def setup(args):
    cfg = config()
    if args.reserve is not None:
        cfg["reserve"] = max(5, min(50, args.reserve))
    if args.urgent:
        cfg["urgent"] = [u.strip() for u in args.urgent.split(";") if u.strip()]

    os.makedirs(DATA, exist_ok=True)
    target = os.path.join(DATA, "token_reserve.py")
    shutil.copyfile(os.path.abspath(__file__), target)
    command = f'"{sys.executable}" "{target}" statusline'.replace("\\", "/")

    settings = read_json(SETTINGS, {}) or {}
    current = (settings.get("statusLine") or {}).get("command")
    if current and "token-reserve" not in current:
        cfg["previous_statusline"] = current
    if os.path.exists(SETTINGS):
        shutil.copyfile(SETTINGS, SETTINGS + ".bak-token-reserve")
    settings["statusLine"] = {"type": "command", "command": command}
    write_json(SETTINGS, settings)
    write_json(CONFIG, cfg)
    print(f"Reserve: {cfg['reserve']}% | urgent: {'; '.join(cfg['urgent'])}")
    print(f"Status line configured: {command}")
    if cfg.get("previous_statusline"):
        print(f"Previous status line kept (chained): {cfg['previous_statusline']}")
    print("Restart Claude Code to activate.")


def remove():
    cfg = config()
    settings = read_json(SETTINGS, {}) or {}
    if cfg.get("previous_statusline"):
        settings["statusLine"] = {"type": "command", "command": cfg["previous_statusline"]}
    else:
        settings.pop("statusLine", None)
    write_json(SETTINGS, settings)
    print("Status line restored. To remove the hook, uninstall the plugin: /plugin uninstall token-reserve")


def status():
    print(json.dumps({"config": config(), "usage": read_json(CACHE)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["statusline", "hook", "setup", "remove", "status"])
    ap.add_argument("--reserve", type=int)
    ap.add_argument("--urgent")
    a = ap.parse_args()
    {"statusline": statusline, "hook": hook, "setup": lambda: setup(a),
     "remove": remove, "status": status}[a.cmd]()
