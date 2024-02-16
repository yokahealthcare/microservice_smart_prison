import torch
import torch.nn as nn

from fight_module.util import *


# Define the neural network model
class ThreeLayerClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(ThreeLayerClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc3(x)
        x = self.sigmoid(x)
        return x


class FightDetector:
    def __init__(self, fight_model):
        # Architect the deep learning structure
        self.input_size = 16
        self.hidden_size = 8
        self.output_size = 1
        self.model = ThreeLayerClassifier(self.input_size, self.hidden_size, self.output_size)
        self.model.load_state_dict(torch.load(fight_model))
        self.model.eval()  # Set to evaluation mode

        # Coordinate for angel
        self.coordinate_for_angel = [
            [8, 6, 2],
            [11, 5, 7],
            [6, 8, 10],
            [5, 7, 9],
            [6, 12, 14],
            [5, 11, 13],
            [12, 14, 16],
            [11, 13, 15]
        ]

        """
            LAYER OF CORRECT PREDICTION
            1. MODEL_THRESHOLD          : Dictate how deep learning is sure there is fight on that frame
            2. CONCLUSION_THRESHOLD     : Dictate how hard the program conclude if a person is in fight action (2 - 4)                            
            3. FINAL_THRESHOLD          : Dictate how many correct fight detected is allowed for the bell to ring
        """

        # Set up the thresholds
        self.model_threshold = 0.9
        self.conclusion_threshold = 2
        self.final_threshold = 20

        # Event variables
        self.fight_detected = 0
        self.smoothing_factor = 0.5

    def detect(self, conf, xyn):
        input_list = []
        keypoint_unseen = False
        for n in self.coordinate_for_angel:
            # Keypoint number that we want to make new angel
            first, mid, end = n[0], n[1], n[2]

            # Gather the coordinate with keypoint number
            c1, c2, c3 = xyn[first], xyn[mid], xyn[end]
            # Check if all three coordinate of one key points is all zeros
            if is_coordinate_zero(c1, c2, c2):
                keypoint_unseen = True
                break
            else:
                # Getting angel from three coordinate
                input_list.append(calculate_angle(c1, c2, c3))
                # Getting the confs mean of three of those coordinate
                conf1, conf2, conf3 = conf[first], conf[mid], conf[end]
                input_list.append((conf1 + conf2 + conf3)/3)

        if keypoint_unseen:
            return None

        # Make a prediction
        prediction = self.model(torch.Tensor(input_list))
        print(f"PREDICTION : {prediction.item()}")
        # Update fight detection using exponential smoothing
        if prediction.item() > self.model_threshold:
            # If fight is detected, increase the fight counter
            self.fight_detected += 1
        else:
            # If no fight is detected, decrease the fight counter using exponential smoothing
            self.fight_detected = self.smoothing_factor * 1 + (1 - self.smoothing_factor) * self.fight_detected

        # Threshold for concluding a fight
        if self.fight_detected > self.final_threshold:
            return True
        else:
            return False
