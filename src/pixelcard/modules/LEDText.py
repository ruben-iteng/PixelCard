from pathlib import Path
from typing import Tuple

from faebryk.core.core import Module
from faebryk.exporters.pcb.layout.absolute import LayoutAbsolute
from faebryk.exporters.pcb.layout.font import FontLayout
from faebryk.exporters.pcb.layout.typehierarchy import LayoutTypeHierarchy
from faebryk.library.Constant import Constant
from faebryk.library.ElectricPower import ElectricPower
from faebryk.library.has_pcb_layout_defined import has_pcb_layout_defined
from faebryk.library.has_pcb_position import has_pcb_position
from faebryk.library.has_pcb_routing_strategy_greedy_direct_line import (
    has_pcb_routing_strategy_greedy_direct_line,
)
from faebryk.library.LED import LED
from faebryk.library.PoweredLED import PoweredLED
from faebryk.library.Resistor import Resistor
from faebryk.libs.brightness import TypicalLuminousIntensity
from faebryk.libs.font import Font
from faebryk.libs.util import times


class LEDText(Module):
    def __init__(
        self,
        text: str,
        char_dimensions: Tuple[float, float],
        font: Font,
    ) -> None:
        super().__init__()

        led_layout = FontLayout(
            font=Font(Path("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf")),
            text=text,
            char_dimensions=char_dimensions,
            resolution=(0.33, 0.35),
            # bbox=(10, 14),
            kerning=5,
        )

        num_leds = led_layout.get_count()

        class _IFs(Module.IFS()):
            power = ElectricPower()

        self.IFs = _IFs(self)

        class _NODES(Module.NODES()):
            leds = times(
                num_leds,
                PoweredLED,
            )

        self.NODEs = _NODES(self)

        class _PARAMs(Module.PARAMS()):
            width = Constant(char_dimensions[0] * len(text))
            height = Constant(char_dimensions[1])

        self.PARAMs = _PARAMs(self)

        for led in self.NODEs.leds:
            # TODO reenable
            # led.IFs.power.connect(self.IFs.power)
            # Parametrize
            led.NODEs.led.PARAMs.color.merge(LED.Color.RED)
            led.NODEs.led.PARAMs.brightness.merge(
                TypicalLuminousIntensity.APPLICATION_LED_INDICATOR_INSIDE.value.value
            )

        # Resistor relative to LED layout
        for led in self.NODEs.leds:
            led.add_trait(
                has_pcb_layout_defined(
                    LayoutTypeHierarchy(
                        layouts=[
                            LayoutTypeHierarchy.Level(
                                mod_type=LED,
                                layout=LayoutAbsolute(
                                    has_pcb_position.Point(
                                        (0, 0, 90, has_pcb_position.layer_type.NONE)
                                    )
                                ),
                            ),
                            LayoutTypeHierarchy.Level(
                                mod_type=Resistor,
                                layout=LayoutAbsolute(
                                    has_pcb_position.Point(
                                        (
                                            1.1,
                                            -0.25,
                                            -90,
                                            has_pcb_position.layer_type.NONE,
                                        )
                                    )
                                ),
                            ),
                        ]
                    )
                )
            )

            led.add_trait(has_pcb_routing_strategy_greedy_direct_line())

        led_layout.apply(*self.NODEs.leds)
