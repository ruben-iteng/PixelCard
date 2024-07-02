# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging

from faebryk.core.core import Module
from faebryk.library.has_overriden_name_defined import has_overriden_name_defined
from faebryk.library.has_pcb_routing_strategy_via_to_layer import (
    has_pcb_routing_strategy_via_to_layer,
)
from faebryk.library.Net import Net
from pixelcard.library.Faebryk_Logo import Faebryk_Logo
from pixelcard.modules.LEDText import LEDText
from pixelcard.modules.USB_C_5V_PSU_16p_Receptical import USB_C_5V_PSU_16p_Receptical

logger = logging.getLogger(__name__)


class PixelCard(Module):
    def __init__(self) -> None:
        super().__init__()

        # ----------------------------------------
        #     modules, interfaces, parameters
        # ----------------------------------------
        class _NODEs(Module.NODES()):
            text = LEDText(text="F", char_dimensions=(10, 14))
            usb_psu = USB_C_5V_PSU_16p_Receptical()
            faebryk_logo = Faebryk_Logo()

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
            setattr(self.NODEs, f"net_{net_name}", net)

        self.NODEs.net_vbus.add_trait(
            has_pcb_routing_strategy_via_to_layer(
                "B.Cu",
                (0.8, 0.3),
            )
        )
        self.NODEs.net_gnd.add_trait(
            has_pcb_routing_strategy_via_to_layer(
                "F.Cu",
                (0, 0),
            )
        )

        # ----------------------------------------
        #              connections
        # ----------------------------------------
        self.NODEs.text.IFs.power.connect(vbus)

        # ----------------------------------------
        #              parametrization
        # ----------------------------------------

        # ----------------------------------------
        #              specializations
        # ----------------------------------------
        # for node in get_all_nodes(self):
        #    if node.has_trait(F.is_decoupled):
        #        # TODO do somewhere else
        #        capacitance = (
        #            node.get_trait(F.is_decoupled).get_capacitor().PARAMs.capacitance
        #        )
        #        if isinstance(capacitance.get_most_narrow(), F.TBD):
        #            capacitance.merge(F.Constant(100e-9))
