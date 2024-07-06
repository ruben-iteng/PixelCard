# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging

from faebryk.core.util import (
    get_all_nodes,
    get_first_child_of_type,
)
from faebryk.exporters.pcb.kicad.transformer import PCB_Transformer, Zone
from faebryk.exporters.pcb.layout.absolute import LayoutAbsolute
from faebryk.exporters.pcb.layout.typehierarchy import LayoutTypeHierarchy
from faebryk.exporters.pcb.routing.util import Path as FPath
from faebryk.library.Capacitor import Capacitor
from faebryk.library.has_pcb_layout_defined import has_pcb_layout_defined
from faebryk.library.has_pcb_position import has_pcb_position
from faebryk.library.has_pcb_position_defined import has_pcb_position_defined
from faebryk.library.has_pcb_routing_strategy import has_pcb_routing_strategy
from faebryk.library.has_pcb_routing_strategy_manual import (
    has_pcb_routing_strategy_manual,
)
from faebryk.library.has_pcb_routing_strategy_via_to_layer import (
    has_pcb_routing_strategy_via_to_layer,
)
from faebryk.libs.font import Font as Ffont
from faebryk.libs.kicad.pcb import At, Font
from pixelcard.app import PixelCard
from pixelcard.library.Faebryk_Logo import Faebryk_Logo
from pixelcard.modules.LEDText import LEDText
from pixelcard.modules.USB_C_5V_PSU_16p_Receptical import USB_C_5V_PSU_16p_Receptical

logger = logging.getLogger(__name__)

"""
Here you can do PCB scripting.
E.g placing components, layer switching, mass renaming, etc.
"""


def transform_pcb(transformer: PCB_Transformer):
    app = transformer.app
    assert isinstance(app, PixelCard)

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

    font = Ffont(app.font.path)

    polygons = font.string_to_polygons(
        app.font_settings["text"],
        app.font_settings["font_size"],
        bbox=app.font_settings["bbox"],
        scale_to_fit=app.font_settings["scale_to_fit"],
    )

    for polygon in polygons:
        transformer.insert(
            Zone.factory(
                net=0,
                net_name="Text",
                layer="F.SilkS",
                uuid=transformer.gen_uuid(mark=True),
                name="Text_polygon",
                polygon=[
                    (
                        p[0] + app.font_settings["pcb_offset"][0],
                        p[1] + app.font_settings["pcb_offset"][1],
                    )
                    for p in polygon.exterior.coords
                ],
            )
        )

    ledtext_height = (
        max([p.bounds[3] for p in polygons]) + app.font_settings["pcb_offset"][1]
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

    for i, line in enumerate(app.contact_info.split("\\n")):
        transformer.insert_text(
            text=line,
            at=At.factory((creditcard_width / 3, creditcard_height / 3 + i * 5)),
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
    app.NODEs.net_gnd.get_trait(has_pcb_routing_strategy).priority = 1.0

    # vbus routing usb-c connector
    usb_con = app.NODEs.usb_psu.NODEs.usb
    usb_con.add_trait(
        has_pcb_routing_strategy_manual(
            [
                (
                    usb_con.IFs.vbus,
                    FPath(
                        [
                            FPath.Track(
                                0.1,
                                "F.Cu",
                                [
                                    # vbus[0]
                                    (-2.5, -2.5),
                                    (-1.5, -1),
                                    (0, -1),
                                    (1.5, -1),
                                    # vbus[1]
                                    (2.5, -2.5),
                                ],
                            )
                        ]
                    ),
                ),
            ]
        )
    )

    get_first_child_of_type(app.NODEs.usb_psu, Capacitor).IFs.unnamed[0].add_trait(
        has_pcb_routing_strategy_via_to_layer("B.Cu", (0, -1))
    )

    # ----------------------------------------
    #                   Layout
    # ----------------------------------------
    Point = has_pcb_position.Point
    L = has_pcb_position.layer_type

    app.add_trait(
        has_pcb_layout_defined(
            LayoutTypeHierarchy(
                layouts=[
                    LayoutTypeHierarchy.Level(
                        mod_type=LEDText,
                        layout=LayoutAbsolute(
                            Point(
                                (
                                    0 + app.font_settings["pcb_offset"][0],
                                    0 + app.font_settings["pcb_offset"][1],
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
                                    ledtext_height
                                    + (creditcard_height - ledtext_height) / 2,
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
                                    ledtext_height
                                    + (creditcard_height - ledtext_height) / 2,
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
