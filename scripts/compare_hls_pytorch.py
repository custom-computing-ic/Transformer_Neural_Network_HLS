import os
import sys
import subprocess
import argparse
import re
import pickle
import numpy as np
import matplotlib.pyplot as plt

from os import fdopen, remove
from tempfile import mkstemp
from shutil import move, copymode
from time import time
from datetime import datetime
from typing import Dict
from itertools import product
from colorama import Fore, Style

def run_vivado_hls(hls_dir_path, build_tcl_path, quiet=True):
  hls_command = 'vivado_hls -f ' + build_tcl_path

  if quiet:
    result = subprocess.run(hls_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, cwd=hls_dir_path)

  else:
    print('Running Vivado HLS, this might take a while...')

    start_time = time()
    result = subprocess.run(hls_command, shell=True, cwd=hls_dir_path)
    end_time = time()

    print(f'Running Vivado HLS took {(end_time - start_time) / 3600:.3f} h')

  if result.returncode != 0:
    raise RuntimeError(f'{hls_command} returned {result.returncode}')


def run_pytorch(script_path, update_path):
  # script_command = f'python3 {script_path} --only_predictions | tail -n 1'
  script_command = f'python3 {script_path} --generate_hls_tb --use_cpu --particles 1'

  start_time = time()
  # result = subprocess.run(script_command, shell=True, stdout=subprocess.PIPE)
  result = subprocess.run(script_command, shell=True)
  end_time = time()

  if result.returncode != 0:
    raise RuntimeError(f'{script_command} returned {result.returncode}')

  print(f'Running Pytorch took {end_time - start_time:.2f} s')
  
  # pytorch_results = [float(el) for el in result.stdout.decode('UTF-8').split(' ')]
  # For now, put results inside another list as in the future this might become list of results for different inputs
  # pytorch_results = [pytorch_results]

  update_command = f'python3 {update_path}'
  # subprocess.run(update_command, shell=True)
  subprocess.run(update_command, shell=True, stdout=subprocess.PIPE)
  if result.returncode != 0:
    raise RuntimeError(f'{update_command} returned {result.returncode}')

  # return pytorch_results



def get_hls_results(path):
  
  results = []

  with open(path, 'r') as f:
    for line in f:
      results.append([float(el) for el in line.split(' ') if el != '\n'])

  return results


def get_pytorch_results(path):
  results = []

  with open(path, 'r') as f:
    for line in f:
      results.append([float(el) for el in line.split(' ') if el != '\n'])

  return results


def compare_results(hls_results, pytorch_results, labels, quiet=True):
  total_MSE = 0.
  elements_count = 0
  correct_predictions_pytorch = 0
  correct_predictions_hls = 0
  predictions_count = 0

  assert len(hls_results) == len(pytorch_results), f'{hls_results=}, {pytorch_results=}'

  if not quiet:
    print('Results:')
    print('HLS \t\t\t\t\t\t\t Pytorch')

  for hls_result, pytorch_result, label in zip(hls_results, pytorch_results, labels):
    assert len(hls_result) == len(pytorch_result)
    if not quiet:
      print(hls_result, pytorch_result)

    for hls_val, pytorch_val in zip(hls_result, pytorch_result):
      # print(hls_val, pytorch_val)
      diff = hls_val - pytorch_val
      total_MSE += diff * diff
      elements_count += 1

    label = int(label[0])
    correct_predictions_pytorch += int(np.argmax(pytorch_result) == label)
    correct_predictions_hls += int(np.argmax(hls_result) == label)
    # if int(np.argmax(hls_result)) != int(np.argmax(pytorch_result)) != label:
    #   print(f'hls: {int(np.argmax(hls_result))}, pytorch: {int(np.argmax(pytorch_result))}, label: {label}')
    predictions_count += 1

  return (total_MSE / float(elements_count), correct_predictions_pytorch / predictions_count, correct_predictions_hls / predictions_count)


def clean_file(path):
  open(path, 'w').close() 


def set_build_options(
  path: str,
  options: Dict[str, bool],
  disable_all: bool = False,
) -> None:

  modified_lines = 0
  lines_to_modify = len(options)

  fh, abs_path = mkstemp()

  # Check if lines look like '<name> <0/1>' and change them accordingly to options
  with fdopen(fh,'w') as new_file:
    with open(path) as old_file:
      for line in old_file:
        if modified_lines < lines_to_modify:
          for key, value in options.items():
            if key in line.split(' '):
              value = '0' if disable_all else str(int(value))
              line = re.sub(fr'(.*)({key})( *) (\d)', fr'\1\2\3 {value}', line)
              modified_lines += 1

          new_file.write(line)

        else:
          new_file.write(line)
              
  # Copy the file permissions from the old file to the new file
  copymode(path, abs_path)

  # Remove original file
  remove(path)

  # Move new file
  move(abs_path, path)

def modify_defines(
  path: str,
  options: Dict,
  line_type: str,
) -> None:

  def pretty_print(line):
    line_to_print = line.replace('\n', '')
    print(f'{Fore.GREEN}L{key}:{Style.RESET_ALL} {line_to_print}', end=f' {Fore.RED}|{Style.RESET_ALL} ')

  fh, abs_path = mkstemp()

  # Check if lines look like '<name> <0/1>' and change them accordingly to options
  with fdopen(fh,'w') as new_file:
    with open(path) as old_file:
      
      for index, line in enumerate(old_file):
        for key, value in options.items():
          if index == key - 1:
            if line_type == 'ap_fixed':
              assert isinstance(value, tuple)
              # @ hack as otherwise raw string treats value as part of the capture group, i.e. \1 becomes \125
              line = re.sub(fr'([^\d]*)(\d+)(,)(\d+)(.*)', fr'\1@{value[0]}\3@{value[1]}\5', line).replace('@', '')
              pretty_print(line)

            elif line_type == '#define':
              assert isinstance(value, int)
              line = re.sub(fr'(.*) (\d+)', fr'\1 {value}', line)
              pretty_print(line)

        new_file.write(line)

  print()

  # Copy the file permissions from the old file to the new file
  copymode(path, abs_path)

  # Remove original file
  remove(path)

  # Move new file
  move(abs_path, path)


