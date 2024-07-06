# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

"""
This is the entrypoint and boilerplate of the application.
It sets up several paths and calls the app to create the graph.
Afterwards it uses the graph to export to different artifacts (e.g netlist).
"""

import logging
import sys
from pathlib import Path

import faebryk.libs.picker.lcsc as lcsc
import typer
from faebryk.libs.app.checks import run_checks
from faebryk.libs.app.manufacturing import export_pcba_artifacts
from faebryk.libs.app.parameters import replace_tbd_with_any
from faebryk.libs.app.pcb import apply_design
from faebryk.libs.font import Font
from faebryk.libs.logging import setup_basic_logging
from faebryk.libs.picker.picker import pick_part_recursively
from pixelcard.app import PixelCard
from pixelcard.pcb import transform_pcb
from pixelcard.pickers import pick

# logging settings
logger = logging.getLogger(__name__)


def get_font(font_path: Path, font_url: str):
    if font_path.exists():
        return

    import zipfile
    from io import BytesIO

    import requests

    r = requests.get(font_url)
    zip_content = BytesIO(r.content)

    # Extract the specific file from the zip into the desired location
    with zipfile.ZipFile(zip_content, "r") as zip_ref:
        zip_ref.extract(font_path.name, font_path.parent)


def main(
    visualize_graph: bool = typer.Option(False, help="Visualize the faebryk graph"),
    export_artifacts: bool = typer.Option(False, help="Export PCBA artifacts"),
    led_text: str = typer.Argument("PixelCard", help="Text to convert into LEDText."),
    contact_info: str = typer.Argument(help="Your contact information."),
):
    # paths --------------------------------------------------
    build_dir = Path("./build")
    font_cache_dir = build_dir / Path("cache") / Path("fonts")
    faebryk_build_dir = build_dir.joinpath("faebryk")
    faebryk_build_dir.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).parent.parent.parent
    netlist_path = faebryk_build_dir.joinpath("faebryk.net")
    kicad_prj_path = root.joinpath("source")
    pcbfile = kicad_prj_path.joinpath("main.kicad_pcb")
    manufacturing_artifacts = build_dir.joinpath("manufacturing_artifacts")

    lcsc.BUILD_FOLDER = build_dir
    lcsc.LIB_FOLDER = root.joinpath("libs")

    # Get font
    font_path = font_cache_dir / Path("Minecraftia-Regular.ttf")
    font_url = "https://dl.dafont.com/dl/?f=minecraftia"
    get_font(font_path, font_url)

    # Run app
    try:
        sys.setrecursionlimit(50000)  # TODO needs optimization
        app = PixelCard(
            font=Font(font_path),
            _text=led_text,
            contact_info=contact_info,
        )
    except RecursionError:
        logger.error("RECURSION ERROR ABORTING")
        return

    logger.info("Filling unspecified parameters")
    replace_tbd_with_any(app, recursive=True)

    # pick parts
    pick_part_recursively(app, pick)

    G = app.get_graph()
    run_checks(app, G)

    # netlist & pcb
    apply_design(pcbfile, netlist_path, G, app, transform=transform_pcb)

    # generate pcba manufacturing and other artifacts
    if export_artifacts:
        export_pcba_artifacts(manufacturing_artifacts, pcbfile, app)


if __name__ == "__main__":
    setup_basic_logging()
    typer.run(main)
