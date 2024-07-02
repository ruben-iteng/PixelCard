# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging
from pathlib import Path

from faebryk.core.graph import Graph
from faebryk.core.util import get_all_nodes
from faebryk.exporters.pcb.kicad.transformer import PCB_Transformer
from faebryk.exporters.pcb.layout.absolute import LayoutAbsolute
from faebryk.exporters.pcb.layout.typehierarchy import LayoutTypeHierarchy
from faebryk.library.has_pcb_layout_defined import has_pcb_layout_defined
from faebryk.library.has_pcb_position import has_pcb_position
from faebryk.library.has_pcb_position_defined import has_pcb_position_defined
from faebryk.library.has_pcb_routing_strategy_via_to_layer import (
    has_pcb_routing_strategy_via_to_layer,
)
from faebryk.libs.app.pcb import apply_layouts, apply_routing
from faebryk.libs.kicad.pcb import PCB, At, Font
from pixelcard.app import PixelCard
from pixelcard.library.Faebryk_Logo import Faebryk_Logo
from pixelcard.modules.LEDText import LEDText
from pixelcard.modules.USB_C_5V_PSU_16p_Receptical import USB_C_5V_PSU_16p_Receptical

logger = logging.getLogger(__name__)

"""
Here you can do PCB scripting.
E.g placing components, layer switching, mass renaming, etc.
"""


def transform_pcb(pcb_file: Path, graph: Graph, app: PixelCard):
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
        f.reference.font = Font.factory(size=(0.5, 0.5), thickness=0.1)  # 0.075)

    font = app.font
    font_name = font.path.stem
    bold = False
    if "-Bold" in font_name:
        font_name, _ = font_name.split("-Bold")
        bold = True

    TEXT_POS = (2, 2)

    # TODO better trace actual font
    # add text as silkscreen
    # transformer.insert_text(
    #    text=app.text,
    #    at=At.factory(
    #        (
    #            -2.5 + TEXT_POS[0],
    #            0.5 + TEXT_POS[1],
    #        )
    #    ),
    #    font=Font.factory(
    #        size=app.NODEs.text.char_dimension,
    #        thickness=0.2,
    #        bold=bold,
    #        face=font_name,
    #    ),
    # )

    for i, line in enumerate(app.contact_info.split("\\n")):
        transformer.insert_text(
            text=line,
            at=At.factory((creditcard_width / 2, creditcard_height / 2 + i * 5)),
            font=Font.factory(
                size=(2, 2),
                thickness=0.1,
                bold=bold,
                face=font_name,
            ),
            front=False,
        )

    app.NODEs.net_vbus.add_trait(
        has_pcb_routing_strategy_via_to_layer(
            "B.Cu",
            (0.8, 0.3),
        )
    )
    app.NODEs.net_gnd.add_trait(
        has_pcb_routing_strategy_via_to_layer(
            "F.Cu",
            (0.5, 0.5),
        )
    )
    # ----------------------------------------
    #                   Layout
    # ----------------------------------------
    Point = has_pcb_position.Point
    L = has_pcb_position.layer_type

    # TODO: ugly
    for node in get_all_nodes(app):
        if isinstance(node, LEDText):
            # ledtext_width = node.PARAMs.width.value
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
                                    -7 + TEXT_POS[0],
                                    1.5 + TEXT_POS[1],
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
                                    2 * ledtext_height + 2.5,
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

    apply_routing(app, transformer)

    logger.info(f"Writing pcbfile {pcb_file}")
    pcb.dump(pcb_file)
