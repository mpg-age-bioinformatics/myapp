#!/usr/bin/env python3
"""Run once daily inside the configured application container."""
import argparse
import json

from pathlib import Path
import sys

# The container runs from source; include the repository root for direct execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myapp import app
from myapp.email_revalidation import run_email_revalidation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Report counts without sending email or updating users.')
    args = parser.parse_args()
    with app.app_context():
        counts = run_email_revalidation(dry_run=args.dry_run)
    print(json.dumps(counts, sort_keys=True))
    return 1 if counts['failed'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