def parse():
  parser = argparse.ArgumentParser(description='Run Vivado HLS and compare againt Pytorch')

  parser.add_argument('--csim', action='store_true')
  parser.add_argument('--synth', action='store_true')
  parser.add_argument('--cosim', action='store_true')
  parser.add_argument('--reset', action='store_true')

  parser.add_argument('--pytorch', action='store_true')

  parser.add_argument('--load', action='store', type=str, default=None)
  parser.add_argument('--quiet', action='store_true')

  args = parser.parse_args()
  run_hls = args.csim or args.synth or args.cosim or args.reset

  return args, run_hls


def set_hls_output_predictions(path, results):
  # print(f'{results=}')
  results_to_write = ''
  for result in results:
    results_to_write += ' '.join([str(el) for el in result]) + '\n'
  # print(f'{results_to_write=}')
  with open(path, 'w') as f:
    f.write(results_to_write)


def custom_plot(accuracies, widths, use_total_widths: bool, path):
  fig = plt.figure()

  total_widths = [list(width.values())[0][0] for width in widths[:len(accuracies)]]
  int_widths = [list(width.values())[0][1] for width in widths[:len(accuracies)]]

  main_widths = total_widths if use_total_widths else int_widths

  plt.scatter(main_widths, [accuracy*100 for accuracy in accuracies], marker='D', label='Test accuracy')
  plt.xticks(ticks=main_widths, labels=[f'<{total_width},{int_width}>' for total_width, int_width in zip(total_widths, int_widths)], rotation=90)
  plt.axhline(y=20, color='r', linestyle='--', label='Baseline accuracy')
  plt.title('Accuracy against fixed-point precision')
  plt.xlabel('ap_fixed')
  plt.ylabel('Accuracy (%)')
  plt.gca().set_ylim([15, 85])
  fig.tight_layout()
  plt.legend()
  plt.grid()

  plt.savefig(path, format='png', dpi=200)
  print(f'Plotted results saved to {path}')


