# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

from faebryk.core.core import Module
from faebryk.library.DifferentialPair import (
    DifferentialPair,
)
from faebryk.library.Electrical import Electrical
from faebryk.library.has_designator_prefix_defined import (
    has_designator_prefix_defined,
)
from faebryk.libs.util import times


class USB_Type_C_Receptacle_16_pin(Module):
    def __init__(self) -> None:
        super().__init__()

        class _IFs(Module.IFS()):
            cc1 = Electrical()
            cc2 = Electrical()
            sbu1 = Electrical()
            sbu2 = Electrical()
            shield = Electrical()
            # power
            gnd = times(4, Electrical)
            vbus = times(4, Electrical)
            # diffpairs: p, n
            d1 = DifferentialPair()
            d2 = DifferentialPair()

        self.IFs = _IFs(self)

        self.add_trait(has_designator_prefix_defined("P"))
