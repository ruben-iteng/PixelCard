# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

from faebryk.core.core import Module
from faebryk.exporters.pcb.layout.typehierarchy import LayoutTypeHierarchy
from faebryk.library.can_be_decoupled import can_be_decoupled
from faebryk.library.Capacitor import Capacitor
from faebryk.library.Constant import Constant
from faebryk.library.ElectricPower import ElectricPower
from faebryk.library.Fuse import Fuse
from faebryk.library.has_pcb_layout_defined import has_pcb_layout_defined
from faebryk.library.has_pcb_position import has_pcb_position
from faebryk.library.Range import Range
from faebryk.library.Resistor import Resistor
from faebryk.libs.units import k
from faebryk.libs.util import times
from pixelcard.library.USB_Type_C_Receptacle_16_pin import (
    USB_Type_C_Receptacle_16_pin,
)


class USB_C_5V_PSU_16p_Receptical(Module):
    def __init__(self) -> None:
        super().__init__()

        # interfaces
        class _IFs(Module.IFS()):
            power_out = ElectricPower()

        self.IFs = _IFs(self)

        # components
        class _NODEs(Module.NODES()):
            usb = USB_Type_C_Receptacle_16_pin()
            fuse = Fuse()
            configuration_resistors = times(
                2,
                lambda: Resistor().builder(
                    lambda r: r.PARAMs.resistance.merge(Constant(5.1 * k))
                ),
            )

        self.NODEs = _NODEs(self)

        self.IFs.power_out.get_trait(can_be_decoupled).decouple()

        # configure as ufp with 5V@max3A
        self.NODEs.usb.IFs.cc1.connect_via(
            self.NODEs.configuration_resistors[0], self.IFs.power_out.IFs.lv
        )
        self.NODEs.usb.IFs.cc2.connect_via(
            self.NODEs.configuration_resistors[1], self.IFs.power_out.IFs.lv
        )

        # set all parameters
        self.NODEs.fuse.PARAMs.trip_current.merge(Constant(1))
        self.NODEs.fuse.PARAMs.fuse_type.merge(Fuse.FuseType.RESETTABLE)
        self.NODEs.fuse.PARAMs.response_type.merge(Fuse.ResponseType.SLOW)

        self.IFs.power_out.PARAMs.voltage.merge(Range(4.75, 5.5))

        for vbus in self.NODEs.usb.IFs.vbus:
            vbus.connect_via(self.NODEs.fuse, self.IFs.power_out.IFs.hv)
        for gnd in self.NODEs.usb.IFs.gnd:
            gnd.connect(self.IFs.power_out.IFs.lv)

        for i, resistor in enumerate(self.NODEs.configuration_resistors):
            resistor.add_trait(
                has_pcb_layout_defined(
                    LayoutTypeHierarchy(
                        layouts=[
                            LayoutTypeHierarchy.Level(
                                mod_type=Resistor,
                                position=has_pcb_position.Point(
                                    (
                                        4.75,
                                        -1.25 if i == 0 else 1.25,
                                        90,
                                        has_pcb_position.layer_type.TOP_LAYER,
                                    )
                                ),
                            ),
                        ]
                    )
                )
            )
        for node in self.NODEs.get_all():
            node.add_trait(
                has_pcb_layout_defined(
                    LayoutTypeHierarchy(
                        layouts=[
                            LayoutTypeHierarchy.Level(
                                mod_type=USB_Type_C_Receptacle_16_pin,
                                position=has_pcb_position.Point(
                                    (0, 0, 0, has_pcb_position.layer_type.TOP_LAYER)
                                ),
                            ),
                            LayoutTypeHierarchy.Level(
                                mod_type=Fuse,
                                position=has_pcb_position.Point(
                                    (
                                        4.75,
                                        2.4,
                                        90,
                                        has_pcb_position.layer_type.TOP_LAYER,
                                    )
                                ),
                            ),
                            LayoutTypeHierarchy.Level(
                                mod_type=Capacitor,
                                position=has_pcb_position.Point(
                                    (6, 0, 0, has_pcb_position.layer_type.TOP_LAYER)
                                ),
                            ),
                        ]
                    )
                )
            )
