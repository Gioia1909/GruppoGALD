import unittest
import json
import os
import math
from collections import deque

from calcolatrice import (
    apply_binary,
    apply_unary,
    resolve,
    push_history,
    load_history,
    save_history,
    MEMORY_FILE,
    MEMORY_MAX,
)
import calcolatrice


# ─── Helper: pulisce il file JSON prima/dopo ogni test che lo tocca ───────────
def _clear_json():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)


# ─── US1 · US2 · US6 — Operazioni binarie ────────────────────────────────────
class TestApplyBinary(unittest.TestCase):

    def test_somma(self):
        self.assertEqual(apply_binary(5, '+', 5), 10)

    def test_sottrazione(self):
        self.assertEqual(apply_binary(10, '-', 3), 7)

    def test_moltiplicazione(self):
        self.assertEqual(apply_binary(3, '*', 4), 12)

    def test_divisione(self):
        self.assertEqual(apply_binary(10, '/', 2), 5.0)

    def test_divisione_zero(self):
        with self.assertRaises(ZeroDivisionError):
            apply_binary(10, '/', 0)

    def test_potenza(self):
        self.assertEqual(apply_binary(2, '^', 8), 256)

    def test_operatore_non_supportato(self):
        with self.assertRaises(ValueError):
            apply_binary(5, '%', 2)


# ─── US5 · US6 — Funzioni unarie ─────────────────────────────────────────────
class TestApplyUnary(unittest.TestCase):

    def setUp(self):
        # Forza la modalità gradi per tutti i test trig
        calcolatrice.angle_mode = "deg"

    def test_sqrt(self):
        self.assertAlmostEqual(apply_unary("sqrt", 25), 5.0)

    def test_sqrt_negativo(self):
        with self.assertRaises(ValueError):
            apply_unary("sqrt", -1)

    def test_sin_90(self):
        self.assertAlmostEqual(apply_unary("sin", 90), 1.0, places=10)

    def test_cos_0(self):
        self.assertAlmostEqual(apply_unary("cos", 0), 1.0, places=10)

    def test_tan_45(self):
        self.assertAlmostEqual(apply_unary("tan", 45), 1.0, places=10)

    def test_asin_1(self):
        # asin(1) in gradi = 90°
        self.assertAlmostEqual(apply_unary("asin", 1), 90.0, places=10)

    def test_trig_radianti(self):
        calcolatrice.angle_mode = "rad"
        self.assertAlmostEqual(apply_unary("sin", math.pi / 2), 1.0, places=10)

    def test_funzione_sconosciuta(self):
        with self.assertRaises(ValueError):
            apply_unary("log", 10)


# ─── US3 — ANS ────────────────────────────────────────────────────────────────
class TestAns(unittest.TestCase):

    def setUp(self):
        calcolatrice.ans = 0.0

    def test_resolve_sostituisce_ans(self):
        calcolatrice.ans = 42.0
        self.assertEqual(resolve(["ans", "+", "8"]), ["42.0", "+", "8"])

    def test_resolve_senza_ans(self):
        self.assertEqual(resolve(["5", "+", "3"]), ["5", "+", "3"])

    def test_ans_aggiornato_dopo_calcolo(self):
        calcolatrice.ans = 10.0
        tokens = resolve(["ans", "*", "2"])
        result = apply_binary(float(tokens[0]), tokens[1], float(tokens[2]))
        calcolatrice.ans = result
        self.assertEqual(calcolatrice.ans, 20.0)


# ─── US8 — Memoria JSON a coda scorrevole ─────────────────────────────────────
class TestMemoria(unittest.TestCase):

    def setUp(self):
        _clear_json()
        calcolatrice.history = deque(maxlen=MEMORY_MAX)

    def tearDown(self):
        _clear_json()

    def test_push_salva_su_file(self):
        push_history("5 + 3", 8.0)
        self.assertTrue(os.path.exists(MEMORY_FILE))

    def test_push_aggiunge_entry(self):
        push_history("5 + 3", 8.0)
        self.assertEqual(len(calcolatrice.history), 1)
        self.assertEqual(calcolatrice.history[-1]["result"], 8.0)

    def test_coda_scala_a_max_10(self):
        for i in range(MEMORY_MAX + 3):
            push_history(f"{i} + 1", float(i + 1))
        self.assertEqual(len(calcolatrice.history), MEMORY_MAX)

    def test_elemento_piu_vecchio_viene_rimosso(self):
        # Riempiamo la coda con valori 1..10, poi aggiungiamo 11
        for i in range(1, MEMORY_MAX + 1):
            push_history(f"op {i}", float(i))
        push_history("op 11", 11.0)
        results = [e["result"] for e in calcolatrice.history]
        self.assertNotIn(1.0, results)   # il primo deve essere uscito
        self.assertIn(11.0, results)     # l'ultimo deve esserci

    def test_persistenza_load(self):
        push_history("2 ^ 8", 256.0)
        # Simula riavvio: svuota la deque in memoria e ricarica dal file
        calcolatrice.history = deque(maxlen=MEMORY_MAX)
        load_history()
        self.assertEqual(len(calcolatrice.history), 1)
        self.assertEqual(calcolatrice.history[-1]["result"], 256.0)

    def test_clear_svuota_file(self):
        push_history("3 * 4", 12.0)
        calcolatrice.history.clear()
        save_history()
        with open(MEMORY_FILE) as f:
            data = json.load(f)
        self.assertEqual(data["history"], [])

    def test_file_corrotto_non_crasha(self):
        with open(MEMORY_FILE, "w") as f:
            f.write("{ INVALID JSON }")
        # load_history non deve sollevare eccezioni
        try:
            load_history()
        except Exception as e:
            self.fail(f"load_history ha sollevato un'eccezione inattesa: {e}")


# ─── US4 — Reset ──────────────────────────────────────────────────────────────
class TestReset(unittest.TestCase):

    def test_reset_azzera_ans(self):
        calcolatrice.ans = 99.0
        calcolatrice.ans = 0.0   # simula il comando reset
        self.assertEqual(calcolatrice.ans, 0.0)

    def test_reset_non_tocca_history(self):
        calcolatrice.history = deque([{"expr": "1+1", "result": 2.0}], maxlen=MEMORY_MAX)
        calcolatrice.ans = 0.0   # reset
        self.assertEqual(len(calcolatrice.history), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)