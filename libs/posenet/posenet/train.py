import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms

from .model import PoseNet
from .dataset import PoseDataset
from .posenet_checkpoint import save_checkpoint, load_checkpoint

def train_model(images_txt_path, frames_root, output_path, epochs=20,
                checkpoint_path=None, resume=False, save_checkpoints=[]):
    batch_size = 32
    learning_rate = 1e-4
    lambda_pos = 1.0
    lambda_ori = 100.0

    dataset = PoseDataset(images_txt_path, frames_root, transform=transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ]))
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = PoseNet()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    start_epoch = 0

    if resume and checkpoint_path and os.path.exists(checkpoint_path):
        model, optimizer, start_epoch = load_checkpoint(model, optimizer, checkpoint_path)
        print(f"Resumed from checkpoint at epoch {start_epoch}")

    model.train()
    for epoch in range(start_epoch, epochs):
        total_loss = 0
        for images, poses in dataloader:
            images, poses = images.to(device), poses.to(device)
            preds = model(images)
            pos_loss = nn.functional.mse_loss(preds[:, :3], poses[:, :3])
            ori_loss = nn.functional.mse_loss(preds[:, 3:], poses[:, 3:])
            loss = lambda_pos * pos_loss + lambda_ori * ori_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch + 1}, Loss: {total_loss / len(dataloader):.4f}")

        if (epoch + 1) in save_checkpoints:
            chkpnt_name = f"chkpnt{epoch + 1}.pth"
            chkpnt_path = os.path.join(output_path, chkpnt_name)
            save_checkpoint(model, optimizer, epoch + 1, loss.item(), chkpnt_path)

    model_save_path = os.path.join(output_path, 'model.pth')
    torch.save(model.state_dict(), model_save_path)
    print(f"Final model saved to: {model_save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train PoseNet with optional checkpointing")
    parser.add_argument('--images_txt_path', required=True, help="Path to COLMAP's images.txt")
    parser.add_argument('--frames_root', required=True, help="Path to directory with image files")
    parser.add_argument('--output_path', required=True, help="Path to save trained model")
    parser.add_argument('--epochs', type=int, default=20, help="Number of training epochs")
    parser.add_argument('--checkpoint_path', default=None, help="Path to save/load checkpoint")
    parser.add_argument('--resume', action='store_true', help="Resume training from checkpoint if available")
    parser.add_argument('--save_checkpoints', nargs='*', type=int, default=[], help="Epochs to save checkpoints")
    args = parser.parse_args()

    train_model(
        args.images_txt_path,
        args.frames_root,
        args.output_path,
        args.epochs,
        args.checkpoint_path,
        args.resume,
        args.save_checkpoints
    )