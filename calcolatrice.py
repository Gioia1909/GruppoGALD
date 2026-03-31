import math
import json
import os
from collections import deque

# ─── Costanti ─────────────────────────────────────────────────────────────────
MEMORY_FILE = "memory.json"
MEMORY_MAX  = 10

# ─── Stato globale ────────────────────────────────────────────────────────────
ans: float = 0.0
angle_mode: str = "deg"   # "deg" | "rad"

# US8: coda scorrevole — ogni entry è {"expr": str, "result": float}
history: deque = deque(maxlen=MEMORY_MAX)

UNARY_FUNCS = {"sqrt", "sin", "cos", "tan", "asin", "acos", "atan"}

# ─── Persistenza JSON ─────────────────────────────────────────────────────────
def load_history() -> None:
    """Carica la coda dal file JSON (se esiste)."""
    global history
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
            entries = data.get("history", [])[-MEMORY_MAX:]
            history = deque(entries, maxlen=MEMORY_MAX)
        except (json.JSONDecodeError, KeyError):
            history = deque(maxlen=MEMORY_MAX)

def save_history() -> None:
    """Salva la coda corrente sul file JSON."""
    with open(MEMORY_FILE, "w") as f:
        json.dump({"history": list(history)}, f, indent=2)

def push_history(expr: str, result: float) -> None:
    """Aggiunge un'operazione alla coda (scalando se piena) e salva."""
    history.append({"expr": expr, "result": result})
    save_history()

# ─── Utilità angoli ───────────────────────────────────────────────────────────
def to_rad(x: float) -> float:
    return math.radians(x) if angle_mode == "deg" else x

def from_rad(x: float) -> float:
    return math.degrees(x) if angle_mode == "deg" else x

# ─── Sostituzione ANS nei token ───────────────────────────────────────────────
def resolve(tokens: list) -> list:
    """US3: sostituisce 'ans' con l'ultimo risultato."""
    return [str(ans) if t == "ans" else t for t in tokens]

# ─── Operazioni ───────────────────────────────────────────────────────────────
def apply_binary(a: float, op: str, b: float) -> float:
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/":
        if b == 0: raise ZeroDivisionError("Errore: divisione per zero.")
        return a / b
    if op == "^": return a ** b
    raise ValueError(f"Operatore '{op}' non supportato.")

def apply_unary(name: str, arg: float) -> float:
    if name == "sqrt":
        if arg < 0: raise ValueError("Errore: radice di numero negativo.")
        return math.sqrt(arg)
    trig_map = {
        "sin":  lambda x: math.sin(to_rad(x)),
        "cos":  lambda x: math.cos(to_rad(x)),
        "tan":  lambda x: math.tan(to_rad(x)),
        "asin": lambda x: from_rad(math.asin(x)),
        "acos": lambda x: from_rad(math.acos(x)),
        "atan": lambda x: from_rad(math.atan(x)),
    }
    if name in trig_map:
        return trig_map[name](arg)
    raise ValueError(f"Funzione '{name}' non riconosciuta.")

# ─── Guida ────────────────────────────────────────────────────────────────────
def show_help():
    mode_label = "GRADI" if angle_mode == "deg" else "RADIANTI"
    print(f"""
╔══════════════════════════════════════════════════════╗
║          GUIDA CALCOLATRICE GALD  v2.0               ║
╠══════════════════════════════════════════════════════╣
║  OPERAZIONI BASE                                     ║
║    5 + 3  |  5 - 2  |  5 * 4  |  10 / 2  |  2 ^ 8  ║
║                                                      ║
║  FUNZIONI  (nome + spazio + numero)                  ║
║    sqrt 25                   radice quadrata         ║
║    sin 90 | cos 0 | tan 45   (modo: {mode_label:<13})║
║    asin 1 | acos 0 | atan 1  (risultato in {mode_label:<9})║
║                                                      ║
║  ANS  (ultimo risultato calcolato)                   ║
║    ans + 5   |   3 * ans   |   sqrt ans              ║
║                                                      ║
║  MEMORIA  (coda scorrevole, max {MEMORY_MAX} operazioni)       ║
║    Ogni calcolo viene salvato automaticamente        ║
║    su '{MEMORY_FILE}'. Quando si raggiunge il limite  ║
║    di {MEMORY_MAX}, l'operazione piu' vecchia viene rimossa.  ║
║                                                      ║
║    mem list       mostra le ultime {MEMORY_MAX} operazioni    ║
║    mem load <n>   carica il risultato n in ANS       ║
║                   (1 = piu' recente, {MEMORY_MAX} = piu' vecchio)  ║
║    mem clear      svuota la coda e il file JSON      ║
║                                                      ║
║  MODALITA' ANGOLI                                    ║
║    mode deg   /   mode rad                           ║
║                                                      ║
║  COMANDI                                             ║
║    reset   azzera ANS (la memoria storica resta)     ║
║    help    mostra questa guida                       ║
║    exit    esci                                      ║
╚══════════════════════════════════════════════════════╝
""")

