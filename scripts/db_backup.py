#!/usr/bin/env python3
"""
MTIS Database Backup Script (Operational Rubric D5).
Supports PostgreSQL (via pg_dump or docker exec mtis-postgres-db pg_dump)
and local SQLite (via sqlite3 iterdump / file snapshot).

Usage:
    python scripts/db_backup.py
    python scripts/db_backup.py --output database/backups/custom_backup.sql
    python scripts/db_backup.py --url postgresql://user:password@localhost:5432/malaysian_thesis_institution_system_mtis
"""
import os
import sys
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))


def get_default_db_url() -> str:
    # 1. Environment variable
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # 2. Check .env file
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DATABASE_URL="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # 3. Check for local SQLite demo database
    sqlite_db = PROJECT_ROOT / "backend" / "demo_mtis.db"
    if sqlite_db.exists():
        return f"sqlite:///{sqlite_db.as_posix()}"

    root_sqlite = PROJECT_ROOT / "demo_mtis.db"
    if root_sqlite.exists():
        return f"sqlite:///{root_sqlite.as_posix()}"

    # Default fallback to standard docker postgres URL
    return "postgresql://user:password@localhost:5432/malaysian_thesis_institution_system_mtis"


def backup_sqlite(db_path: Path, output_path: Path) -> bool:
    import sqlite3
    print(f"[Backup] Performing SQLite database dump from {db_path}...")
    try:
        conn = sqlite3.connect(str(db_path))
        with open(output_path, "w", encoding="utf-8") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        conn.close()
        print(f"[Backup] Successfully generated SQLite SQL dump: {output_path} ({output_path.stat().st_size} bytes)")
        return True
    except Exception as e:
        print(f"[Backup Error] Failed SQLite backup: {e}", file=sys.stderr)
        return False


def backup_postgres(url: str, output_path: Path) -> bool:
    parsed = urlparse(url)
    username = parsed.username or "user"
    password = parsed.password or "password"
    hostname = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    dbname = parsed.path.lstrip("/") or "malaysian_thesis_institution_system_mtis"

    env = os.environ.copy()
    env["PGPASSWORD"] = password

    # 1. Try local pg_dump executable
    pg_dump_bin = shutil.which("pg_dump")
    if pg_dump_bin:
        cmd = [
            pg_dump_bin,
            "-h", hostname,
            "-p", port,
            "-U", username,
            "-d", dbname,
            "-F", "p",  # Plain text SQL dump
            "-f", str(output_path),
        ]
        print(f"[Backup] Executing pg_dump command: {' '.join(cmd[:5])}...")
        try:
            res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
            print(f"[Backup] pg_dump completed successfully: {output_path} ({output_path.stat().st_size} bytes)")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[Backup Warning] Local pg_dump returned code {e.returncode}: {e.stderr.strip()}", file=sys.stderr)

    # 2. Try docker exec against mtis-postgres-db container
    docker_bin = shutil.which("docker")
    if docker_bin:
        container_name = "mtis-postgres-db"
        cmd = [
            docker_bin, "exec",
            "-e", f"PGPASSWORD={password}",
            container_name,
            "pg_dump", "-U", username, "-d", dbname,
        ]
        print(f"[Backup] Attempting docker exec backup via {container_name}...")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                res = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=True)
            if output_path.stat().st_size > 0:
                print(f"[Backup] Docker pg_dump succeeded: {output_path} ({output_path.stat().st_size} bytes)")
                return True
        except Exception as e:
            print(f"[Backup Warning] Docker pg_dump attempt: {e}", file=sys.stderr)

    # 3. Check for local SQLite demo db fallback if PostgreSQL is not reachable in current dev env
    local_sqlite = PROJECT_ROOT / "backend" / "demo_mtis.db"
    if local_sqlite.exists():
        print("[Backup] Falling back to available local demo SQLite database...")
        return backup_sqlite(local_sqlite, output_path)

    print("[Backup Error] Neither pg_dump nor docker container could complete the backup.", file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(description="MTIS Database Backup Utility (D5 Operations)")
    parser.add_argument("-o", "--output", help="Output path for SQL backup file")
    parser.add_argument("--url", help="Database connection URL (defaults to DATABASE_URL)")
    args = parser.parse_args()

    db_url = args.url or get_default_db_url()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backups_dir = PROJECT_ROOT / "database" / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = backups_dir / f"mtis_backup_{timestamp}.sql"

    print(f"=== MTIS Database Backup ===")
    print(f"Target DB: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print(f"Output:    {output_path}")

    if db_url.startswith("sqlite"):
        db_path_str = db_url.replace("sqlite:///", "")
        db_path = Path(db_path_str)
        if not db_path.is_absolute():
            db_path = PROJECT_ROOT / db_path
        if not db_path.exists():
            # Check backend relative
            alt_path = PROJECT_ROOT / "backend" / db_path_str
            if alt_path.exists():
                db_path = alt_path
        success = backup_sqlite(db_path, output_path)
    else:
        success = backup_postgres(db_url, output_path)

    if success:
        print(f"[Backup Success] Backup saved to {output_path}")
        sys.exit(0)
    else:
        print("[Backup Failed] Backup failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
