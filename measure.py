from __future__ import annotations

import bisect
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
HORIZONS = (1.0, 10.0)


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


@dataclass(frozen=True)
class HorizonStats:
    seconds: float
    trades: int
    shares: int
    effective_bps: float
    realized_bps: float
    impact_bps: float


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
        if pre.bid <= 0 or pre.ask <= pre.bid:
            continue
        direction = int(direction_s)
        if direction not in (-1, 1):
            continue
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


def summarize(path: Path, horizons: tuple[float, ...] = HORIZONS) -> list[HorizonStats]:
    times, executions, quotes = load_zip(path)
    stats: list[HorizonStats] = []
    for horizon in horizons:
        eff_num = real_num = impact_num = 0.0
        shares = 0
        trades = 0
        for execution in executions:
            future_at = execution.time + horizon
            index = bisect.bisect_right(times, future_at) - 1
            if index < 0 or index >= len(quotes):
                continue
            future = quotes[index]
            if future.bid <= 0 or future.ask <= future.bid:
                continue
            mid = execution.pre.mid
            weight = execution.size
            effective = 10_000 * 2 * execution.sign * (execution.price - mid) / mid
            realized = 10_000 * 2 * execution.sign * (execution.price - future.mid) / mid
            eff_num += weight * effective
            real_num += weight * realized
            impact_num += weight * (effective - realized)
            shares += weight
            trades += 1
        if shares == 0:
            raise ValueError(f"no executions usable at horizon {horizon}")
        stats.append(
            HorizonStats(
                seconds=horizon,
                trades=trades,
                shares=shares,
                effective_bps=eff_num / shares,
                realized_bps=real_num / shares,
                impact_bps=impact_num / shares,
            )
        )
    return stats


def format_stats(stats: list[HorizonStats]) -> str:
    lines = []
    for row in stats:
        lines.append(
            f"{row.seconds:>5.1f}s trades={row.trades} shares={row.shares} "
            f"effective_bps={row.effective_bps:.2f} "
            f"realized_bps={row.realized_bps:.2f} "
            f"impact_bps={row.impact_bps:.2f}"
        )
    return "\n".join(lines)


def main() -> None:
    sample = download_sample(Path(__file__).resolve().parent / "data" / "AAPL_2012-06-21_1.zip")
    print(format_stats(summarize(sample)))


if __name__ == "__main__":
    main()
