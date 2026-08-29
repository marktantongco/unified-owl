#!/usr/bin/env python3
"""🦉 OWL-AGENT Online SQLite Backup Utility with Automatic Gzip Compression"""
import datetime
import gzip
import os
import shutil
import sqlite3
import sys

DATA_DIR = os.path.expanduser("~/.owl-agent/data")
DB_SRC = os.path.join(DATA_DIR, "scrapes.sqlite")

def run_backup(retention_days=7, compress=True):
    if not os.path.exists(DB_SRC):
        print(f"Source database not found: {DB_SRC}", file=sys.stderr)
        return
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp_dst = os.path.join(DATA_DIR, f"backup_{date_str}.sqlite.tmp")
    final_dst = os.path.join(DATA_DIR, f"backup_{date_str}.sqlite.gz" if compress else f"backup_{date_str}.sqlite")
    
    src = sqlite3.connect(DB_SRC)
    dst = sqlite3.connect(tmp_dst)
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

    if compress:
        with open(tmp_dst, "rb") as f_in:
            with gzip.open(final_dst, "wb", compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
        if os.path.exists(tmp_dst):
            os.remove(tmp_dst)
    else:
        os.rename(tmp_dst, final_dst)

    print(f"✓ Created compressed backup: {final_dst} ({os.path.getsize(final_dst)} bytes)")

    # Prune old backups
    now = datetime.datetime.now()
    for fname in os.listdir(DATA_DIR):
        if fname.startswith("backup_") and (fname.endswith(".sqlite") or fname.endswith(".sqlite.gz")):
            fpath = os.path.join(DATA_DIR, fname)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))
            if (now - mtime).days > retention_days:
                os.remove(fpath)
                print(f"Pruned stale backup: {fname}")

if __name__ == "__main__":
    run_backup()
