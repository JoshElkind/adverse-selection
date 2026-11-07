from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve

SAMPLE_URL = (
    "https://php.lobsterdata.com/info/sample/"
    "LOBSTER_SampleFile_AAPL_2012-06-21_1.zip"
)
MESSAGE_NAME = "AAPL_2012-06-21_34200000_57600000_message_1.csv"
BOOK_NAME = "AAPL_2012-06-21_34200000_57600000_orderbook_1.csv"


@dataclass(frozen=True)
class Quote:
    bid: int
    ask: int

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2


@dataclass(frozen=True)
class Execution:
    time: float
    price: int
    size: int
    # +1 buyer-initiated, -1 seller-initiated
    sign: int
    pre: Quote


def download_sample(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        urlretrieve(SAMPLE_URL, dest)
    return dest


def load_zip(path: Path) -> tuple[list[float], list[Execution], list[Quote]]:
    with zipfile.ZipFile(path) as archive:
        messages = archive.read(MESSAGE_NAME).decode().splitlines()
        books = archive.read(BOOK_NAME).decode().splitlines()

    times: list[float] = []
    quotes: list[Quote] = []
    executions: list[Execution] = []
    for index, (message_line, book_line) in enumerate(zip(messages, books)):
        time_s, event_type, _order_id, size_s, price_s, direction_s = message_line.split(",")
        ask_s, _ask_size, bid_s, _bid_size = book_line.split(",")
        time = float(time_s)
        quote = Quote(int(bid_s), int(ask_s))
        times.append(time)
        quotes.append(quote)
        if event_type != "4" or index == 0:
            continue
        pre = quotes[index - 1]
        direction = int(direction_s)
        executions.append(
            Execution(
                time=time,
                price=int(price_s),
                size=int(size_s),
                sign=-direction,
                pre=pre,
            )
        )
    return times, executions, quotes


def main() -> None:
    sample = download_sample(Path(__file__).resolve().parent / "data" / "AAPL_2012-06-21_1.zip")
    _times, executions, quotes = load_zip(sample)
    print(f"{len(quotes)} events, {len(executions)} executions")


if __name__ == "__main__":
    main()
