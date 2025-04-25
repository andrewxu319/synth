import logging
import json
import numpy as np
from time import sleep

# from ..synthesis.signal.modulators.set_parameter import set_parameter
from .. import settings
from ..synthesis.signal.oscillator import Oscillator
from ..synthesis.signal.fx.gain import OscillatorGain, VelocityGain
from ..synthesis.signal.modulators.envelope import Envelope
from ..synthesis.signal.fx.delay import Delay

class PresetHandler:
    def __init__(self, synthesizer):
        self.log = logging.getLogger(__name__)
        self.synthesizer = synthesizer
        self.file_path = ""
        self.oscillator_count_range = range(len(self.synthesizer.voices[0].signal_chain.get_components_by_class(Oscillator))) # maybe clean this up later

    def save(self, file_path):
        self.file_path = file_path
        if file_path.split(".")[-1] != "json":
            self.log.error(f"Save path must be json! Entered the following: {file_path}")

        chain = self.synthesizer.voices[0].signal_chain
        envelope = chain.get_components_by_class(Envelope)[0]
        delay = chain.get_components_by_class(Delay)[0]
        parameters = {
            "oscillators": {
                "active": [chain.get_components_by_control_tag(f"osc_{i}")[0].active for i in self.oscillator_count_range],
                "oscillator_gain": [chain.get_components_by_control_tag(f"oscillator_gain_{i}")[0].amplitude for i in self.oscillator_count_range],
                "hpf_active": [chain.get_components_by_control_tag(f"hpf_{i}")[0].active for i in self.oscillator_count_range],
                "hpf_cutoff": [chain.get_components_by_control_tag(f"hpf_{i}")[0].cutoff for i in self.oscillator_count_range],
                "hpf_wet": [chain.get_components_by_control_tag(f"hpf_{i}")[0].wet for i in self.oscillator_count_range],
                "lpf_active": [chain.get_components_by_control_tag(f"lpf_{i}")[0].active for i in self.oscillator_count_range],
                "lpf_cutoff": [chain.get_components_by_control_tag(f"lpf_{i}")[0].cutoff for i in self.oscillator_count_range],
                "lpf_wet": [chain.get_components_by_control_tag(f"lpf_{i}")[0].wet for i in self.oscillator_count_range]
            },
            "fx": {
                "delay": {
                    "active": delay.active,
                    "time": delay.delay_time,
                    "feedback": delay.feedback,
                    "wet": delay.wet
                }
            },
            "modulators": {
                "envelope": {
                    "attack": [float(envelope.attack)], # multiple envelopes in the future
                    "decay": [float(envelope.decay)],
                    "sustain": [float(envelope.sustain)],
                    "release": [float(envelope.release)]
                }
            },
            "performance": {
                "velocity_sensitivity": chain.get_components_by_class(VelocityGain)[0].velocity_sensitivity
            }
        }

        with open(file_path, "w") as file:
            file.write(json.dumps(parameters, indent=4))

    # def get_parameter_path(self, dictionary, path, path_list):
    #     for key in dictionary.keys():
    #         if isinstance(dictionary[key], dict):
    #             child_path = path.copy()
    #             child_path.append(key)
    #             self.get_parameter_path(dictionary[key], child_path, path_list)
    #         elif isinstance(dictionary[key], list):
    #             for i in range(len(dictionary[key])):
    #                 child_path = path.copy()
    #                 child_path.append(key)
    #                 child_path.append(i)
    #                 path_list.append(child_path)
    #         else:
    #             child_path = path.copy()
    #             child_path.append(key)
    #             path_list.append(child_path)

    # def get_parameter_value(self, dictionary, path):
    #     dictionary_copy = dictionary.copy()
    #     for key in path:
    #         dictionary = dictionary[key]
    #     return dictionary

    def load(self, file_path, window):
        with open(file_path, "r") as file:
            dictionary = json.load(file)
        
        try:
            # path_list = []
            # self.get_parameter_path(dictionary, [], path_list)
            # print(f"tagtag + {path_list}")
            # for path in path_list:
            #     set_parameter(window, path, self.get_parameter_value(dictionary, path), self.oscillator_count_range)

            # Oscillators
            for i in self.oscillator_count_range:
                osc = window.osc_tab.osc_list[i]
                # osc.active_checkbox.setChecked(True) # unsure why but need to first setChecked(True) otherwise stateChanged wont trigger if checking false
                osc.active_checkbox.setChecked(dictionary["oscillators"]["active"][i])
                osc.gain_dial.setValue(self.find_nearest(settings.amp_values, dictionary["oscillators"]["oscillator_gain"][i]))
                osc.hpf_cutoff_dial.setValue(self.find_nearest(settings.filter_cutoff_values, dictionary["oscillators"]["hpf_cutoff"][i]))
                osc.hpf_wet_dial.setValue(self.find_nearest(settings.filter_wet_values, dictionary["oscillators"]["hpf_wet"][i]))
                osc.lpf_cutoff_dial.setValue(self.find_nearest(settings.filter_cutoff_values, dictionary["oscillators"]["lpf_cutoff"][i]))
                osc.lpf_wet_dial.setValue(self.find_nearest(settings.filter_wet_values, dictionary["oscillators"]["lpf_wet"][i]))

            # FX
            delay = window.fx_tab.delay_fx
            delay.active_checkbox.setChecked(dictionary["fx"]["delay"]["active"])
            delay.delay_time_dial.setValue(self.find_nearest(settings.delay_time_values, dictionary["fx"]["delay"]["time"]))
            delay.delay_feedback_dial.setValue(self.find_nearest(settings.delay_feedback_values, dictionary["fx"]["delay"]["feedback"]))
            delay.delay_wet_dial.setValue(self.find_nearest(settings.delay_wet_values, dictionary["fx"]["delay"]["wet"]))

            # Modulators
            envelope = window.osc_tab.envelope_section

            envelope.attack_dial.setValue(self.find_nearest(settings.envelope_attack_values, dictionary["modulators"]["envelope"]["attack"]))
            envelope.decay_dial.setValue(self.find_nearest(settings.envelope_decay_values, dictionary["modulators"]["envelope"]["decay"]))
            envelope.sustain_dial.setValue(self.find_nearest(settings.envelope_sustain_values, dictionary["modulators"]["envelope"]["sustain"]))
            envelope.release_dial.setValue(self.find_nearest(settings.envelope_release_values, dictionary["modulators"]["envelope"]["release"]))

            # Performance
            performance = window.osc_tab.performance_section
            performance.velocity_sensitivity_dial.setValue(dictionary["performance"]["velocity_sensitivity"])
        
        except KeyError as e:
            self.save(file_path)
            self.log.info(f"{str(e)} setting not found in {file_path}. Default setting has been added to save file.")
            self.load(file_path, window)

        # Cleanup
        self.log.info(f"Successfully loaded preset {file_path}!")

    def autosave(self):
        self.save("presets/autosave.json") # Save to autosave even if an active file is open---they can resave into their file if desired
        
        self.log.info("Autosaved!")
    
    def find_nearest(self, values_array, value):
        values_array = np.asarray(values_array)
        index = (np.abs(values_array - value)).argmin()
        return index



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