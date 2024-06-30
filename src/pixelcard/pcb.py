# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging
from pathlib import Path

from faebryk.core.core import Module
from faebryk.core.graph import Graph
from faebryk.core.util import get_all_modules
from faebryk.exporters.pcb.kicad.transformer import PCB_Transformer
from faebryk.exporters.pcb.layout.absolute import LayoutAbsolute
from faebryk.exporters.pcb.layout.typehierarchy import LayoutTypeHierarchy
from faebryk.library.has_pcb_layout import has_pcb_layout
from faebryk.library.has_pcb_layout_defined import has_pcb_layout_defined
from faebryk.library.has_pcb_position import has_pcb_position
from faebryk.library.has_pcb_position_defined import has_pcb_position_defined
from faebryk.libs.kicad.pcb import PCB
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
    transformer.set_dimensions_rectangle(
        width_mm=creditcard_width,
        height_mm=creditcard_height,
        origin_x_mm=0,
        origin_y_mm=0,
    )

    # ----------------------------------------
    #                   Layout
    # ----------------------------------------
    Point = has_pcb_position.Point
    L = has_pcb_position.layer_type

    layout = LayoutTypeHierarchy(
        layouts=[
            LayoutTypeHierarchy.Level(
                mod_type=LEDText,
                layout=LayoutAbsolute(Point((0, 0, 0, L.TOP_LAYER))),
            ),
            LayoutTypeHierarchy.Level(
                mod_type=USB_C_5V_PSU_16p_Receptical,
                layout=LayoutAbsolute(
                    Point((creditcard_width, creditcard_height, 90, L.TOP_LAYER))
                ),
            ),
        ]
    )
    app.add_trait(has_pcb_layout_defined(layout))
    # set pcb center position
    app.add_trait(has_pcb_position_defined(Point((0, 0, 0, L.TOP_LAYER))))

    # apply layout
    if not app.has_trait(has_pcb_position):
        app.add_trait(has_pcb_position_defined(Point((0, 0, 0, L.TOP_LAYER))))
    for n in get_all_modules(app) | {app}:
        if n.has_trait(has_pcb_layout):
            n.get_trait(has_pcb_layout).apply()
    transformer.move_footprints()

    logger.info(f"Writing pcbfile {pcb_file}")
    pcb.dump(pcb_file)
