#!/usr/bin/env python3
"""F115 (Sprint 15 Task F): read the text of page images with RapidOCR. Runs only under the OCR virtual environment
(`store.ocr.engine_python`), never the main interpreter: RapidOCR's dependencies would raise this machine's numpy
from 1.26 to 2.5. `store.ocr` calls it; it is not meant to be run by hand.

    <ocr-venv python> -I scripts/ocr_worker.py <image> [<image> ...]

Prints one JSON object: the engine (RapidOCR's and ONNX Runtime's versions, and each model file's SHA-256, so the
provenance names exactly what read the page) and each image's text, its lines in the order the engine gives them.
The models ship inside RapidOCR's wheel; a missing one is an error here, never a download.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path


def engine() -> dict:
    import onnxruntime
    import rapidocr
    models = Path(rapidocr.__file__).parent / "models"
    files = sorted(models.glob("*.onnx"))
    if len(files) < 3:  # detection, recognition and the direction classifier
        raise SystemExit(f"RapidOCR's models are missing from {models}; reinstall from requirements-ocr.txt "
                         "(this worker never downloads one)")
    return {"rapidocr": importlib.metadata.version("rapidocr"), "onnxruntime": onnxruntime.__version__,
            "models": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}


def main(images: list[str]) -> int:
    from rapidocr import RapidOCR
    info = engine()
    reader = RapidOCR()
    pages = []
    for image in images:
        result = reader(image)
        pages.append({"image": image, "text": "\n".join(result.txts or ())})
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"engine": info, "pages": pages}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
