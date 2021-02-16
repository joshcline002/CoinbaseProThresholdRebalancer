import os
import subprocess
import sys

path = os.path.dirname(os.path.realpath(__file__))
lambdas = f"{path}/{lambda_dir}"
lambda_dirs = os.listdir(lambdas))
for dir in lambda_dirs:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", f'{destination}/requirement.txt', f'--target={destination}'])
