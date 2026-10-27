"""Load the official offline tools from the extracted capstone dataset."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType

_cached: tuple[str, ModuleType] | None = None


def _load_tools() -> ModuleType:
    global _cached
    configured = os.getenv("ZENTOMART_DATA_DIR", "").strip()
    if not configured:
        raise RuntimeError(
            "ZENTOMART_DATA_DIR is missing. Set it to the extracted "
            "Capstone_Project_Dataset_FTTT_2026 folder."
        )
    root = Path(configured).expanduser().resolve()
    tools_file = root / "tools" / "tools.py"
    if not tools_file.is_file():
        raise FileNotFoundError(f"Supplied dataset tools not found: {tools_file}")
    if _cached and _cached[0] == str(tools_file):
        return _cached[1]
    spec = importlib.util.spec_from_file_location("zentomart_dataset_tools", tools_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load supplied tools from {tools_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _cached = (str(tools_file), module)
    return module


def lookup_order(order_id: str, verification_value: str | None = None) -> dict:
    """Call the dataset's identity-gated order lookup without bypassing checks."""
    return _load_tools().lookup_order(order_id, verification_value=verification_value)


def create_ticket(summary: str, order_id: str | None = None,
                  reason: str | None = None, intent: str | None = None) -> dict:
    """Create a synthetic handover ticket using the supplied dataset tool."""
    return _load_tools().create_ticket(
        summary=summary, order_id=order_id, reason=reason, intent=intent
    )
