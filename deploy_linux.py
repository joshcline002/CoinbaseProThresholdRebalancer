import os
import subprocess
import sys


def main():
    path = os.path.dirname(os.path.realpath(__file__))
    lambdas = f"{path}/lambda"
    lambda_dirs = os.listdir(lambdas)
    for dir in lambda_dirs:
        destination = f'{lambdas}/{dir}'
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", f'{destination}/requirement.txt', f'--target={destination}'])
    print("complete")


main()
