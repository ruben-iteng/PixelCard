# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging

from faebryk.core.core import Module

logger = logging.getLogger(__name__)


# Files in /modules are for application-specific modules
# Non-application-specific modules should not be placed in /modules but in /library
# If you come from a classical EDA background, think of these as hiearchical sheets


class MyApplicationModule(Module):
    def __init__(self) -> None:
        super().__init__()

        class _NODEs(Module.NODES()):
            submodule = MyApplicationModuleSubmodule()
            ...

        self.NODEs = _NODEs(self)

        class _IFs(Module.IFS()):
            ...

        self.IFs = _IFs(self)

        class _PARAMs(Module.PARAMS()):
            ...

        self.PARAMs = _PARAMs(self)

        # self.add_trait()
        # self.add_trait()
        # self.add_trait()


class MyApplicationModuleSubmodule(Module):
    def __init__(self) -> None:
        super().__init__()

        class _NODEs(Module.NODES()):
            ...

        self.NODEs = _NODEs(self)

        class _IFs(Module.IFS()):
            ...

        self.IFs = _IFs(self)

        class _PARAMs(Module.PARAMS()):
            ...

        self.PARAMs = _PARAMs(self)

        # self.add_trait()
        # self.add_trait()
        # self.add_trait()
