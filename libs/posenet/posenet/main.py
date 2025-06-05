import argparse
from .utils.colmap_csv_converter import convert_colmap_to_csv
import subprocess
import os

def main(args):
    print("Convert COLMAP data to CSV")
    csv_path = convert_colmap_to_csv(args.colmap_root, args.frames_root)

    print("Train PoseNet model")
    train_cmd = [
        "python", "train.py",
        "--csv_path", csv_path,
        "--output_path", args.project_root,
        "--checkpoint_path", os.path.join(args.project_root, "checkpoint.pth")
    ]
    if args.resume:
        train_cmd.append("--resume")

    subprocess.run(train_cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PoseNet Training Pipeline")
    parser.add_argument('--colmap_root', required=True, help="Path to extracted COLMAP directory (with sparse/0/txts/images.txt)")
    parser.add_argument('--frames_root', required=True, help="Path to images folder")
    parser.add_argument('--project_root', default='/content/project')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    
    main(args)
