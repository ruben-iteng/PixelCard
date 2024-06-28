# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging

import faebryk.library._F as F
from faebryk.core.core import Module
from faebryk.core.util import get_all_nodes
from faebryk.library.has_overriden_name_defined import has_overriden_name_defined
from faebryk.library.Net import Net
from faebryk.libs.brightness import TypicalLuminousIntensity
from faebryk.libs.util import times
from pixelcard.modules.USB_C_5V_PSU_16p_Receptical import USB_C_5V_PSU_16p_Receptical

logger = logging.getLogger(__name__)


class PixelCard(Module):
    def __init__(self) -> None:
        super().__init__()

        # ----------------------------------------
        #     modules, interfaces, parameters
        # ----------------------------------------
        class _NODEs(Module.NODES()):
            leds = times(2, F.PoweredLED)
            usb_psu = USB_C_5V_PSU_16p_Receptical()

        self.NODEs = _NODEs(self)

        class _PARAMs(Module.PARAMS()): ...

        self.PARAMs = _PARAMs(self)

        # ----------------------------------------
        #                aliases
        # ----------------------------------------
        vbus = self.NODEs.usb_psu.IFs.power_out
        gnd = self.NODEs.usb_psu.IFs.power_out.IFs.lv

        # ----------------------------------------
        #                net names
        # ----------------------------------------
        nets = {
            "vbus": vbus.IFs.hv,
            "gnd": gnd,
        }
        for net_name, mif in nets.items():
            net = Net()
            net.add_trait(has_overriden_name_defined(net_name))
            net.IFs.part_of.connect(mif)

        # ----------------------------------------
        #              connections
        # ----------------------------------------
        for led in self.NODEs.leds:
            led.IFs.power.connect(vbus)

        # ----------------------------------------
        #              parametrization
        # ----------------------------------------
        for pled in self.NODEs.leds:
            pled.NODEs.led.PARAMs.brightness.merge(
                TypicalLuminousIntensity.APPLICATION_LED_DECORATIVE_LIGHTING
            )
            pled.NODEs.led.PARAMs.color.merge(F.LED.Color.RED)

        # ----------------------------------------
        #              specializations
        # ----------------------------------------
        for node in get_all_nodes(self):
            if node.has_trait(F.is_decoupled):
                # TODO do somewhere else
                capacitance = (
                    node.get_trait(F.is_decoupled).get_capacitor().PARAMs.capacitance
                )
                if isinstance(capacitance.get_most_narrow(), F.TBD):
                    capacitance.merge(F.Constant(100e-9))
