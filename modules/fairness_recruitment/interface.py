
from pathlib import Path
import runpy
import sys


def render() -> None:
    module_dir = Path(__file__).resolve().parent
    module_path = str(module_dir)

    if module_path not in sys.path:
        sys.path.insert(0, module_path)

    ui_path = module_dir / "fairhire_ui.py"
    runpy.run_path(str(ui_path), run_name="__main__")
