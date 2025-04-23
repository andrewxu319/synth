import logging
import numpy as np

from ....ui.main_window import MainWindow

def set_parameter(window: MainWindow, parameter: str, value, oscillator_count_range: int):
    log = logging.getLogger(__name__)
    
    match parameter:
        case ["oscillators", *sublevels, i]:
            osc = window.osc_tab.osc_list[i]
            
            match sublevels:
                case ["active"]:
                    osc.active_checkbox.setChecked(True) # unsure why but need to first setChecked(True) otherwise stateChanged wont trigger if checking false
                    osc.active_checkbox.setChecked(value)
                case ["oscillator_gain"]:
                    osc.gain_dial.setValue(value)
                case ["hpf_active"]:
                    pass
                case ["hpf_cutoff"]:
                    osc.hpf_cutoff_dial.setValue(value)
                case ["hpf_wet"]:
                    osc.hpf_wet_dial.setValue(value)
                case ["lpf_active"]:
                    pass
                case ["lpf_cutoff"]:
                    osc.lpf_cutoff_dial.setValue(value)
                case ["lpf_wet"]:
                    osc.lpf_wet_dial.setValue(value)
                case _:
                    self.log.warning(f"Attempted to change nonexistent parameter {_} in oscillators!")

        case ["fx", *sublevels]:
            match sublevels:
                case ["delay", *sublevels]:
                    delay = window.fx_tab.delay_fx
                    match sublevels:
                        case ["active"]:
                            delay.active_checkbox.setChecked(value)
                        case ["time"]:
                            delay.delay_time_dial.setValue(value)
                        case ["feedback"]:
                            delay.delay_feedback_dial.setValue(value)
                        case ["wet"]:
                            delay.delay_wet_dial.setValue(value)
                        case _:
                            self.log.warning(f"Attempted to change nonexistent parameter {_} in fx -> delay!")
                
                case _:
                    self.log.warning(f"Attempted to change nonexistent parameter {_} in fx!")

        case ["modulators", *sublevels]:
            match sublevels:
                case []


        envelope = window.osc_tab.envelope_section
        envelope.attack_dial.setValue(value)
        envelope.decay_dial.setValue(value)
        envelope.sustain_dial.setValue(value)
        envelope.release_dial.setValue(value)

        # Performance
        performance = window.osc_tab.performance_section
        performance.velocity_sensitivity_dial.setValue(value)

# LATER: call set_parameter in preset_handler. make it call it for each parameter