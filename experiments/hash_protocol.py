"""
Hash and register the pre-specified protocol.

Usage:
    python experiments/hash_protocol.py              # compute and register hash
    python experiments/hash_protocol.py --verify     # verify existing hash
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone


PROTOCOL_PATH = os.path.join(os.path.dirname(__file__), 'protocol.md')
HASH_REGISTRY = os.path.join(os.path.dirname(__file__), 'protocol_hash.json')


def compute_hash(path):
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def register_hash():
    """Compute and register the protocol hash with timestamp."""
    if not os.path.exists(PROTOCOL_PATH):
        print("ERROR: protocol.md not found.")
        sys.exit(1)

    file_hash = compute_hash(PROTOCOL_PATH)
    timestamp = datetime.now(timezone.utc).isoformat()

    registry = {
        'protocol_file': 'experiments/protocol.md',
        'sha256': file_hash,
        'registered_at': timestamp,
        'note': (
            'This hash was computed BEFORE downloading any financial data. '
            'Any modification to protocol.md after this timestamp '
            'constitutes a protocol violation.'
        ),
    }

    with open(HASH_REGISTRY, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"Protocol hash registered:")
    print(f"  SHA-256:    {file_hash}")
    print(f"  Timestamp:  {timestamp}")
    print(f"  Registry:   {HASH_REGISTRY}")

    return file_hash


def verify_hash():
    """Verify that protocol.md matches the registered hash."""
    if not os.path.exists(HASH_REGISTRY):
        print("ERROR: protocol_hash.json not found. Run without --verify first.")
        sys.exit(1)

    with open(HASH_REGISTRY) as f:
        registry = json.load(f)

    expected = registry['sha256']
    actual = compute_hash(PROTOCOL_PATH)

    if actual == expected:
        print(f"PASS: protocol.md matches registered hash.")
        print(f"  Hash:       {actual}")
        print(f"  Registered: {registry['registered_at']}")
        return True
    else:
        print(f"FAIL: protocol.md has been modified!")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Hash and verify the pre-specified protocol.'
    )
    parser.add_argument('--verify', action='store_true',
                        help='Verify existing hash instead of registering')
    args = parser.parse_args()

    if args.verify:
        success = verify_hash()
        sys.exit(0 if success else 1)
    else:
        register_hash()
