#!/usr/bin/env python3
import gzip
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import yaml


def run(cmd, **kwargs):
    print("+ " + " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True, **kwargs)


def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "/app/config.yml"

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    backup_root = cfg["backup_root"].rstrip("/")
    local_tmp = Path(cfg.get("local_tmp", "/tmp/mariadb-backups"))
    keep_last = int(cfg.get("keep_last", 3))

    dump_cfg = cfg.get("dump", {})
    dump_binary = dump_cfg.get("binary", "mariadb-dump")
    dump_extra_args = dump_cfg.get("extra_args", [
        "--single-transaction",
        "--quick",
        "--routines",
        "--triggers",
        "--events",
        "--hex-blob",
    ])

    local_tmp.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    for server in cfg["servers"]:
        server_name = server["name"]

        for database in server["databases"]:
            env = os.environ.copy()
            env["MYSQL_PWD"] = str(server["password"])

            filename = f"{database}-{timestamp}.sql.gz"
            output_path = local_tmp / filename
            remote_dir = f"{backup_root}/{server_name}/{database}"

            dump_cmd = [
                dump_binary,
                "--host", str(server["host"]),
                "--port", str(server.get("port", 3306)),
                "--user", str(server["user"]),
                *dump_extra_args,
                "--databases", database,
            ]

            with tempfile.NamedTemporaryFile(delete=False) as raw_dump:
                raw_path = Path(raw_dump.name)

            try:
                print(f"[{server_name}/{database}] Creating MariaDB dump...")
                with open(raw_path, "wb") as out:
                    run(dump_cmd, stdout=out, env=env)

                print(f"[{server_name}/{database}] Compressing...")
                with open(raw_path, "rb") as src, gzip.open(output_path, "wb", compresslevel=6) as dst:
                    shutil.copyfileobj(src, dst)

                print(f"[{server_name}/{database}] Uploading to Google Drive...")
                run(["rclone", "mkdir", remote_dir])
                run(["rclone", "copyto", str(output_path), f"{remote_dir}/{filename}"])

                print(f"[{server_name}/{database}] Verifying upload...")
                run(["rclone", "lsf", f"{remote_dir}/{filename}"], stdout=subprocess.DEVNULL)

                print(f"[{server_name}/{database}] Applying retention...")
                result = subprocess.run(
                    ["rclone", "lsf", remote_dir, "--files-only"],
                    text=True,
                    capture_output=True,
                    check=True,
                )

                files = sorted(
                    [x.strip() for x in result.stdout.splitlines() if x.strip().endswith(".sql.gz")],
                    reverse=True,
                )

                for old_file in files[keep_last:]:
                    print(f"[{server_name}/{database}] Removing old backup: {old_file}")
                    run(["rclone", "deletefile", f"{remote_dir}/{old_file}"])

                print(f"[{server_name}/{database}] OK")

            finally:
                raw_path.unlink(missing_ok=True)
                output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
