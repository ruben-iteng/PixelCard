from faebryk.core.core import Module
from faebryk.exporters.pcb.layout.absolute import LayoutAbsolute
from faebryk.exporters.pcb.layout.font import FontLayout
from faebryk.exporters.pcb.layout.typehierarchy import LayoutTypeHierarchy
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
        font: Font,
        font_size: float,
        bbox: tuple[float, float] | None = None,
        scale_to_fit: bool = False,
    ) -> None:
        super().__init__()

        led_layout = FontLayout(
            font=font,
            text=text,
            font_size=font_size,
            density=0.13,
            bbox=bbox,
            scale_to_fit=scale_to_fit,
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

        class _PARAMs(Module.PARAMS()): ...

        self.PARAMs = _PARAMs(self)

        for led in self.NODEs.leds:
            led.IFs.power.connect(self.IFs.power)
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