def main(args, run_hls: bool = True):

  # Paths
  hls_dir_path = 'hls/'

  defines_path = hls_dir_path + 'firmware/defines.h'
  labels_path = hls_dir_path + 'tb_data/tb_labels.dat'
  hls_output_predictions_path = hls_dir_path + 'tb_data/tb_output_predictions.dat'
  csim_results_log_path = hls_dir_path + 'tb_data/csim_results.log'
  rtl_cosim_results_log_path = hls_dir_path + 'tb_data/rtl_cosim_results.log'
  hls_layers_log_path = hls_dir_path + 'tb_data/csim_layers.log'

  build_tcl_path = 'build_prj.tcl'
  build_tcl_path_full = hls_dir_path + build_tcl_path
  pytorch_script_path = 'pytorch/train_evaluate.py'
  update_weights_script_path = 'scripts/extract_weights_biases.py'
  pytorch_results_log_path = 'logs/pytorch_results.log'

  if args.pytorch:
    run_pytorch(script_path=pytorch_script_path, update_path=update_weights_script_path)
    pytorch_results = get_pytorch_results(path=hls_output_predictions_path)
  else:
    pytorch_results = get_pytorch_results(path=hls_output_predictions_path)

  # Options and results
  type_options2 = [
    {
      47: (34, 18), 49: (34, 18), 50: (34, 18), 51: (34, 18), 52: (34, 18), 54: (34, 18), 56: (34, 18), 57: (34, 18), 58: (34, 18), 60: (34, 18),
      62: (34, 18), 63: (34, 18), 64: (34, 18), 66: (34, 18), 67: (34, 18), 68: (34, 18), 69: (34, 18), 71: (34, 18), 72: (34, 18), 73: (34, 18), 78: (34, 18),

      82: (34, 18), 83: (34, 18), 84: (34, 18), 90: (34, 18), 91: (34, 18), 92: (34, 18), 94: (34, 18), 95: (34, 18), 96: (34, 18), 98: (34, 18), 99: (34, 18),
      100: (34, 18), 102: (34, 18), 104: (34, 18), 105: (34, 18), 106: (34, 18), 108: (34, 18), 109: (34, 18), 110: (34, 18), 115: (34, 18), 117: (34, 18),
      119: (34, 18), 120: (34, 18), 121: (34, 18), 123: (34, 18),

      127: (34, 18), 129: (34, 18), 130: (34, 18), 131: (34, 18), 133: (34, 18), 135: (34, 18), 136: (34, 18), 137: (34, 18), 139: (34, 18), 140: (34, 18), 141: (34, 18),
      143: (34, 18), 145: (34, 18), 146: (34, 18), 147: (34, 18),
    },
    {
      47: (33, 18), 49: (33, 18), 50: (33, 18), 51: (33, 18), 52: (33, 18), 54: (33, 18), 56: (33, 18), 57: (33, 18), 58: (33, 18), 60: (33, 18),
      62: (33, 18), 63: (33, 18), 64: (33, 18), 66: (33, 18), 67: (33, 18), 68: (33, 18), 69: (33, 18), 71: (33, 18), 72: (33, 18), 73: (33, 18), 78: (33, 18),

      82: (33, 18), 83: (33, 18), 84: (33, 18), 90: (33, 18), 91: (33, 18), 92: (33, 18), 94: (33, 18), 95: (33, 18), 96: (33, 18), 98: (33, 18), 99: (33, 18),
      100: (33, 18), 102: (33, 18), 104: (33, 18), 105: (33, 18), 106: (33, 18), 108: (33, 18), 109: (33, 18), 110: (33, 18), 115: (33, 18), 117: (33, 18),
      119: (33, 18), 120: (33, 18), 121: (33, 18), 123: (33, 18),

      127: (33, 18), 129: (33, 18), 130: (33, 18), 131: (33, 18), 133: (33, 18), 135: (33, 18), 136: (33, 18), 137: (33, 18), 139: (33, 18), 140: (33, 18), 141: (33, 18),
      143: (33, 18), 145: (33, 18), 146: (33, 18), 147: (33, 18),
    },
    {
      47: (32, 18), 49: (32, 18), 50: (32, 18), 51: (32, 18), 52: (32, 18), 54: (32, 18), 56: (32, 18), 57: (32, 18), 58: (32, 18), 60: (32, 18),
      62: (32, 18), 63: (32, 18), 64: (32, 18), 66: (32, 18), 67: (32, 18), 68: (32, 18), 69: (32, 18), 71: (32, 18), 72: (32, 18), 73: (32, 18), 78: (32, 18),

      82: (32, 18), 83: (32, 18), 84: (32, 18), 90: (32, 18), 91: (32, 18), 92: (32, 18), 94: (32, 18), 95: (32, 18), 96: (32, 18), 98: (32, 18), 99: (32, 18),
      100: (32, 18), 102: (32, 18), 104: (32, 18), 105: (32, 18), 106: (32, 18), 108: (32, 18), 109: (32, 18), 110: (32, 18), 115: (32, 18), 117: (32, 18),
      119: (32, 18), 120: (32, 18), 121: (32, 18), 123: (32, 18),

      127: (32, 18), 129: (32, 18), 130: (32, 18), 131: (32, 18), 132: (32, 18), 135: (32, 18), 136: (32, 18), 137: (32, 18), 139: (32, 18), 140: (32, 18), 141: (32, 18),
      143: (32, 18), 145: (32, 18), 146: (32, 18), 147: (32, 18),
    },
    {
      47: (31, 18), 49: (31, 18), 50: (31, 18), 51: (31, 18), 52: (31, 18), 54: (31, 18), 56: (31, 18), 57: (31, 18), 58: (31, 18), 60: (31, 18),
      62: (31, 18), 63: (31, 18), 64: (31, 18), 66: (31, 18), 67: (31, 18), 68: (31, 18), 69: (31, 18), 71: (31, 18), 72: (31, 18), 73: (31, 18), 78: (31, 18),

      82: (31, 18), 83: (31, 18), 84: (31, 18), 90: (31, 18), 91: (31, 18), 92: (31, 18), 94: (31, 18), 95: (31, 18), 96: (31, 18), 98: (31, 18), 99: (31, 18),
      100: (31, 18), 102: (31, 18), 104: (31, 18), 105: (31, 18), 106: (31, 18), 108: (31, 18), 109: (31, 18), 110: (31, 18), 115: (31, 18), 117: (31, 18),
      119: (31, 18), 120: (31, 18), 121: (31, 18), 123: (31, 18),

      127: (31, 18), 129: (31, 18), 130: (31, 18), 131: (31, 18), 131: (31, 18), 135: (31, 18), 136: (31, 18), 137: (31, 18), 139: (31, 18), 140: (31, 18), 141: (31, 18),
      143: (31, 18), 145: (31, 18), 146: (31, 18), 147: (31, 18),
    },
    {
      47: (30, 18), 49: (30, 18), 50: (30, 18), 51: (30, 18), 52: (30, 18), 54: (30, 18), 56: (30, 18), 57: (30, 18), 58: (30, 18), 60: (30, 18),
      62: (30, 18), 63: (30, 18), 64: (30, 18), 66: (30, 18), 67: (30, 18), 68: (30, 18), 69: (30, 18), 71: (30, 18), 72: (30, 18), 73: (30, 18), 78: (30, 18),

      82: (30, 18), 83: (30, 18), 84: (30, 18), 90: (30, 18), 91: (30, 18), 92: (30, 18), 94: (30, 18), 95: (30, 18), 96: (30, 18), 98: (30, 18), 99: (30, 18),
      100: (30, 18), 102: (30, 18), 104: (30, 18), 105: (30, 18), 106: (30, 18), 108: (30, 18), 109: (30, 18), 110: (30, 18), 115: (30, 18), 117: (30, 18),
      119: (30, 18), 120: (30, 18), 121: (30, 18), 123: (30, 18),

      127: (30, 18), 129: (30, 18), 130: (30, 18), 131: (30, 18), 130: (30, 18), 135: (30, 18), 136: (30, 18), 137: (30, 18), 139: (30, 18), 140: (30, 18), 141: (30, 18),
      143: (30, 18), 145: (30, 18), 146: (30, 18), 147: (30, 18),
    },
    {
      47: (29, 18), 49: (29, 18), 50: (29, 18), 51: (29, 18), 52: (29, 18), 54: (29, 18), 56: (29, 18), 57: (29, 18), 58: (29, 18), 60: (29, 18),
      62: (29, 18), 63: (29, 18), 64: (29, 18), 66: (29, 18), 67: (29, 18), 68: (29, 18), 69: (29, 18), 71: (29, 18), 72: (29, 18), 73: (29, 18), 78: (29, 18),

      82: (29, 18), 83: (29, 18), 84: (29, 18), 90: (29, 18), 91: (29, 18), 92: (29, 18), 94: (29, 18), 95: (29, 18), 96: (29, 18), 98: (29, 18), 99: (29, 18),
      100: (29, 18), 102: (29, 18), 104: (29, 18), 105: (29, 18), 106: (29, 18), 108: (29, 18), 109: (29, 18), 110: (29, 18), 115: (29, 18), 117: (29, 18),
      119: (29, 18), 120: (29, 18), 121: (29, 18), 123: (29, 18),

      127: (29, 18), 129: (29, 18), 130: (29, 18), 131: (29, 18), 129: (29, 18), 135: (29, 18), 136: (29, 18), 137: (29, 18), 139: (29, 18), 140: (29, 18), 141: (29, 18),
      143: (29, 18), 145: (29, 18), 146: (29, 18), 147: (29, 18),
    },
    {
      47: (28, 18), 49: (28, 18), 50: (28, 18), 51: (28, 18), 52: (28, 18), 54: (28, 18), 56: (28, 18), 57: (28, 18), 58: (28, 18), 60: (28, 18),
      62: (28, 18), 63: (28, 18), 64: (28, 18), 66: (28, 18), 67: (28, 18), 68: (28, 18), 69: (28, 18), 71: (28, 18), 72: (28, 18), 73: (28, 18), 78: (28, 18),

      82: (28, 18), 83: (28, 18), 84: (28, 18), 90: (28, 18), 91: (28, 18), 92: (28, 18), 94: (28, 18), 95: (28, 18), 96: (28, 18), 98: (28, 18), 99: (28, 18),
      100: (28, 18), 102: (28, 18), 104: (28, 18), 105: (28, 18), 106: (28, 18), 108: (28, 18), 109: (28, 18), 110: (28, 18), 115: (28, 18), 117: (28, 18),
      119: (28, 18), 120: (28, 18), 121: (28, 18), 123: (28, 18),

      127: (28, 18), 129: (28, 18), 130: (28, 18), 131: (28, 18), 128: (28, 18), 135: (28, 18), 136: (28, 18), 137: (28, 18), 139: (28, 18), 140: (28, 18), 141: (28, 18),
      143: (28, 18), 145: (28, 18), 146: (28, 18), 147: (28, 18),
    },
    {
      47: (27, 18), 49: (27, 18), 50: (27, 18), 51: (27, 18), 52: (27, 18), 54: (27, 18), 56: (27, 18), 57: (27, 18), 58: (27, 18), 60: (27, 18),
      62: (27, 18), 63: (27, 18), 64: (27, 18), 66: (27, 18), 67: (27, 18), 68: (27, 18), 69: (27, 18), 71: (27, 18), 72: (27, 18), 73: (27, 18), 78: (27, 18),

      82: (27, 18), 83: (27, 18), 84: (27, 18), 90: (27, 18), 91: (27, 18), 92: (27, 18), 94: (27, 18), 95: (27, 18), 96: (27, 18), 98: (27, 18), 99: (27, 18),
      100: (27, 18), 102: (27, 18), 104: (27, 18), 105: (27, 18), 106: (27, 18), 108: (27, 18), 109: (27, 18), 110: (27, 18), 115: (27, 18), 117: (27, 18),
      119: (27, 18), 120: (27, 18), 121: (27, 18), 123: (27, 18),

      127: (27, 18), 129: (27, 18), 130: (27, 18), 131: (27, 18), 127: (27, 18), 135: (27, 18), 136: (27, 18), 137: (27, 18), 139: (27, 18), 140: (27, 18), 141: (27, 18),
      143: (27, 18), 145: (27, 18), 146: (27, 18), 147: (27, 18),
    },
    {
      47: (26, 18), 49: (26, 18), 50: (26, 18), 51: (26, 18), 52: (26, 18), 54: (26, 18), 56: (26, 18), 57: (26, 18), 58: (26, 18), 60: (26, 18),
      62: (26, 18), 63: (26, 18), 64: (26, 18), 66: (26, 18), 67: (26, 18), 68: (26, 18), 69: (26, 18), 71: (26, 18), 72: (26, 18), 73: (26, 18), 78: (26, 18),

      82: (26, 18), 83: (26, 18), 84: (26, 18), 90: (26, 18), 91: (26, 18), 92: (26, 18), 94: (26, 18), 95: (26, 18), 96: (26, 18), 98: (26, 18), 99: (26, 18),
      100: (26, 18), 102: (26, 18), 104: (26, 18), 105: (26, 18), 106: (26, 18), 108: (26, 18), 109: (26, 18), 110: (26, 18), 115: (26, 18), 117: (26, 18),
      119: (26, 18), 120: (26, 18), 121: (26, 18), 123: (26, 18),

      127: (26, 18), 129: (26, 18), 130: (26, 18), 131: (26, 18), 126: (26, 18), 135: (26, 18), 136: (26, 18), 137: (26, 18), 139: (26, 18), 140: (26, 18), 141: (26, 18),
      143: (26, 18), 145: (26, 18), 146: (26, 18), 147: (26, 18),
    },
    {
      47: (25, 18), 49: (25, 18), 50: (25, 18), 51: (25, 18), 52: (25, 18), 54: (25, 18), 56: (25, 18), 57: (25, 18), 58: (25, 18), 60: (25, 18),
      62: (25, 18), 63: (25, 18), 64: (25, 18), 66: (25, 18), 67: (25, 18), 68: (25, 18), 69: (25, 18), 71: (25, 18), 72: (25, 18), 73: (25, 18), 78: (25, 18),

      82: (25, 18), 83: (25, 18), 84: (25, 18), 90: (25, 18), 91: (25, 18), 92: (25, 18), 94: (25, 18), 95: (25, 18), 96: (25, 18), 98: (25, 18), 99: (25, 18),
      100: (25, 18), 102: (25, 18), 104: (25, 18), 105: (25, 18), 106: (25, 18), 108: (25, 18), 109: (25, 18), 110: (25, 18), 115: (25, 18), 117: (25, 18),
      119: (25, 18), 120: (25, 18), 121: (25, 18), 123: (25, 18),

      127: (25, 18), 129: (25, 18), 130: (25, 18), 131: (25, 18), 125: (25, 18), 135: (25, 18), 136: (25, 18), 137: (25, 18), 139: (25, 18), 140: (25, 18), 141: (25, 18),
      143: (25, 18), 145: (25, 18), 146: (25, 18), 147: (25, 18),
    },
    {
      47: (24, 18), 49: (24, 18), 50: (24, 18), 51: (24, 18), 52: (24, 18), 54: (24, 18), 56: (24, 18), 57: (24, 18), 58: (24, 18), 60: (24, 18),
      62: (24, 18), 63: (24, 18), 64: (24, 18), 66: (24, 18), 67: (24, 18), 68: (24, 18), 69: (24, 18), 71: (24, 18), 72: (24, 18), 73: (24, 18), 78: (24, 18),

      82: (24, 18), 83: (24, 18), 84: (24, 18), 90: (24, 18), 91: (24, 18), 92: (24, 18), 94: (24, 18), 95: (24, 18), 96: (24, 18), 98: (24, 18), 99: (24, 18),
      100: (24, 18), 102: (24, 18), 104: (24, 18), 105: (24, 18), 106: (24, 18), 108: (24, 18), 109: (24, 18), 110: (24, 18), 115: (24, 18), 117: (24, 18),
      119: (24, 18), 120: (24, 18), 121: (24, 18), 123: (24, 18),

      127: (24, 18), 129: (24, 18), 130: (24, 18), 131: (24, 18), 124: (24, 18), 135: (24, 18), 136: (24, 18), 137: (24, 18), 139: (24, 18), 140: (24, 18), 141: (24, 18),
      143: (24, 18), 145: (24, 18), 146: (24, 18), 147: (24, 18),
    },
    {
      47: (23, 18), 49: (23, 18), 50: (23, 18), 51: (23, 18), 52: (23, 18), 54: (23, 18), 56: (23, 18), 57: (23, 18), 58: (23, 18), 60: (23, 18),
      62: (23, 18), 63: (23, 18), 64: (23, 18), 66: (23, 18), 67: (23, 18), 68: (23, 18), 69: (23, 18), 71: (23, 18), 72: (23, 18), 73: (23, 18), 78: (23, 18),

      82: (23, 18), 83: (23, 18), 84: (23, 18), 90: (23, 18), 91: (23, 18), 92: (23, 18), 94: (23, 18), 95: (23, 18), 96: (23, 18), 98: (23, 18), 99: (23, 18),
      100: (23, 18), 102: (23, 18), 104: (23, 18), 105: (23, 18), 106: (23, 18), 108: (23, 18), 109: (23, 18), 110: (23, 18), 115: (23, 18), 117: (23, 18),
      119: (23, 18), 120: (23, 18), 121: (23, 18), 123: (23, 18),

      127: (23, 18), 129: (23, 18), 130: (23, 18), 131: (23, 18), 123: (23, 18), 135: (23, 18), 136: (23, 18), 137: (23, 18), 139: (23, 18), 140: (23, 18), 141: (23, 18),
      143: (23, 18), 145: (23, 18), 146: (23, 18), 147: (23, 18),
    },
    {
      47: (22, 18), 49: (22, 18), 50: (22, 18), 51: (22, 18), 52: (22, 18), 54: (22, 18), 56: (22, 18), 57: (22, 18), 58: (22, 18), 60: (22, 18),
      62: (22, 18), 63: (22, 18), 64: (22, 18), 66: (22, 18), 67: (22, 18), 68: (22, 18), 69: (22, 18), 71: (22, 18), 72: (22, 18), 73: (22, 18), 78: (22, 18),

      82: (22, 18), 83: (22, 18), 84: (22, 18), 90: (22, 18), 91: (22, 18), 92: (22, 18), 94: (22, 18), 95: (22, 18), 96: (22, 18), 98: (22, 18), 99: (22, 18),
      100: (22, 18), 102: (22, 18), 104: (22, 18), 105: (22, 18), 106: (22, 18), 108: (22, 18), 109: (22, 18), 110: (22, 18), 115: (22, 18), 117: (22, 18),
      119: (22, 18), 120: (22, 18), 121: (22, 18), 123: (22, 18),

      127: (22, 18), 129: (22, 18), 130: (22, 18), 131: (22, 18), 122: (22, 18), 135: (22, 18), 136: (22, 18), 137: (22, 18), 139: (22, 18), 140: (22, 18), 141: (22, 18),
      143: (22, 18), 145: (22, 18), 146: (22, 18), 147: (22, 18),
    },
    {
      47: (21, 18), 49: (21, 18), 50: (21, 18), 51: (21, 18), 52: (21, 18), 54: (21, 18), 56: (21, 18), 57: (21, 18), 58: (21, 18), 60: (21, 18),
      62: (21, 18), 63: (21, 18), 64: (21, 18), 66: (21, 18), 67: (21, 18), 68: (21, 18), 69: (21, 18), 71: (21, 18), 72: (21, 18), 73: (21, 18), 78: (21, 18),

      82: (21, 18), 83: (21, 18), 84: (21, 18), 90: (21, 18), 91: (21, 18), 92: (21, 18), 94: (21, 18), 95: (21, 18), 96: (21, 18), 98: (21, 18), 99: (21, 18),
      100: (21, 18), 102: (21, 18), 104: (21, 18), 105: (21, 18), 106: (21, 18), 108: (21, 18), 109: (21, 18), 110: (21, 18), 115: (21, 18), 117: (21, 18),
      119: (21, 18), 120: (21, 18), 121: (21, 18), 123: (21, 18),

      127: (21, 18), 129: (21, 18), 130: (21, 18), 131: (21, 18), 121: (21, 18), 135: (21, 18), 136: (21, 18), 137: (21, 18), 139: (21, 18), 140: (21, 18), 141: (21, 18),
      143: (21, 18), 145: (21, 18), 146: (21, 18), 147: (21, 18),
    },
    {
      47: (20, 18), 49: (20, 18), 50: (20, 18), 51: (20, 18), 52: (20, 18), 54: (20, 18), 56: (20, 18), 57: (20, 18), 58: (20, 18), 60: (20, 18),
      62: (20, 18), 63: (20, 18), 64: (20, 18), 66: (20, 18), 67: (20, 18), 68: (20, 18), 69: (20, 18), 71: (20, 18), 72: (20, 18), 73: (20, 18), 78: (20, 18),

      82: (20, 18), 83: (20, 18), 84: (20, 18), 90: (20, 18), 91: (20, 18), 92: (20, 18), 94: (20, 18), 95: (20, 18), 96: (20, 18), 98: (20, 18), 99: (20, 18),
      100: (20, 18), 102: (20, 18), 104: (20, 18), 105: (20, 18), 106: (20, 18), 108: (20, 18), 109: (20, 18), 110: (20, 18), 115: (20, 18), 117: (20, 18),
      119: (20, 18), 120: (20, 18), 121: (20, 18), 123: (20, 18),

      127: (20, 18), 129: (20, 18), 130: (20, 18), 131: (20, 18), 120: (20, 18), 135: (20, 18), 136: (20, 18), 137: (20, 18), 139: (20, 18), 140: (20, 18), 141: (20, 18),
      143: (20, 18), 145: (20, 18), 146: (20, 18), 147: (20, 18),
    },
    {
      47: (19, 18), 49: (19, 18), 50: (19, 18), 51: (19, 18), 52: (19, 18), 54: (19, 18), 56: (19, 18), 57: (19, 18), 58: (19, 18), 60: (19, 18),
      62: (19, 18), 63: (19, 18), 64: (19, 18), 66: (19, 18), 67: (19, 18), 68: (19, 18), 69: (19, 18), 71: (19, 18), 72: (19, 18), 73: (19, 18), 78: (19, 18),

      82: (19, 18), 83: (19, 18), 84: (19, 18), 90: (19, 18), 91: (19, 18), 92: (19, 18), 94: (19, 18), 95: (19, 18), 96: (19, 18), 98: (19, 18), 99: (19, 18),
      100: (19, 18), 102: (19, 18), 104: (19, 18), 105: (19, 18), 106: (19, 18), 108: (19, 18), 109: (19, 18), 110: (19, 18), 115: (19, 18), 117: (19, 18),
      119: (19, 18), 120: (19, 18), 121: (19, 18), 123: (19, 18),

      127: (19, 18), 129: (19, 18), 130: (19, 18), 131: (19, 18), 119: (19, 18), 135: (19, 18), 136: (19, 18), 137: (19, 18), 139: (19, 18), 140: (19, 18), 141: (19, 18),
      143: (19, 18), 145: (19, 18), 146: (19, 18), 147: (19, 18),
    },
  ]
  type_options = [
    {
      47: (29, 19), 49: (29, 19), 50: (29, 19), 51: (29, 19), 52: (29, 19), 54: (29, 19), 56: (29, 19), 57: (29, 19), 58: (29, 19), 60: (29, 19),
      62: (29, 19), 63: (29, 19), 64: (29, 19), 66: (29, 19), 67: (29, 19), 68: (29, 19), 69: (29, 19), 71: (29, 19), 72: (29, 19), 73: (29, 19), 78: (29, 19),

      82: (29, 19), 83: (29, 19), 84: (29, 19), 90: (29, 19), 91: (29, 19), 92: (29, 19), 94: (29, 19), 95: (29, 19), 96: (29, 19), 98: (29, 19), 99: (29, 19),
      100: (29, 19), 102: (29, 19), 104: (29, 19), 105: (29, 19), 106: (29, 19), 108: (29, 19), 109: (29, 19), 110: (29, 19), 115: (29, 19), 117: (29, 19),
      119: (29, 19), 120: (29, 19), 121: (29, 19), 123: (29, 19),

      127: (29, 19), 129: (29, 19), 130: (29, 19), 131: (29, 19), 133: (29, 19), 135: (29, 19), 136: (29, 19), 137: (29, 19), 139: (29, 19), 140: (29, 19), 141: (29, 19),
      143: (29, 19), 145: (29, 19), 146: (29, 19), 147: (29, 18),
    },
    {
      47: (28, 18), 49: (28, 18), 50: (28, 18), 51: (28, 18), 52: (28, 18), 54: (28, 18), 56: (28, 18), 57: (28, 18), 58: (28, 18), 60: (28, 18),
      62: (28, 18), 63: (28, 18), 64: (28, 18), 66: (28, 18), 67: (28, 18), 68: (28, 18), 69: (28, 18), 71: (28, 18), 72: (28, 18), 73: (28, 18), 78: (28, 18),

      82: (28, 18), 83: (28, 18), 84: (28, 18), 90: (28, 18), 91: (28, 18), 92: (28, 18), 94: (28, 18), 95: (28, 18), 96: (28, 18), 98: (28, 18), 99: (28, 18),
      100: (28, 18), 102: (28, 18), 104: (28, 18), 105: (28, 18), 106: (28, 18), 108: (28, 18), 109: (28, 18), 110: (28, 18), 115: (28, 18), 117: (28, 18),
      119: (28, 18), 120: (28, 18), 121: (28, 18), 123: (28, 18),

      127: (28, 18), 129: (28, 18), 130: (28, 18), 131: (28, 18), 133: (28, 18), 135: (28, 18), 136: (28, 18), 137: (28, 18), 139: (28, 18), 140: (28, 18), 141: (28, 18),
      143: (28, 18), 145: (28, 18), 146: (28, 18), 147: (28, 18),
    },
    {
      47: (27, 17), 49: (27, 17), 50: (27, 17), 51: (27, 17), 52: (27, 17), 54: (27, 17), 56: (27, 17), 57: (27, 17), 58: (27, 17), 60: (27, 17),
      62: (27, 17), 63: (27, 17), 64: (27, 17), 66: (27, 17), 67: (27, 17), 68: (27, 17), 69: (27, 17), 71: (27, 17), 72: (27, 17), 73: (27, 17), 78: (27, 17),

      82: (27, 17), 83: (27, 17), 84: (27, 17), 90: (27, 17), 91: (27, 17), 92: (27, 17), 94: (27, 17), 95: (27, 17), 96: (27, 17), 98: (27, 17), 99: (27, 17),
      100: (27, 17), 102: (27, 17), 104: (27, 17), 105: (27, 17), 106: (27, 17), 108: (27, 17), 109: (27, 17), 110: (27, 17), 115: (27, 17), 117: (27, 17),
      119: (27, 17), 120: (27, 17), 121: (27, 17), 123: (27, 17),

      127: (27, 17), 129: (27, 17), 130: (27, 17), 131: (27, 17), 133: (27, 17), 135: (27, 17), 136: (27, 17), 137: (27, 17), 139: (27, 17), 140: (27, 17), 141: (27, 17),
      143: (27, 17), 145: (27, 17), 146: (27, 17), 147: (27, 17),
    },
    {
      47: (26, 16), 49: (26, 16), 50: (26, 16), 51: (26, 16), 52: (26, 16), 54: (26, 16), 56: (26, 16), 57: (26, 16), 58: (26, 16), 60: (26, 16),
      62: (26, 16), 63: (26, 16), 64: (26, 16), 66: (26, 16), 67: (26, 16), 68: (26, 16), 69: (26, 16), 71: (26, 16), 72: (26, 16), 73: (26, 16), 78: (26, 16),

      82: (26, 16), 83: (26, 16), 84: (26, 16), 90: (26, 16), 91: (26, 16), 92: (26, 16), 94: (26, 16), 95: (26, 16), 96: (26, 16), 98: (26, 16), 99: (26, 16),
      100: (26, 16), 102: (26, 16), 104: (26, 16), 105: (26, 16), 106: (26, 16), 108: (26, 16), 109: (26, 16), 110: (26, 16), 115: (26, 16), 117: (26, 16),
      119: (26, 16), 120: (26, 16), 121: (26, 16), 123: (26, 16),

      127: (26, 16), 129: (26, 16), 130: (26, 16), 131: (26, 16), 133: (26, 16), 135: (26, 16), 136: (26, 16), 137: (26, 16), 139: (26, 16), 140: (26, 16), 141: (26, 16),
      143: (26, 16), 145: (26, 16), 146: (26, 16), 147: (26, 16),
    },
    {
      47: (25, 15), 49: (25, 15), 50: (25, 15), 51: (25, 15), 52: (25, 15), 54: (25, 15), 56: (25, 15), 57: (25, 15), 58: (25, 15), 60: (25, 15),
      62: (25, 15), 63: (25, 15), 64: (25, 15), 66: (25, 15), 67: (25, 15), 68: (25, 15), 69: (25, 15), 71: (25, 15), 72: (25, 15), 73: (25, 15), 78: (25, 15),

      82: (25, 15), 83: (25, 15), 84: (25, 15), 90: (25, 15), 91: (25, 15), 92: (25, 15), 94: (25, 15), 95: (25, 15), 96: (25, 15), 98: (25, 15), 99: (25, 15),
      100: (25, 15), 102: (25, 15), 104: (25, 15), 105: (25, 15), 106: (25, 15), 108: (25, 15), 109: (25, 15), 110: (25, 15), 115: (25, 15), 117: (25, 15),
      119: (25, 15), 120: (25, 15), 121: (25, 15), 123: (25, 15),

      127: (25, 15), 129: (25, 15), 130: (25, 15), 131: (25, 15), 133: (25, 15), 135: (25, 15), 136: (25, 15), 137: (25, 15), 139: (25, 15), 140: (25, 15), 141: (25, 15),
      143: (25, 15), 145: (25, 15), 146: (25, 15), 147: (25, 15),
    },
    {
      47: (24, 14), 49: (24, 14), 50: (24, 14), 51: (24, 14), 52: (24, 14), 54: (24, 14), 56: (24, 14), 57: (24, 14), 58: (24, 14), 60: (24, 14),
      62: (24, 14), 63: (24, 14), 64: (24, 14), 66: (24, 14), 67: (24, 14), 68: (24, 14), 69: (24, 14), 71: (24, 14), 72: (24, 14), 73: (24, 14), 78: (24, 14),

      82: (24, 14), 83: (24, 14), 84: (24, 14), 90: (24, 14), 91: (24, 14), 92: (24, 14), 94: (24, 14), 95: (24, 14), 96: (24, 14), 98: (24, 14), 99: (24, 14),
      100: (24, 14), 102: (24, 14), 104: (24, 14), 105: (24, 14), 106: (24, 14), 108: (24, 14), 109: (24, 14), 110: (24, 14), 115: (24, 14), 117: (24, 14),
      119: (24, 14), 120: (24, 14), 121: (24, 14), 123: (24, 14),

      127: (24, 14), 129: (24, 14), 130: (24, 14), 131: (24, 14), 133: (24, 14), 135: (24, 14), 136: (24, 14), 137: (24, 14), 139: (24, 14), 140: (24, 14), 141: (24, 14),
      143: (24, 14), 145: (24, 14), 146: (24, 14), 147: (24, 14),
    },
    {
      47: (23, 13), 49: (23, 13), 50: (23, 13), 51: (23, 13), 52: (23, 13), 54: (23, 13), 56: (23, 13), 57: (23, 13), 58: (23, 13), 60: (23, 13),
      62: (23, 13), 63: (23, 13), 64: (23, 13), 66: (23, 13), 67: (23, 13), 68: (23, 13), 69: (23, 13), 71: (23, 13), 72: (23, 13), 73: (23, 13), 78: (23, 13),

      82: (23, 13), 83: (23, 13), 84: (23, 13), 90: (23, 13), 91: (23, 13), 92: (23, 13), 94: (23, 13), 95: (23, 13), 96: (23, 13), 98: (23, 13), 99: (23, 13),
      100: (23, 13), 102: (23, 13), 104: (23, 13), 105: (23, 13), 106: (23, 13), 108: (23, 13), 109: (23, 13), 110: (23, 13), 115: (23, 13), 117: (23, 13),
      119: (23, 13), 120: (23, 13), 121: (23, 13), 123: (23, 13),

      127: (23, 13), 129: (23, 13), 130: (23, 13), 131: (23, 13), 133: (23, 13), 135: (23, 13), 136: (23, 13), 137: (23, 13), 139: (23, 13), 140: (23, 13), 141: (23, 13),
      143: (23, 13), 145: (23, 13), 146: (23, 13), 147: (23, 13),
    },
    {
      47: (22, 12), 49: (22, 12), 50: (22, 12), 51: (22, 12), 52: (22, 12), 54: (22, 12), 56: (22, 12), 57: (22, 12), 58: (22, 12), 60: (22, 12),
      62: (22, 12), 63: (22, 12), 64: (22, 12), 66: (22, 12), 67: (22, 12), 68: (22, 12), 69: (22, 12), 71: (22, 12), 72: (22, 12), 73: (22, 12), 78: (22, 12),

      82: (22, 12), 83: (22, 12), 84: (22, 12), 90: (22, 12), 91: (22, 12), 92: (22, 12), 94: (22, 12), 95: (22, 12), 96: (22, 12), 98: (22, 12), 99: (22, 12),
      100: (22, 12), 102: (22, 12), 104: (22, 12), 105: (22, 12), 106: (22, 12), 108: (22, 12), 109: (22, 12), 110: (22, 12), 115: (22, 12), 117: (22, 12),
      119: (22, 12), 120: (22, 12), 121: (22, 12), 123: (22, 12),

      127: (22, 12), 129: (22, 12), 130: (22, 12), 131: (22, 12), 133: (22, 12), 135: (22, 12), 136: (22, 12), 137: (22, 12), 139: (22, 12), 140: (22, 12), 141: (22, 12),
      143: (22, 12), 145: (22, 12), 146: (22, 12), 147: (22, 12),
    },
    {
      47: (21, 11), 49: (21, 11), 50: (21, 11), 51: (21, 11), 52: (21, 11), 54: (21, 11), 56: (21, 11), 57: (21, 11), 58: (21, 11), 60: (21, 11),
      62: (21, 11), 63: (21, 11), 64: (21, 11), 66: (21, 11), 67: (21, 11), 68: (21, 11), 69: (21, 11), 71: (21, 11), 72: (21, 11), 73: (21, 11), 78: (21, 11),

      82: (21, 11), 83: (21, 11), 84: (21, 11), 90: (21, 11), 91: (21, 11), 92: (21, 11), 94: (21, 11), 95: (21, 11), 96: (21, 11), 98: (21, 11), 99: (21, 11),
      100: (21, 11), 102: (21, 11), 104: (21, 11), 105: (21, 11), 106: (21, 11), 108: (21, 11), 109: (21, 11), 110: (21, 11), 115: (21, 11), 117: (21, 11),
      119: (21, 11), 120: (21, 11), 121: (21, 11), 123: (21, 11),

      127: (21, 11), 129: (21, 11), 130: (21, 11), 131: (21, 11), 133: (21, 11), 135: (21, 11), 136: (21, 11), 137: (21, 11), 139: (21, 11), 140: (21, 11), 141: (21, 11),
      143: (21, 11), 145: (21, 11), 146: (21, 11), 147: (21, 11),
    },
    {
      47: (20, 10), 49: (20, 10), 50: (20, 10), 51: (20, 10), 52: (20, 10), 54: (20, 10), 56: (20, 10), 57: (20, 10), 58: (20, 10), 60: (20, 10),
      62: (20, 10), 63: (20, 10), 64: (20, 10), 66: (20, 10), 67: (20, 10), 68: (20, 10), 69: (20, 10), 71: (20, 10), 72: (20, 10), 73: (20, 10), 78: (20, 10),

      82: (20, 10), 83: (20, 10), 84: (20, 10), 90: (20, 10), 91: (20, 10), 92: (20, 10), 94: (20, 10), 95: (20, 10), 96: (20, 10), 98: (20, 10), 99: (20, 10),
      100: (20, 10), 102: (20, 10), 104: (20, 10), 105: (20, 10), 106: (20, 10), 108: (20, 10), 109: (20, 10), 110: (20, 10), 115: (20, 10), 117: (20, 10),
      119: (20, 10), 120: (20, 10), 121: (20, 10), 123: (20, 10),

      127: (20, 10), 129: (20, 10), 130: (20, 10), 131: (20, 10), 133: (20, 10), 135: (20, 10), 136: (20, 10), 137: (20, 10), 139: (20, 10), 140: (20, 10), 141: (20, 10),
      143: (20, 10), 145: (20, 10), 146: (20, 10), 147: (20, 10),
    },
    {
      47: (19, 9), 49: (19, 9), 50: (19, 9), 51: (19, 9), 52: (19, 9), 54: (19, 9), 56: (19, 9), 57: (19, 9), 58: (19, 9), 60: (19, 9),
      62: (19, 9), 63: (19, 9), 64: (19, 9), 66: (19, 9), 67: (19, 9), 68: (19, 9), 69: (19, 9), 71: (19, 9), 72: (19, 9), 73: (19, 9), 78: (19, 9),

      82: (19, 9), 83: (19, 9), 84: (19, 9), 90: (19, 9), 91: (19, 9), 92: (19, 9), 94: (19, 9), 95: (19, 9), 96: (19, 9), 98: (19, 9), 99: (19, 9),
      100: (19, 9), 102: (19, 9), 104: (19, 9), 105: (19, 9), 106: (19, 9), 108: (19, 9), 109: (19, 9), 110: (19, 9), 115: (19, 9), 117: (19, 9),
      119: (19, 9), 120: (19, 9), 121: (19, 9), 123: (19, 9),

      127: (19, 9), 129: (19, 9), 130: (19, 9), 131: (19, 9), 133: (19, 9), 135: (19, 9), 136: (19, 9), 137: (19, 9), 139: (19, 9), 140: (19, 9), 141: (19, 9),
      143: (19, 9), 145: (19, 9), 146: (19, 9), 147: (19, 9),
    },
  ]
  all_hls_accuracies = []
  all_pytorch_accuracies = []
  
  start_time = time()
  for type_option in type_options:
    try:
      if run_hls:
        # Set relevant flags in build_prj.tcl
        set_build_options(path=build_tcl_path_full, options=vars(args))

        modify_defines(path=defines_path, options=type_option, line_type='ap_fixed')

        clean_file(path=hls_layers_log_path)
        run_vivado_hls(hls_dir_path=hls_dir_path, build_tcl_path=build_tcl_path, quiet=args.quiet)
        
        # Set all flags in build_prj.tcl to 0
        set_build_options(path=build_tcl_path_full, options=vars(args), disable_all=True)
      
      if args.csim:
        print('CSimulation:', end=' ')

        csim_results = get_hls_results(path=csim_results_log_path)
        labels = get_hls_results(path=labels_path)
        average_MSE, accuracy_pytorch, accuracy_hls = compare_results(hls_results=csim_results, pytorch_results=pytorch_results, labels=labels, quiet=args.quiet)

        print(f'\tAverage MSE: {average_MSE:.5f}, accuracy (PyTorch): {accuracy_pytorch*100:.2f}% , accuracy (HLS): {accuracy_hls*100:.2f}%')
        all_hls_accuracies.append(accuracy_hls)
        all_pytorch_accuracies.append(accuracy_pytorch)


      if args.cosim:
        print('\nRTL Co-simulation ')

        cosim_results = get_hls_results(path=rtl_cosim_results_log_path)
        pytorch_results = get_pytorch_results(path=pytorch_results_log_path)
        labels = get_hls_results(path=labels_path)
        average_MSE, accuracy_pytorch, accuracy_hls = compare_results(hls_results=cosim_results, pytorch_results=pytorch_results, labels=labels, quiet=args.quiet)

        print(f'\tAverage MSE: {average_MSE:.5f}, accuracy (PyTorch): {accuracy_pytorch*100:.2f}% , accuracy (HLS): {accuracy_hls*100:.2f}%')

    except KeyboardInterrupt:
      print(f'Skipping run since KeyboardInterrupt was raised')


  end_time = time()
  print(f'Running analysis took {(end_time - start_time) / 3600:.3f} h')

  date = datetime.now().strftime('%d-%m_%H-%M')
  pickle_path = f'logs/type_exploration_{date}.pickle'
  with open(pickle_path, 'wb') as f:
    pickle.dump((all_hls_accuracies, all_pytorch_accuracies, type_options), f)

  custom_plot(accuracies=all_hls_accuracies, widths=type_options, use_total_widths=True, path=pickle_path.replace('pickle', 'png'))


