from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

SAMPLE_URL = (
    "https://php.lobsterdata.com/info/sample/"
    "LOBSTER_SampleFile_AAPL_2012-06-21_1.zip"
)


def download_sample(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        urlretrieve(SAMPLE_URL, dest)
    return dest


def main() -> None:
    sample = download_sample(Path(__file__).resolve().parent / "data" / "AAPL_2012-06-21_1.zip")
    print(sample)


if __name__ == "__main__":
    main()
