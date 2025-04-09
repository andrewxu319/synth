import logging
import json
import numpy as np

from ..synthesis.signal.gain import Gain
from ..synthesis.signal.fx.delay import Delay

class PresetHandler:
    def __init__(self, synthesizer):
        self.log = logging.getLogger(__name__)
        self.synthesizer = synthesizer
        self.file_path = ""
        self.oscillator_count_range = range(len(self.synthesizer.voices[0].signal_chain.get_components_by_class(Gain))) # maybe clean this up later

    def find_nearest(self, array, value):
        array = np.asarray(array)
        index = (np.abs(array - value)).argmin()
        return index
    
    def save(self, file_path, window):
        self.file_path = file_path

        chain = self.synthesizer.voices[0].signal_chain
        delay = chain.get_components_by_class(Delay)[0]

        parameters = {
            "oscillators": {
                "actives": [chain.get_components_by_control_tag(f"gain_{i}")[0].subcomponents[0].active for i in self.oscillator_count_range],
                "gains": [chain.get_components_by_control_tag(f"gain_{i}")[0].amplitude for i in self.oscillator_count_range],
                "hpf_actives": [chain.get_components_by_control_tag(f"hpf_{i}")[0].active for i in self.oscillator_count_range],
                "hpf_cutoffs": [chain.get_components_by_control_tag(f"hpf_{i}")[0].cutoff for i in self.oscillator_count_range],
                "hpf_wets": [chain.get_components_by_control_tag(f"hpf_{i}")[0].wet for i in self.oscillator_count_range],
                "lpf_actives": [chain.get_components_by_control_tag(f"lpf_{i}")[0].active for i in self.oscillator_count_range],
                "lpf_cutoffs": [chain.get_components_by_control_tag(f"lpf_{i}")[0].cutoff for i in self.oscillator_count_range],
                "lpf_wets": [chain.get_components_by_control_tag(f"lpf_{i}")[0].wet for i in self.oscillator_count_range],
            },
            "fx": {
                "delay": {
                    "active": delay.active,
                    "time": delay.delay_time,
                    "feedback": delay.feedback,
                    "wet": delay.wet
                }
            }
        }

        with open(file_path, "w") as file:
            file.write(json.dumps(parameters, indent=4))
        
        window.setWindowTitle(f"{file_path.split("/")[-1].split(".")[-2]} - Synth")
    
    def load(self, file_path, window):
        with open(file_path, "r") as file:
            dictionary = json.load(file)
        
        # Oscillators
        for i in self.oscillator_count_range:
            osc = window.osc_tab.osc_list[i]
            osc.active_checkbox.setChecked(dictionary["oscillators"]["actives"][i])
            osc.gain_dial.setValue(self.find_nearest(self.synthesizer.amp_values, dictionary["oscillators"]["gains"][i]))
            osc.hpf_cutoff_dial.setValue(self.find_nearest(self.synthesizer.filter_cutoff_values, dictionary["oscillators"]["hpf_cutoffs"][i]))
            osc.hpf_wet_dial.setValue(self.find_nearest(self.synthesizer.filter_wet_values, dictionary["oscillators"]["hpf_wets"][i]))
            osc.lpf_cutoff_dial.setValue(self.find_nearest(self.synthesizer.filter_cutoff_values, dictionary["oscillators"]["lpf_cutoffs"][i]))
            osc.lpf_wet_dial.setValue(self.find_nearest(self.synthesizer.filter_wet_values, dictionary["oscillators"]["lpf_wets"][i]))

        # FX
        delay = window.fx_tab.delay_fx
        delay.active_checkbox.setChecked(dictionary["fx"]["delay"]["active"])
        delay.delay_time_dial.setValue(self.find_nearest(self.synthesizer.delay_time_values, dictionary["fx"]["delay"]["time"]))
        delay.delay_feedback_dial.setValue(self.find_nearest(self.synthesizer.delay_feedback_values, dictionary["fx"]["delay"]["feedback"]))
        delay.delay_wet_dial.setValue(self.find_nearest(self.synthesizer.delay_wet_values, dictionary["fx"]["delay"]["wet"]))

        # Cleanup
        window.setWindowTitle(f"{file_path.split("/")[-1].split(".")[-2]} - Synth")

        self.log.info(f"Successfully loaded preset {file_path}!")



# import pickle

# from ..synthesizer import 

# class PresetHandler:
#     def __init__(self, save_folder):
#         self.save_folder = save_folder
    
#     def get_data(self, synthesizer):
#         i
    
#     def save(self, synthesizer, name):
#         file_path = f"{self.save_folder}/{name}.json"
#         with open(file_path, "wb") as file:
#             pickle.dump(self.get_data(synthesizer), file)
    
#     def load(self, name):
#         with open(f"{self.save_folder}/{name}.json", "rb") as file:
#             data = pickle.load(file)