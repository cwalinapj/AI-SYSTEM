from __future__ import annotations

import io
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.artifacts.s3 import checksum, upload_bytes


def bundle_directory(source_dir: Path, project: str, workflow: str) -> str:
    """
    Tar-gz a directory and upload it to MinIO.
    Returns the s3:// URI.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    key = f"projects/{project}/bundles/{workflow}/{timestamp}.tar.gz"

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(source_dir, arcname=source_dir.name)
    data = buf.getvalue()

    uri = upload_bytes(key, data, content_type="application/gzip")
    return uri


def bundle_files(files: dict[str, bytes], project: str, workflow: str) -> str:
    """
    Bundle a dict of {filename: content} into a tar.gz and upload.
    Returns the s3:// URI.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    key = f"projects/{project}/bundles/{workflow}/{timestamp}.tar.gz"

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, content in files.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    data = buf.getvalue()

    uri = upload_bytes(key, data, content_type="application/gzip")
    return uri
