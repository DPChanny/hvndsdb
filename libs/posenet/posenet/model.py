import torch.nn as nn
from torchvision.models import googlenet, GoogLeNet_Weights


class PoseNet(nn.Module):
    def __init__(self):
        super(PoseNet, self).__init__()
        weights = GoogLeNet_Weights.IMAGENET1K_V1
        base_model = googlenet(weights=weights)
        self.feature_extractor = nn.Sequential(
            *list(base_model.children())[:-1]
        )
        self.fc_pose = nn.Linear(1024, 7)

    def forward(self, x):
        x = self.feature_extractor(x).view(x.size(0), -1)
        pose = self.fc_pose(x)
        return pose
