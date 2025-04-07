import json

from ..synthesis.signal.gain import Gain
from ..synthesis.signal.fx.delay import Delay

class PresetHandler:
    def __init__(self, synthesizer, save_folder):
        self.synthesizer = synthesizer
        self.save_folder = save_folder
        self.parameters = self.get_parameters()
    
    def get_parameters(self):
        chain = self.synthesizer.voices[0].signal_chain
        oscillator_count = range(len(chain.get_components_by_class(Gain)))
        delay = chain.get_components_by_class(Delay)[0]

        parameters = {
            "oscillators": {
                "actives": [chain.get_components_by_control_tag(f"gain_{i}")[0].subcomponents[0].active for i in oscillator_count],
                "amplitudes": [chain.get_components_by_control_tag(f"gain_{i}")[0].amplitude for i in oscillator_count],
                "hpf_actives": [chain.get_components_by_control_tag(f"hpf_{i}")[0].active for i in oscillator_count],
                "hpf_cutoffs": [chain.get_components_by_control_tag(f"hpf_{i}")[0].cutoff for i in oscillator_count],
                "lpf_actives": [chain.get_components_by_control_tag(f"lpf_{i}")[0].active for i in oscillator_count],
                "lpf_cutoffs": [chain.get_components_by_control_tag(f"lpf_{i}")[0].cutoff for i in oscillator_count],
            },
            "fx": {
                "delay_active": delay.active,
                "delay_time": delay.delay_time,
                "delay_feedback": delay.feedback,
                "delay_wet": delay.wet
            }
        }
        
        return parameters
    
    def get_references(self):
        references = {"hi": self.synthesizer}

    def save(self, name):
        file_path = f"{self.save_folder}/{name}.json"
        with open(file_path, "w") as file:
            file.write(json.dumps(self.parameters, indent=4))
    
    def load(self, name):
        with open(f"{self.save_folder}/{name}.json", "r") as file:
            dictionary = json.load(file)
        return dictionary

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