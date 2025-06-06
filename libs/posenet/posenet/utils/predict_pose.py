import torch
from torchvision import transforms
from PIL import Image
from ..model import PoseNet

def load_model(model_path):
    model = PoseNet()
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

def predict(model, image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(image)

    pose = output.squeeze().tolist()
    return tuple(pose)