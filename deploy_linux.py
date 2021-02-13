import os
import shutil
import subprocess
import sys

path = os.path.dirname(os.path.realpath(__file__))
lambda_dir = 'CoinbaseTrader'
print("Before copying file:")
print(os.listdir(path))

src = f'{path}/{lambda_dir}'
dest = f'{path}/{lambda_dir}_deploy'
destination = shutil.copytree(src, dest)
print("After copying file:")
print(os.listdir(path))

print("Destination path:", destination)

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", f'{destination}/requirement.txt', f'--target={destination}'])

shutil.rmtree(dest)
