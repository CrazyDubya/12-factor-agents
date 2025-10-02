from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh.readlines() if line.strip() and not line.startswith("#")]

setup(
    name="finetune-narrative",
    version="0.1.0",
    author="Finetune Research Team",
    author_email="research@finetune.ai",
    description="Synthetic narrative finetuning system for coherent worldbuilding",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/finetune-research/narrative-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "finetune-generate=finetune.cli:main",
            "finetune-train=finetune.training.cli:main",
            "finetune-evaluate=finetune.evaluation.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "finetune": [
            "data_generation/prompt_templates/*.json",
            "finetuning/model_configs/*.yaml",
        ],
    },
)