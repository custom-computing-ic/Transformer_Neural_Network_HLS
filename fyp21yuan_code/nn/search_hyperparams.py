import argparse
import os
from subprocess import check_call
import sys

import utils

PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN = os.path.join(BASE_DIR, 'nn/train.py')

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', default=os.path.join(BASE_DIR, 'data/processed'),
                    help="Directory containing the dataset")
parser.add_argument('--parent_dir', default=os.path.join(BASE_DIR,'experiments/constituent_perceiver_depth'),
                    help="Directory containing params.json")


def launch_training_job(parent_dir, data_dir, job_name, params):
    """Launch training of the model with a set of hyperparameters in parent_dir/job_name
    Args:
        model_dir: (string) directory containing config, weights and log
        data_dir: (string) directory containing the dataset
        params: (dict) containing hyperparameters
    """

    print(job_name)
    # Create a new folder in parent_dir with unique_name "job_name"
    model_dir = os.path.join(parent_dir, job_name)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # Write parameters in json file
    json_path = os.path.join(model_dir, 'params.json')
    params.save(json_path)

    # Launch training with this config
    cmd = f"{PYTHON} {TRAIN} --model_dir={model_dir} --data_dir {data_dir}"
    print(cmd)
    check_call(cmd, shell=True)


if __name__ == "__main__":
    # Load the "reference" parameters from parent_dir json file
    args = parser.parse_args()
    json_path = os.path.join(args.parent_dir, 'params.json')
    assert os.path.isfile(json_path), "No json configuration file found at {}".format(json_path)
    params = utils.Params(json_path)

    # Perform hypersearch over one parameter
    num_perceivers = [3]

    for num in num_perceivers:
        # Modify the relevant parameter in params
        params.num_perceivers = num

        # Launch job (name has to be unique)
        job_name = "num_perceivers_{}".format(num)
        launch_training_job(args.parent_dir, args.data_dir, job_name, params)