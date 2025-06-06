from setuptools import setup, find_packages

setup(
    name="posenet",
    version="0.1.0",
    description="PoseNet implementation for 6DoF visual localization",
    author="Your Name",
    author_email="your_email@example.com",
    packages=find_packages(),  # posenet, posenet.utils 포함
    include_package_data=True,
    install_requires=[
        "torch",
        "torchvision",
        "Pillow",
        "pandas",
        "opencv-python",
        "tqdm",
        "tensorboard",
        "torchmetrics",
        "matplotlib",
        "scipy"
    ],
    python_requires=">=3.7",
)