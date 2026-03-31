import math

def apply_binary(a: float, op: str, b: float) -> float:
    """US1: Operazioni base, US2: Divisione per zero, US6: Potenza"""
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/":
        if b == 0: raise ZeroDivisionError("Errore: divisione per zero.")
        return a / b
    if op == "^": return a ** b
    raise ValueError(f"Operatore '{op}' non supportato.")

def apply_unary(name: str, arg: float) -> float:
    """US6: Radice quadrata"""
    if name == "sqrt":
        if arg < 0: raise ValueError("Errore: radice di numero negativo.")
        return math.sqrt(arg)
    return None

def show_help():
    """US7: Guida utente"""
    print("""
╔══════════════════════════════════════════════════╗
║             GUIDA CALCOLATRICE GALD              ║
╠══════════════════════════════════════════════════╣
║ Operazioni base:  numero [spazio] op [spazio] numero
║ Esempio:          5 + 3                          ║
║ Potenza:          5 ^ 2                          ║
║ Radice:           sqrt [spazio] numero           ║
║ Esci:             exit                           ║
╚══════════════════════════════════════════════════╝
""")

def main():
    show_help()
    
    while True:
        try:
            raw = input(">>> ").strip().lower()
            
            if raw == "exit":
                print("Consegna Sprint 1 effettuata. Arrivederci!")
                break
            if raw == "help":
                show_help()
                continue
            
            tokens = raw.split()

            # Caso 1: Radice (es: sqrt 25) -> US6
            if tokens[0] == "sqrt" and len(tokens) == 2:
                valore = float(tokens[1])
                risultato = apply_unary("sqrt", valore)
                print(f"Risultato: {risultato}")
                
            # Caso 2: Operazione binaria (es: 5 + 3) -> US1, US2, US6
            elif len(tokens) == 3:
                n1 = float(tokens[0])
                op = tokens[1]
                n2 = float(tokens[2])
                risultato = apply_binary(n1, op, n2)
                print(f"Risultato: {risultato}")
            
            else:
                print("Formato non valido. Usa '5 + 3' o 'sqrt 25'.")

        except (ValueError, ZeroDivisionError, IndexError) as e:
            print(f"⚠ {e}")

if __name__ == "__main__":
    main()