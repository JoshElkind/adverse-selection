# Realized spread on one day of AAPL

Share-weighted effective and realized spreads for visible executions in the public LOBSTER level-1 sample, AAPL on 2012-06-21.

The book row on a line is the book after that message. The effective spread uses the mid from the previous line. A sell-limit execution is buyer-initiated. The future mid is the book after the last event at or before the trade time plus the horizon. Spreads are in basis points of the pre-trade mid. No fee is subtracted.

On this file the effective spread is 1.70 bps, about one penny on a stock near $585. The realized spread is 0.44 bps at 100 ms, 0.09 bps at 1 second, and -0.25 bps at 10 seconds. A maker who sold the touch to a buyer was, on average, behind the move after 10 seconds.

## Run

```bash
python3 -m unittest test_measure.py
python3 measure.py
```

`measure.py` downloads the sample zip from LOBSTER into `data/` and does not commit it.
