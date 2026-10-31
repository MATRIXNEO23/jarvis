"""Read-only network widget tests; no real subprocess is executed."""
import unittest
from unittest.mock import patch
from network_telemetry import parse_interface_bytes, friendly_rate, NetworkTelemetry


class NetworkHUDTests(unittest.TestCase):
    def test_international_windows_interface_counters(self):
        examples = [
            "Interface Statistics\n                 Received   Sent\n"
            "Bytes             1234500     540000\n",
            "Statistiche interfaccia\n                 Ricevuti Inviati\n"
            "Byte              1.234.500 540.000\n",
            "Estadisticas\n                 Recibidos Enviados\n"
            "Octetos 1,234,500 540,000\n",
        ]
        for text in examples:
            self.assertEqual(parse_interface_bytes(text),(1234500,540000))
        self.assertIsNone(parse_interface_bytes("nessuna misura"))
        self.assertIsNone(parse_interface_bytes("Errore 1 2 3"))

    def test_throughput_units_are_real_bytes_per_second(self):
        self.assertEqual(friendly_rate(None),"--")
        self.assertEqual(friendly_rate(0),"0B/s")
        self.assertEqual(friendly_rate(1024),"1.0KB/s")
        self.assertEqual(friendly_rate(1024**2),"1.0MB/s")

    def test_counter_deltas_and_reset(self):
        meter=NetworkTelemetry()
        meter._queue.put((10.0,(1000,2500)))
        self.assertIsNone(meter.result())
        meter._queue.put((12.0,(5096,4548)))
        self.assertEqual(meter.result(),(2048.,1024.))
        # A reset must not make negative fake network speed.
        meter._queue.put((14.0,(1,2)))
        self.assertEqual(meter.result(),(0.,0.))


if __name__=="__main__":
    unittest.main()
