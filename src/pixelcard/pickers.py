# This file is part of the faebryk project
# SPDX-License-Identifier: MIT

import logging

from faebryk.core.core import Module
from faebryk.library.Capacitor import Capacitor
from faebryk.library.Constant import Constant
from faebryk.library.Fuse import Fuse
from faebryk.library.LED import LED
from faebryk.library.Resistor import Resistor
from faebryk.libs.picker.lcsc import LCSC_Part
from faebryk.libs.picker.picker import PickerOption, pick_module_by_params
from pixelcard.library.USB_Type_C_Receptacle_16_pin import (
    USB_Type_C_Receptacle_16_pin,
)

logger = logging.getLogger(__name__)

"""
This file is for picking actual electronic components for your design.
You can make use of faebryk's picker & parameter system to do this.
"""

# part pickers --------------------------------------------


def pick_resistor(resistor: Resistor):
    """
    Link a partnumber/footprint to a Resistor

    Selects only 1% 0402 resistors
    """

    pick_module_by_params(
        resistor,
        [
            PickerOption(
                part=LCSC_Part(partno="C25076"),
                params={"resistance": Constant(100)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25087"),
                params={"resistance": Constant(200)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C11702"),
                params={"resistance": Constant(1e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25879"),
                params={"resistance": Constant(2.2e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25900"),
                params={"resistance": Constant(4.7e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25905"),
                params={"resistance": Constant(5.1e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25917"),
                params={"resistance": Constant(6.8e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25744"),
                params={"resistance": Constant(10e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25752"),
                params={"resistance": Constant(12e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25771"),
                params={"resistance": Constant(27e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25741"),
                params={"resistance": Constant(100e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25782"),
                params={"resistance": Constant(390e3)},
            ),
            PickerOption(
                part=LCSC_Part(partno="C25790"),
                params={"resistance": Constant(470e3)},
            ),
        ],
    )


def pick_led(module: LED):
    pick_module_by_params(
        module,
        [
            PickerOption(
                part=LCSC_Part(partno="C965790"),
                params={
                    "color": Constant(LED.Color.RED),
                    "max_brightness": Constant(300e-3),
                    "forward_voltage": Constant(2.1),
                    "max_current": Constant(20e-3),
                },
                pinmap={"1": module.IFs.cathode, "2": module.IFs.anode},
            ),
            PickerOption(
                part=LCSC_Part(partno="C2286"),
                params={
                    "color": Constant(LED.Color.GREEN),
                    "max_brightness": Constant(285e-3),
                    "forward_voltage": Constant(3.7),
                    "max_current": Constant(100e-3),
                },
                pinmap={"1": module.IFs.cathode, "2": module.IFs.anode},
            ),
            PickerOption(
                part=LCSC_Part(partno="C72041"),
                params={
                    "color": Constant(LED.Color.BLUE),
                    "max_brightness": Constant(28.5e-3),
                    "forward_voltage": Constant(3.1),
                    "max_current": Constant(100e-3),
                },
                pinmap={"1": module.IFs.cathode, "2": module.IFs.anode},
            ),
        ],
    )


def pick_capacitor(module: Capacitor):
    """
    Link a partnumber/footprint to a Capacitor

    Uses 0402 when possible
    """

    pick_module_by_params(
        module,
        [
            PickerOption(
                part=LCSC_Part(partno="C1525"),
                params={
                    "temperature_coefficient": Constant(
                        Capacitor.TemperatureCoefficient.X7R,
                    ),
                    "capacitance": Constant(100e-9),
                    "rated_voltage": Constant(16),
                },
            ),
            PickerOption(
                part=LCSC_Part(partno="C19702"),
                params={
                    "temperature_coefficient": Constant(
                        Capacitor.TemperatureCoefficient.X5R,
                    ),
                    "capacitance": Constant(10e-6),
                    "rated_voltage": Constant(10),
                },
            ),
        ],
    )


def pick_fuse(module: Fuse):
    pick_module_by_params(
        module,
        [
            PickerOption(
                part=LCSC_Part(partno="C914087"),
                params={
                    "fuse_type": Constant(Fuse.FuseType.RESETTABLE),
                    "response_type": Constant(Fuse.ResponseType.SLOW),
                    "trip_current": Constant(1),
                },
            ),
            PickerOption(
                part=LCSC_Part(partno="C914085"),
                params={
                    "fuse_type": Constant(Fuse.FuseType.RESETTABLE),
                    "response_type": Constant(Fuse.ResponseType.SLOW),
                    "trip_current": Constant(0.5),
                },
            ),
        ],
    )


# ----------------------------------------------------------


def pick(module: Module) -> bool:
    # switch over all types of parts you want to assign real components to

    if isinstance(module, Resistor):
        pick_resistor(module)
    elif isinstance(module, LED):
        pick_led(module)
    elif isinstance(module, Capacitor):
        pick_capacitor(module)
    elif isinstance(module, Fuse):
        pick_fuse(module)
    elif isinstance(module, USB_Type_C_Receptacle_16_pin):
        pick_module_by_params(
            module,
            [
                PickerOption(
                    part=LCSC_Part(partno="C2765186"),
                    pinmap={
                        "1": module.IFs.gnd[0],
                        "2": module.IFs.vbus[0],
                        "3": module.IFs.sbu2,
                        "4": module.IFs.cc1,
                        "5": module.IFs.d2.IFs.n,
                        "6": module.IFs.d1.IFs.p,
                        "7": module.IFs.d1.IFs.n,
                        "8": module.IFs.d2.IFs.p,
                        "9": module.IFs.cc2,
                        "10": module.IFs.sbu1,
                        "11": module.IFs.vbus[3],
                        "12": module.IFs.gnd[3],
                        "13": module.IFs.shield,
                        "14": module.IFs.shield,
                    },
                ),
            ],
        )
    else:
        return False

    return True
