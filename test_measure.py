import unittest
import zipfile
from pathlib import Path

from measure import Quote, load_zip, summarize


class MeasureTests(unittest.TestCase):
    def test_buyer_initiated_execution_uses_the_pre_trade_mid(self):
        root = Path(__file__).resolve().parent / "testdata"
        root.mkdir(exist_ok=True)
        path = root / "tiny.zip"
        # Sell limit execution (direction -1) is buyer-initiated.
        # Pre-trade book 100/102, so mid is 101. Trade at 102.
        # One second later the book is 103/105, mid 104.
        message = "\n".join(
            [
                "0.0,1,1,10,1000000,1",
                "1.0,4,2,10,1020000,-1",
                "1.5,1,3,10,1030000,1",
            ]
        )
        book = "\n".join(
            [
                "1020000,10,1000000,10",
                "1020000,5,1000000,10",
                "1050000,10,1030000,10",
            ]
        )
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                "AAPL_2012-06-21_34200000_57600000_message_1.csv", message
            )
            archive.writestr(
                "AAPL_2012-06-21_34200000_57600000_orderbook_1.csv", book
            )
        _times, executions, _quotes = load_zip(path)
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0].sign, 1)
        self.assertEqual(executions[0].pre, Quote(1000000, 1020000))
        stats = {row.seconds: row for row in summarize(path, (1.0,))}
        # effective = 2 * (102 - 101) / 101 * 10000
        self.assertAlmostEqual(stats[1.0].effective_bps, 2 * (102 - 101) / 101 * 10_000, places=4)
        # future mid is 104, realized = 2 * (102 - 104) / 101 * 10000
        self.assertAlmostEqual(stats[1.0].realized_bps, 2 * (102 - 104) / 101 * 10_000, places=4)

    def test_prices_are_in_lobster_units_in_the_fixture(self):
        # The fixture stores 101 dollars as 1_010_000. The assertion above uses
        # dollar prices only as a ratio, which matches the tick ratio.
        self.assertEqual(Quote(1000000, 1020000).mid, 1010000)


if __name__ == "__main__":
    unittest.main()
