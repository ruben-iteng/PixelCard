# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging

from faebryk.core.core import Module
from faebryk.library.has_overriden_name_defined import has_overriden_name_defined
from faebryk.library.Net import Net
from faebryk.libs.picker.picker import pick_part_recursively
from pixelcard.library.my_library_module import MyLibraryModule
from pixelcard.modules.my_application_module import MyApplicationModule
from pixelcard.pickers import pick

logger = logging.getLogger(__name__)

"""
This file is for the top-level application modules.
This should be the entrypoint for collaborators to start in to understand your project.
Treat it as the high-level design of your project.
Avoid putting any generic or reusable application modules here.
Avoid putting any low-level modules or parameter specializations here.
"""


class PixelCard(Module):
    def __init__(self) -> None:
        super().__init__()

        # modules ------------------------------------
        class _NODEs(Module.NODES()):
            submodule = MyApplicationModule()
            my_part = MyLibraryModule()
            ...

        self.NODEs = _NODEs(self)

        class _PARAMs(Module.PARAMS()): ...

        self.PARAMs = _PARAMs(self)

        # net names ----------------------------------
        nets = {
            # "in_5v": ...power.IFs.hv,
            # "gnd": ...power.IFs.lv,
        }
        for net_name, mif in nets.items():
            net = Net()
            net.add_trait(has_overriden_name_defined(net_name))
            net.IFs.part_of.connect(mif)

        # parametrization ----------------------------

        # specialize

        # set global params

        # part picking -------------------------------
        pick_part_recursively(self, pick)
