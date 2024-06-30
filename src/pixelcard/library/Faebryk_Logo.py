import logging

from faebryk.core.core import Module
from faebryk.library.can_attach_to_footprint_symmetrically import (
    can_attach_to_footprint_symmetrically,
)
from faebryk.library.has_defined_footprint import has_defined_footprint
from faebryk.library.has_designator_prefix_defined import (
    has_designator_prefix_defined,
)
from faebryk.library.KicadFootprint import KicadFootprint

logger = logging.getLogger(__name__)


class Faebryk_Logo(Module):
    def __init__(self) -> None:
        super().__init__()
        self.add_trait(can_attach_to_footprint_symmetrically())
        self.add_trait(has_designator_prefix_defined("LOGO"))
        self.add_trait(
            has_defined_footprint(KicadFootprint("logo:faebryk_logo", pin_names=[]))
        )
