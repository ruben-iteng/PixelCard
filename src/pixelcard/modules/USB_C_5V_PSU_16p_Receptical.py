# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

from faebryk.core.core import Module
from faebryk.library.can_be_decoupled import can_be_decoupled
from faebryk.library.Constant import Constant
from faebryk.library.ElectricPower import ElectricPower
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

        for vbus in self.NODEs.usb.IFs.vbus:
            vbus.connect(self.IFs.power_out.IFs.hv)
        for gnd in self.NODEs.usb.IFs.gnd:
            gnd.connect(self.IFs.power_out.IFs.lv)
