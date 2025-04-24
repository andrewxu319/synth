import logging
import numpy as np

from .... import settings
from ....ui.main_window import MainWindow

def set_parameter(window: MainWindow, path: str, value, oscillator_count_range: int):
    log = logging.getLogger(__name__)
    log.info(f"Received set parameter request, path {path}, value {value}")
    
    match path:
        case ["oscillators", *sublevels, i]:
            osc = window.osc_tab.osc_list[i]
            
            match sublevels:
                case ["active"]:
                    osc.active_checkbox.setChecked(True) # unsure why but need to first setChecked(True) otherwise stateChanged wont trigger if checking false
                    osc.active_checkbox.setChecked(value)
                case ["oscillator_gain"]:
                    osc.gain_dial.setValue(find_nearest(settings.amp_values, value))
                case ["hpf_active"]:
                    pass
                case ["hpf_cutoff"]:
                    osc.hpf_cutoff_dial.setValue(find_nearest(settings.filter_cutoff_values, value))
                case ["hpf_wet"]:
                    osc.hpf_wet_dial.setValue(find_nearest(settings.filter_wet_values, value))
                case ["lpf_active"]:
                    pass
                case ["lpf_cutoff"]:
                    osc.lpf_cutoff_dial.setValue(find_nearest(settings.filter_cutoff_values, value))
                case ["lpf_wet"]:
                    osc.lpf_wet_dial.setValue(find_nearest(settings.filter_wet_values, value))
                case _:
                    log.warning(f"Attempted to change nonexistent parameter {sublevels} in oscillators!")

        case ["fx", *sublevels]:
            match sublevels:
                case ["delay", *sublevels]:
                    delay = window.fx_tab.delay_fx
                    match sublevels:
                        case ["active"]:
                            delay.active_checkbox.setChecked(value)
                        case ["time"]:
                            delay.delay_time_dial.setValue(find_nearest(settings.delay_time_values, value))
                        case ["feedback"]:
                            delay.delay_feedback_dial.setValue(find_nearest(settings.delay_feedback_values, value))
                        case ["wet"]:
                            delay.delay_wet_dial.setValue(find_nearest(settings.delay_wet_values, value))
                        case _:
                            log.warning(f"Attempted to change nonexistent parameter {sublevels} in fx -> delay!")
                
                case _:
                    log.warning(f"Attempted to change nonexistent parameter {sublevels} in fx!")

        case ["modulators", *sublevels]:
            match sublevels:
                case ["envelope", *sublevels, i]:
                    envelope = window.osc_tab.envelope_section # make it numbered later
                    match sublevels:
                        case ["attack"]:
                            envelope.attack_dial.setValue(find_nearest(settings.envelope_attack_values, value))
                        case ["decay"]:
                            envelope.decay_dial.setValue(find_nearest(settings.envelope_decay_values, value))
                        case ["sustain"]:
                            envelope.sustain_dial.setValue(find_nearest(settings.envelope_sustain_values, value))
                        case ["release"]:
                            envelope.release_dial.setValue(find_nearest(settings.envelope_release_values, value))
                        case _:
                            log.warning(f"Attempted to change nonexistent parameter {sublevels} in modulators -> envelope!")

                case _:
                    log.warning(f"Attempted to change nonexistent parameter {sublevels} in modulators!")

        case ["performance", *sublevels]:
            performance = window.osc_tab.performance_section

            match sublevels:
                case ["velocity_sensitivity"]:
                    performance.velocity_sensitivity_dial.setValue(value)
                
                case _:
                    log.warning(f"Attempted to change nonexistent parameter {sublevels} in performance!")

def find_nearest(values_array, value):
    values_array = np.asarray(values_array)
    index = (np.abs(values_array - value)).argmin()
    return index