# ─── Stampa della coda ────────────────────────────────────────────────────────
def print_history():
    if not history:
        print("  (memoria vuota)")
        return
    print(f"  Ultime {len(history)} operazioni salvate (1 = piu' recente):")
    for i, entry in enumerate(reversed(history), start=1):
        print(f"  [{i:2}]  {entry['expr']:<28} =  {entry['result']}")

# ─── Loop principale ──────────────────────────────────────────────────────────
def main():
    global ans, angle_mode

    load_history()   # ripristina la coda dal file all'avvio
    show_help()

    while True:
        try:
            raw = input(">>> ").strip().lower()
            if not raw:
                continue

            if raw == "exit":
                print("Sprint 2 completato. Arrivederci!")
                break

            if raw == "help":
                show_help()
                continue

            # US4: Reset ANS
            if raw == "reset":
                ans = 0.0
                print("OK Reset: ANS = 0  (la memoria storica e' intatta).")
                continue

            # US5: Modalita' angoli
            if raw.startswith("mode "):
                parts = raw.split()
                mode_arg = parts[1] if len(parts) > 1 else ""
                if mode_arg in ("deg", "rad"):
                    angle_mode = mode_arg
                    print(f"OK Modalita' angoli: {'GRADI' if angle_mode == 'deg' else 'RADIANTI'}")
                else:
                    print("ATTENZIONE: Usa: mode deg   oppure   mode rad")
                continue

            tokens_raw = raw.split()

            # US8: Comandi memoria
            if tokens_raw[0] == "mem":
                sub = tokens_raw[1] if len(tokens_raw) > 1 else ""

                if sub == "list":
                    print_history()

                elif sub == "load":
                    if len(tokens_raw) < 3:
                        print("ATTENZIONE: Uso: mem load <n>  (1 = piu' recente)")
                        continue
                    try:
                        idx = int(tokens_raw[2])
                    except ValueError:
                        print("ATTENZIONE: <n> deve essere un numero intero.")
                        continue
                    if not (1 <= idx <= len(history)):
                        print(f"ATTENZIONE: Indice non valido. Scegli tra 1 e {len(history)}.")
                    else:
                        entry = list(reversed(history))[idx - 1]
                        ans = entry["result"]
                        print(f"OK Caricato [{idx}]: {entry['expr']} = {ans}  -> ANS aggiornato")

                elif sub == "clear":
                    history.clear()
                    save_history()
                    print("OK Memoria svuotata (file JSON azzerato).")

                else:
                    print("ATTENZIONE: Uso: mem list | mem load <n> | mem clear")
                continue

            # US3: Risolvi ANS
            tokens = resolve(tokens_raw)

            # Funzioni unarie
            if tokens[0] in UNARY_FUNCS and len(tokens) == 2:
                expr_str = " ".join(tokens_raw)
                arg = float(tokens[1])
                ans = apply_unary(tokens[0], arg)
                print(f"  = {ans}")
                push_history(expr_str, ans)

            # Operazione binaria
            elif len(tokens) == 3:
                expr_str = " ".join(tokens_raw)
                n1 = float(tokens[0])
                op = tokens[1]
                n2 = float(tokens[2])
                ans = apply_binary(n1, op, n2)
                print(f"  = {ans}")
                push_history(expr_str, ans)

            else:
                print("ATTENZIONE: Formato non valido. Digita 'help' per la guida.")

        except (ValueError, ZeroDivisionError) as e:
            print(f"ATTENZIONE: {e}")
        except Exception as e:
            print(f"ATTENZIONE: Errore imprevisto: {e}")


if __name__ == "__main__":
    main()