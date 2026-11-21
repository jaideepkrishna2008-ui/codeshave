"""
Quick programmatic usage of ContextForge in Python scripts.
"""

from pathlib import Path
from contextforge import compress_source, compute_savings

sample_file = Path(__file__).parent / "demo_fastapi_service.py"
raw_code = sample_file.read_text(encoding="utf-8")

# Compress using AST visitor
skeleton = compress_source(raw_code, preserve_docstrings=True)
report = compute_savings(raw_code, skeleton)

print("=" * 60)
print("CONTEXTFORGE SKELETON DEMO")
print("=" * 60)
print(skeleton)
print("=" * 60)
print(report.summary_line())
print(f"Estimated savings: ${report.estimated_cost_saved_usd:.6f} per call")
print("=" * 60)
