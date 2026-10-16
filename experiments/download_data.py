"""
Download and freeze financial data for the real data validation protocol.

Downloads daily Close prices (NOT Adj Close) for the pre-specified indices,
saves CSVs, and computes SHA-256 hashes for reproducibility.

Usage:
    python experiments/download_data.py
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

# yfinance is imported inside download_all() to allow the rest
# of the module to be imported without it.


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Pre-specified indices (from protocol.md)
INDICES = {
    'SP500': '^GSPC',
    'FTSE': '^FTSE',
    'NIKKEI': '^N225',
    'DAX': '^GDAXI',
}

# Download range: need 300 trading days before earliest event (1987-10-19)
# so start from ~1986-01-01, end at latest available
START_DATE = '1984-01-01'
END_DATE = '2024-12-31'


def compute_file_hash(path):
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_all():
    """Download all indices and save as frozen CSVs."""
    import yfinance as yf

    os.makedirs(DATA_DIR, exist_ok=True)

    hashes = {}
    coverage = {}

    for name, ticker in INDICES.items():
        print(f"\nDownloading {name} ({ticker})...")

        df = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            progress=False,
            auto_adjust=False,
        )

        if len(df) == 0:
            print(f"  WARNING: No data for {ticker}")
            continue

        # Use Close (not Adj Close)
        # yfinance >= 0.2.31 returns MultiIndex columns for single ticker
        if hasattr(df.columns, 'levels'):
            # MultiIndex: ('Close', '^GSPC')
            close = df['Close']
            if hasattr(close, 'columns'):
                close = close.iloc[:, 0]
        else:
            close = df['Close']

        # Build clean DataFrame with Date, Close, LogPrice
        result = close.to_frame(name='Close')
        result['LogPrice'] = np.log(result['Close'])
        result.index.name = 'Date'

        # Drop NaN rows
        n_nan = result['Close'].isna().sum()
        if n_nan > 0:
            print(f"  Dropping {n_nan} NaN rows")
            result = result.dropna()

        # Save CSV
        csv_path = os.path.join(DATA_DIR, f'{name}_daily.csv')
        result.to_csv(csv_path)

        # Compute hash
        file_hash = compute_file_hash(csv_path)
        hashes[name] = file_hash

        # Coverage info
        first_date = str(result.index[0].date()) if hasattr(result.index[0], 'date') else str(result.index[0])[:10]
        last_date = str(result.index[-1].date()) if hasattr(result.index[-1], 'date') else str(result.index[-1])[:10]
        coverage[name] = {
            'ticker': ticker,
            'first_date': first_date,
            'last_date': last_date,
            'n_rows': len(result),
            'sha256': file_hash,
        }

        print(f"  Saved: {csv_path}")
        print(f"  Coverage: {first_date} to {last_date} ({len(result)} rows)")
        print(f"  SHA-256: {file_hash[:16]}...")

    # Save registry
    registry = {
        'downloaded_at': datetime.now(timezone.utc).isoformat(),
        'source': 'Yahoo Finance via yfinance',
        'price_type': 'Close (not Adj Close)',
        'note': 'Frozen after download. Do not re-download.',
        'indices': coverage,
    }
    registry_path = os.path.join(DATA_DIR, 'data_registry.json')
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"\nData registry saved: {registry_path}")
    print(f"\nCoverage summary:")
    for name, info in coverage.items():
        print(f"  {name:8s}: {info['first_date']} to {info['last_date']} "
              f"({info['n_rows']} rows)")

    # Check Black Monday coverage
    print(f"\nBlack Monday (1987-10-19) coverage check:")
    for name in ['SP500', 'FTSE', 'NIKKEI', 'DAX']:
        if name in coverage:
            first = coverage[name]['first_date']
            has_1987 = first <= '1987-07-01'
            status = 'OK' if has_1987 else 'EXCLUDED (data starts after 1987)'
            print(f"  {name:8s}: first={first} -> {status}")

    return coverage


if __name__ == '__main__':
    download_all()
