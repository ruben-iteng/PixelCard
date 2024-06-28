# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging

from faebryk.core.core import Module

logger = logging.getLogger(__name__)


# Files in /library are for non-application-specific modules
# These files are mostly good candidates for upstreaming to faebryk
# Application specific modules should not be placed in /library but in /modules
# Only one module per file
# For typical library module examples check out faebryk.library


class MyLibraryModule(Module):
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