if __name__ == '__main__':
  
  args, run_hls = parse()
  
  if args.load is None:
    main(args=args, run_hls=run_hls)
  
  else:
    opt_fmt = lambda d: ' '.join([f'L{k}: ap_fixed<{v[0]},{v[1]}>' if isinstance(v, tuple) else (f'L{k}: EMBEDDED_DIM = {v}' if i == 0 else f'L{k}: SCALE_SHIFT = {v}') for i, (k, v) in enumerate(d.items())])
    
    with open(args.load, 'rb') as f:
      loaded_results = pickle.load(f)

    if not args.quiet:
      print(f'Loaded pickled results from {args.load}')
      print(f'Collected results:\n')

      all_hls_accuracies, all_pytorch_accuracies, type_options = loaded_results
      for hls_accuracy, pytorch_accuracy, type_option in zip(all_hls_accuracies, all_pytorch_accuracies, type_options):
        print('Options:')
        print(f'{opt_fmt(type_option)}\n')
        print(f'Accuracy (HLS): {hls_accuracy*100:.2f}%, accuracy (PyTorch): {pytorch_accuracy*100:.2f}%\n')

    custom_plot(accuracies=all_hls_accuracies, widths=type_options, use_total_widths=True, path=args.load.replace('pickle', 'png'))

    if not args.quiet:
      print('All results displayed, quitting...')

