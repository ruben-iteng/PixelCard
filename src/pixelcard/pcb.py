# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging
from pathlib import Path

from faebryk.core.core import Module
from faebryk.core.graph import Graph
from faebryk.core.util import get_all_nodes
from faebryk.exporters.pcb.kicad.transformer import PCB_Transformer
from faebryk.exporters.pcb.layout.absolute import LayoutAbsolute
from faebryk.exporters.pcb.layout.typehierarchy import LayoutTypeHierarchy
from faebryk.library.has_pcb_layout_defined import has_pcb_layout_defined
from faebryk.library.has_pcb_position import has_pcb_position
from faebryk.library.has_pcb_position_defined import has_pcb_position_defined
from faebryk.library.LED import LED
from faebryk.libs.app.pcb import apply_layouts
from faebryk.libs.kicad.pcb import PCB
from pixelcard.library.Faebryk_Logo import Faebryk_Logo
from pixelcard.modules.LEDText import LEDText
from pixelcard.modules.USB_C_5V_PSU_16p_Receptical import USB_C_5V_PSU_16p_Receptical

logger = logging.getLogger(__name__)

"""
Here you can do PCB scripting.
E.g placing components, layer switching, mass renaming, etc.
"""


def transform_pcb(pcb_file: Path, graph: Graph, app: Module):
    logger.info("Load PCB")
    pcb = PCB.load(pcb_file)
    transformer = PCB_Transformer(pcb, graph, app)

    # create pcb outline in shape of a credit card
    creditcard_width = 85.6
    creditcard_height = 53.98

    transformer.set_pcb_outline_complex(
        transformer.create_rectangular_edgecut(
            width_mm=creditcard_width,
            height_mm=creditcard_height,
            rounded_corners=True,
            corner_radius_mm=3.18,
        ),
        remove_existing_outline=True,
    )

    # move all reference designators to the same position
    footprints = [
        cmp.get_trait(PCB_Transformer.has_linked_kicad_footprint).get_fp()
        for cmp in get_all_nodes(transformer.app)
        if cmp.has_trait(PCB_Transformer.has_linked_kicad_footprint)
    ]

    for f in footprints:
        # ref
        f.reference.at.coord = (2.25, 0, 0)
        f.reference.font = (0.5, 0.5, 0.1)  # 0.075)

    # add text as silkscreen
    # TODO: reenable after fixing kicad8 compatibility
    # text = "PixelCard"
    # transformer.pcb.append(
    #    GR_Text.factory(
    #        text=text,
    #        at=At([creditcard_width / 2, creditcard_height / 2]),
    #        font=(5, 5, 0.2),  # Font(Path("/usr/share/fonts/TTF/OpenSans-Bold.ttf")),
    #        layer="F.SilkS",
    #        tstamp=str(int(random.random() * 100000)),
    #    )
    # )
    # add via to bottom plane next to every anode of the LEDs
    for node in get_all_nodes(app):
        if isinstance(node, LED):
            transformer.insert_via_next_to(node.IFs.anode, clearance=(-1, 0))

    # ----------------------------------------
    #                   Layout
    # ----------------------------------------
    Point = has_pcb_position.Point
    L = has_pcb_position.layer_type

    # TODO: ugly
    for node in get_all_nodes(app):
        if isinstance(node, LEDText):
            ledtext_width = node.PARAMs.width.value
            ledtext_height = node.PARAMs.height.value
    app.add_trait(
        has_pcb_layout_defined(
            LayoutTypeHierarchy(
                layouts=[
                    LayoutTypeHierarchy.Level(
                        mod_type=LEDText,
                        layout=LayoutAbsolute(
                            Point(
                                (
                                    creditcard_width / 2 - ledtext_width / 2,
                                    creditcard_height / 2 + ledtext_height / 2,
                                    0,
                                    L.NONE,
                                )
                            )
                        ),
                    ),
                    LayoutTypeHierarchy.Level(
                        mod_type=USB_C_5V_PSU_16p_Receptical,
                        layout=LayoutAbsolute(
                            Point(
                                (
                                    creditcard_width - 4.5,
                                    creditcard_height / 2,
                                    90,
                                    L.NONE,
                                )
                            )
                        ),
                    ),
                    LayoutTypeHierarchy.Level(
                        mod_type=Faebryk_Logo,
                        layout=LayoutAbsolute(
                            Point(
                                (
                                    creditcard_width / 2,
                                    creditcard_height / 2 + ledtext_height,
                                    0,
                                    L.NONE,
                                )
                            )
                        ),
                    ),
                ]
            )
        )
    )
    # set coordinate system
    app.add_trait(has_pcb_position_defined(Point((0, 0, 0, L.TOP_LAYER))))

    # apply layout
    apply_layouts(app)
    transformer.move_footprints()

    logger.info(f"Writing pcbfile {pcb_file}")
    pcb.dump(pcb_file)
