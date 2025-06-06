import argparse
import subprocess
import os

def main(args):
    print("Convert COLMAP data to CSV")
    images_txt_path = os.path.join(args.colmap_root, "sparse", "0", "txts", "images.txt")

    if not os.path.exists(images_txt_path):
        raise FileNotFoundError(f"[ERROR] images.txt not found at: {images_txt_path}")
    
    posenet_output_dir = os.path.join(args.output_path, "posenet")
    os.makedirs(posenet_output_dir, exist_ok=True)

    print("Train PoseNet model")
    train_cmd = [
        "python", "train.py",
        "--images_txt_path", images_txt_path,
        "--frames_root", args.frames_root,
        "--output_path", posenet_output_dir,
        "--checkpoint_path", os.path.join(posenet_output_dir, "checkpoint.pth"),
        "--epochs", str(args.epochs)
    ]

    if args.resume:
        train_cmd.append("--resume")
    if args.save_checkpoints:
        train_cmd.extend(["--save_checkpoints"] + list(map(str, args.save_checkpoints)))

    subprocess.run(train_cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PoseNet Training Pipeline")
    parser.add_argument('--colmap_root', required=True, help="Path to extracted COLMAP directory")
    parser.add_argument('--frames_root', required=True, help="Path to images folder")
    parser.add_argument('--output_path', required=True, help="Root directory to save model and checkpoints")
    parser.add_argument('--epochs', type=int, default=20, help="Number of training epochs")
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--save_checkpoints', nargs='*', type=int, default=[], help="Epochs to save checkpoints")
    args = parser.parse_args()
    main(args)