import torch
from torch.utils.data import Dataset
from PIL import Image
import os

class PoseDataset(Dataset):
    def __init__(self, images_txt_path, image_dir, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        self.data = self._parse_images_txt(images_txt_path)

    def _parse_images_txt(self, path):
        entries = []
        with open(path, 'r') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('#') or line == '':
                i += 1
                continue

            vals = line.split()
            if len(vals) >= 10:
                image_id, qw, qx, qy, qz, tx, ty, tz, camera_id, image_name = vals[:11]
                entries.append([
                    image_name,
                    float(tx), float(ty), float(tz),
                    float(qx), float(qy), float(qz), float(qw)
                ])
                i += 2
            else:
                i += 1
        return entries

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        entry = self.data[idx]
        image_path = os.path.join(self.image_dir, entry[0])
        image = Image.open(image_path).convert('RGB')

        pose = torch.tensor(entry[1:], dtype=torch.float32)

        if self.transform:
            image = self.transform(image)

        return image, pose