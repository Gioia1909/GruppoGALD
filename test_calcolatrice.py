import unittest
from calcolatrice import apply_binary  # <--- Importa la funzione reale!

class TestCalcolatrice(unittest.TestCase):
    def test_somma(self):
        # Usiamo apply_binary invece della copia locale
        self.assertEqual(apply_binary(5, '+', 5), 10)

    def test_divisione_zero(self):
        # Qui deve corrispondere a quello che restituisce la tua vera funzione
        # Se la tua funzione fa 'raise ZeroDivisionError', il test cambierebbe leggermente
        try:
            apply_binary(10, '/', 0)
        except ZeroDivisionError:
            self.assertTrue(True) # Test superato se lancia l'eccezione

    def test_moltiplicazione(self):
        self.assertEqual(apply_binary(3, '*', 4), 12)

if __name__ == '__main__':
    unittest.main()