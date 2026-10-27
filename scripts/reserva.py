"""reserva-tokens: mantém uma reserva do limite do plano do Claude Code para emergências.

Subcomandos:
  statusline   lê o JSON da status line (stdin), mostra o uso 5h/7d e grava o cache
  hook         hook UserPromptSubmit: injeta aviso de MODO RESERVA quando o uso passa do limite
  setup        instala a status line e grava a configuração (--reserva N --urgente "a;b;c")
  remover      restaura a status line anterior
  status       mostra configuração e último uso conhecido
"""
import argparse, json, os, shutil, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")

CLAUDE_DIR = os.path.expanduser("~/.claude")
DADOS = os.path.join(CLAUDE_DIR, "reserva-tokens")
CONFIG = os.path.join(DADOS, "config.json")
CACHE = os.path.join(DADOS, "uso.json")
SETTINGS = os.path.join(CLAUDE_DIR, "settings.json")

PADRAO = {
    "reserva": 20,
    "atencao": 15,
    "urgente": ["incidentes de produção", "sistemas parados ou fora do ar"],
    "statusline_anterior": None,
}
JANELAS = {"five_hour": "janela de 5h", "seven_day": "limite semanal"}


def ler_json(caminho, padrao=None):
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return padrao


def gravar_json(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def config():
    return {**PADRAO, **(ler_json(CONFIG, {}) or {})}


def statusline():
    bruto = sys.stdin.read()
    try:
        d = json.loads(bruto)
    except Exception:
        d = {}
    cfg = config()
    limite = 100 - cfg["reserva"]

    def cor(p):
        if p >= limite:
            return "\033[1;97;41m"
        if p >= limite - cfg["atencao"]:
            return "\033[1;30;43m"
        return "\033[2m"

    rl = d.get("rate_limits") or {}
    uso, partes = {}, []
    for chave, rotulo in (("five_hour", "5h"), ("seven_day", "7d")):
        janela = rl.get(chave) or {}
        p = janela.get("used_percentage")
        if isinstance(p, (int, float)):
            uso[chave] = {"used": p, "resets_at": janela.get("resets_at")}
            partes.append(f"{cor(p)} {rotulo} {p:.0f}% \033[0m")
    if uso:
        uso["updated"] = time.time()
        try:
            gravar_json(CACHE, uso)
        except Exception:
            pass

    base = ""
    if cfg.get("statusline_anterior"):
        try:
            r = subprocess.run(cfg["statusline_anterior"], shell=True, input=bruto,
                               capture_output=True, text=True, encoding="utf-8", timeout=3)
            base = r.stdout.rstrip("\n")
        except Exception:
            base = ""
    if not base:
        base = (d.get("model") or {}).get("display_name", "")
    print("  ".join(x for x in (base, " ".join(partes)) if x))


def hook():
    uso = ler_json(CACHE)
    if not uso:
        return
    cfg = config()
    limite = 100 - cfg["reserva"]
    agora = time.time()
    estourados = []
    for chave, nome in JANELAS.items():
        j = uso.get(chave)
        if not isinstance(j, dict) or j.get("used", 0) < limite:
            continue
        reset = j.get("resets_at")
        if isinstance(reset, (int, float)) and agora >= reset:
            continue  # janela já resetou
        if not reset and agora - uso.get("updated", 0) > 5 * 3600:
            continue  # cache velho
        estourados.append(f"{nome} em {j['used']:.0f}%")
    if estourados:
        print(
            f"[MODO RESERVA DE TOKENS] Uso do plano: {', '.join(estourados)}. "
            f"Os últimos {cfg['reserva']}% são reservados para: {'; '.join(cfg['urgente'])}. "
            "Siga a skill reserva-tokens: se o pedido NÃO for um desses casos urgentes, avise o "
            "usuário e peça confirmação antes de executar; se for urgente, trabalhe no modo econômico."
        )


def setup(args):
    cfg = config()
    if args.reserva is not None:
        cfg["reserva"] = max(5, min(50, args.reserva))
    if args.urgente:
        cfg["urgente"] = [u.strip() for u in args.urgente.split(";") if u.strip()]

    os.makedirs(DADOS, exist_ok=True)
    destino = os.path.join(DADOS, "reserva.py")
    shutil.copyfile(os.path.abspath(__file__), destino)
    comando = f'"{sys.executable}" "{destino}" statusline'.replace("\\", "/")

    settings = ler_json(SETTINGS, {}) or {}
    atual = (settings.get("statusLine") or {}).get("command")
    if atual and "reserva-tokens" not in atual:
        cfg["statusline_anterior"] = atual
    if os.path.exists(SETTINGS):
        shutil.copyfile(SETTINGS, SETTINGS + ".bak-reserva-tokens")
    settings["statusLine"] = {"type": "command", "command": comando}
    gravar_json(SETTINGS, settings)
    gravar_json(CONFIG, cfg)
    print(f"Reserva: {cfg['reserva']}% | urgente: {'; '.join(cfg['urgente'])}")
    print(f"Status line configurada: {comando}")
    if cfg.get("statusline_anterior"):
        print(f"Status line anterior mantida (encadeada): {cfg['statusline_anterior']}")
    print("Reinicie o Claude Code para ativar.")


def remover():
    cfg = config()
    settings = ler_json(SETTINGS, {}) or {}
    if cfg.get("statusline_anterior"):
        settings["statusLine"] = {"type": "command", "command": cfg["statusline_anterior"]}
    else:
        settings.pop("statusLine", None)
    gravar_json(SETTINGS, settings)
    print("Status line restaurada. Para remover o hook, desinstale o plugin: /plugin uninstall reserva-tokens")


def status():
    print(json.dumps({"config": config(), "uso": ler_json(CACHE)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["statusline", "hook", "setup", "remover", "status"])
    ap.add_argument("--reserva", type=int)
    ap.add_argument("--urgente")
    a = ap.parse_args()
    {"statusline": statusline, "hook": hook, "setup": lambda: setup(a),
     "remover": remover, "status": status}[a.cmd]()
