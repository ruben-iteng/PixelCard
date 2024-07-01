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

# from faebryk.exporters.pcb.kicad.artifacts import (
#    export_dxf,
#    export_gerber,
#    export_glb,
#    export_pick_and_place,
#    export_step,
# )
# from faebryk.exporters.pcb.pick_and_place.jlcpcb import (
#    convert_kicad_pick_and_place_to_jlcpcb,
# )
from faebryk.exporters.visualize.graph import render_matrix
from faebryk.libs.app.erc import simple_erc
from faebryk.libs.app.kicad_netlist import write_netlist
from faebryk.libs.app.parameters import replace_tbd_with_any
from faebryk.libs.logging import setup_basic_logging
from faebryk.libs.picker.picker import pick_part_recursively
from pixelcard.app import PixelCard
from pixelcard.pcb import transform_pcb
from pixelcard.pickers import pick

# logging settings
logger = logging.getLogger(__name__)


def main(
    netlist_export: bool = True,
    pcb_transform: bool = True,
    visualize_graph: bool = False,
    export_pcba_artifacts: bool = False,
):
    # paths --------------------------------------------------
    build_dir = Path("./build")
    faebryk_build_dir = build_dir.joinpath("faebryk")
    faebryk_build_dir.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).parent.parent.parent
    netlist_path = faebryk_build_dir.joinpath("faebryk.net")
    kicad_prj_path = root.joinpath("source")
    pcbfile = kicad_prj_path.joinpath("main.kicad_pcb")
    manufacturing_artifacts = build_dir.joinpath("manufacturing_artifacts")
    cad_path = manufacturing_artifacts.joinpath("cad")

    lcsc.BUILD_FOLDER = build_dir
    lcsc.LIB_FOLDER = root.joinpath("libs")

    # graph --------------------------------------------------
    try:
        sys.setrecursionlimit(50000)  # TODO needs optimization
        app = PixelCard()
    except RecursionError:
        logger.error("RECURSION ERROR ABORTING")
        return
    G = app.get_graph()

    # visualize ----------------------------------------------
    if visualize_graph:
        render_matrix(
            G.G,
            nodes_rows=[],
            depth=1,
            show_full=True,
            show_non_sum=False,
        ).show()

    # fill unspecified parameters ----------------------------
    logger.info("Filling unspecified parameters")
    # import faebryk.libs.app.parameters as p_mod

    # lvl = p_mod.logger.getEffectiveLevel()
    # p_mod.logger.setLevel(logging.DEBUG)
    replace_tbd_with_any(app, recursive=True)
    # p_mod.logger.setLevel(lvl)

    # pick parts ---------------------------------------------
    pick_part_recursively(app, pick)
    G = app.get_graph()
    simple_erc(G)

    # netlist -----------------------------------------------
    changed = False
    if netlist_export:
        logger.info(f"Writing netlist to {netlist_path}")
        changed = write_netlist(G, netlist_path, use_kicad_designators=True)

    # pcb ----------------------------------------------------
    if pcb_transform:
        if changed:
            print(
                "Open the PCB in kicad and import the netlist.\n"
                "Then save the pcb and press ENTER.\n"
                f"PCB location: {pcbfile}"
            )
            input()

        logger.info("Transform PCB")
        transform_pcb(pcbfile, G, app)

        print("Reopen PCB in kicad")

    # ---------------------------------------------------------

    # generate pcba manufacturing and other artifacts ---------
    # if export_pcba_artifacts:
    #    logger.info("Exporting PCBA artifacts")
    #    write_bom_jlcpcb(
    #        get_all_modules(app), manufacturing_artifacts.joinpath("jlcpcb_bom.csv")
    #    )
    #    export_step(pcbfile, step_file=cad_path.joinpath("pcba.step"))
    #    export_glb(pcbfile, glb_file=cad_path.joinpath("pcba.glb"))
    #    export_dxf(pcbfile, dxf_file=cad_path.joinpath("pcba.dxf"))
    #    export_gerber(
    #        pcbfile, gerber_zip_file=manufacturing_artifacts.joinpath("gerber.zip")
    #    )
    #    pnp_file = manufacturing_artifacts.joinpath("pick_and_place.csv")
    #    export_pick_and_place(pcbfile, pick_and_place_file=pnp_file)
    #    convert_kicad_pick_and_place_to_jlcpcb(
    #        pnp_file,
    #        manufacturing_artifacts.joinpath("jlcpcb_pick_and_place.csv"),
    #    )


if __name__ == "__main__":
    setup_basic_logging()
    typer.run(main)
