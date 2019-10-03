from setuptools import setup, find_packages

setup(name="tetrispace",
      version="1.0",
      description="Multiplayer tetromino game engine",
      author="Sebastian Psm",
      install_requires=["flask", "numpy", "pytest"],
      packages=find_packages())