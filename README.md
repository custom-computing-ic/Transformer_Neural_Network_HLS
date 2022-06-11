# Reconfigurable Acceleration of Transformer Neural Networks with Meta-Programming Strategies for Particle Physics Experiments
<<<<<<< HEAD
## How to run
Train or evaluate the Pytorch model:

`python3 pytorch/train_evaluate.py [-h] [--train] [--debug] [--timing] [--rng_seed] [--use_cpu]`

`--train`: train before evaluating

`--debug`: train/evaluate debug (prints each layer output) model

`--timing`: time evaluation

`--rng_seed`: randomize all seeds

`--use_cpu`: force CPU usage, even if GPU available

<br>
Extract weights and biases from a trained model:

`python3 scripts/extract_weights_biases.py`

For now no options, hard-coded to the existings paths.

<br>
Run Vivado HLS:

`python3 scripts/compare_hls_pytorch.py --run_hls`

For now no actual options, hard-coded to existing paths.

<br>

## TODO plan
- Scale HLS implementation to multiple particles data:
  - currently: batch size of 1 with 1 particle with 16 dimensions, (1, 1, 16) → (1, 5)
  - next: batch size of 1 with N particles with 16 dimensions, (1, N, 16) → (1, 5)

- Depending on latency/throughput findings, consider scaling HLS implementation to higher batch size:
  - planned: batch size of 1 with N particle with 16 dimensions, (1, N, 16) → (1, 5)
  - next: batch size of B with N particles with 16 dimensions, (B, N, 16) → (B, 5)

- Experiment and optimize with HLS implementation

- Implement self attention and transformer layers as auto generated code in hls4ml

- Instantiate ConstituentNetBase in HLS directly from Pytorch using hls4ml
=======

## Available programs
### Explore a Pytorch architecture

`python3 pytorch/train_evaluate.py <options>`

- `--particles <int>`: use dataset specific jet dataset (1, 30, 50, 100, 150)

- `--train`: train before evaluating

- `--debug`: train/evaluate debug (prints each layer output) model

- `--timing`: perform timing evaluation

- `--rng_seed`: randomize all seeds

- `--use_cpu`: force CPU usage, even if GPU available

- `--only_predictions`: only print predictions

- `--fetch`: refetch a dataset

- `--tiny_size <int>`: number of particles to use for debug (to select fewer particles than the dataset offers, e.g. 10 out of 30)

- `--epochs <int>`: epoch number to use for training and/or timing evaluation

- `--cuda <int>`: CUDA device ID (for machines with more than 1 GPU)

- `--generate_hls_tb <int>`: place specific number of input samples and PyTorch results as TB input and output for HLS

- `--flops`: perform FLOPS measurement

- `--norm_info <str>`: \[deprecated\] write summary of network's normalization layers



<br>

### Extract weights and biases from a trained model

`python3 scripts/extract_weights_biases.py <options>`

- `--debug`: use debug version of the Pytorch model


<br>

###  Run Vivado HLS

`python3 scripts/compare_hls_pytorch.py <options>`

- `--csim`: run C Simulation

- `--synth`: run C/RTL Synthesis

- `--cosim`: run RTL Cosimulation

- `--reset`: reset design

- `--pytorch`: run Pytorch model

- `--load <str>`: load pickled data and analyse it

- `--quiet`: supress outputs

<br>

###  Perform a post-training quantization

`python3 scripts/quantization_search.py <options>`

- `--quiet`: supress outputs

<br>

###  Generate precomputed log table for HLS

`python3 scripts/generate_log_table.py <options>`

- `--table_size <int>`: Number of elements (must be a power of 2)

- `--max_value <int>`: Biggest value used

- `--path <str>`: path of the resulting table

- `--var_name <str>`: name of the table variable

- `--var_type <str>`: HLS type of the table variable

- `--quiet`: supress outputs
>>>>>>> 9c0d86c28c83f71f1cb2ea0cb2e3aa899ae4e20c

<br>

## Repo structure
```
├─ fyp21yuan_code/                             # Yuan MSc code
│
<<<<<<< HEAD
├─ hls/
│   ├─ firmware/
│   │   ├─ nnet_utils/
│   │   │   ├─ nnet_activation.h               # SiLU, init_log_table, Log_softmax_latency
│   │   │   ├─ nnet_helpers.h                  # print_full_results
│   │   │   ├─ nnet_layernorm.h                # layer_normalize
│   │   │   ├─ nnet_merge.h                    # split_equally, join_equally, matmul
=======
├─ example_hls/                                # Tiny HLS design for testing Vivado HLS functions
│
├─ hls/
│   ├─ firmware/
│   │   ├─ nnet_utils/
│   │   │   ├─ nnet_activation.h               # log_softmax_latency, softmax_latency
>>>>>>> 9c0d86c28c83f71f1cb2ea0cb2e3aa899ae4e20c
│   │   │   ├─ nnet_self_attention.h           # self_attention
│   │   │   └─ nnet_transformer.h              # transformer
│   │   │
│   │   ├─ weights/                            # Weights and biases used in HLS
│   │   ├─ defines.h                           # typedef's, #define's
│   │   ├─ myproject.cpp                       # Implementation of ConstituentNetBase
│   │   ├─ myproject.h                         # Prototype of top-level function
│   │   └─ parameters.h                        # #include's, nnet struct redefinitions
│   │
│   ├─ tb_data/
<<<<<<< HEAD
│   │   ├─ csim_layer.log                      # CSimulation layer-by-layer output data
│   │   ├─ csim_result.log                     # CSimulation final output data (calculated)
│   │   ├─ tb_input_features.dat               # Input data
│   │   └─ tb_output_predictions.dat           # Output data (provided)
│   │
│   ├─ build_prj.tcl                           # Script for running CSimulation/Synthesis
│   └─ myproject_test.cpp                      # TB program for CSimulation
=======
│   │   ├─ csim_layer.log                      # C Simulation layer-by-layer output data
│   │   ├─ csim_result.log                     # C Simulation final output data (calculated)
│   │   ├─ tb_input_features.dat               # Input data
│   │   └─ tb_output_predictions.dat           # Output data (provided)
│   │
│   ├─ build_prj.tcl                           # Script for running C Simulation/Synthesis
│   └─ myproject_test.cpp                      # TB program for C Simulation
>>>>>>> 9c0d86c28c83f71f1cb2ea0cb2e3aa899ae4e20c
│
├─ pytorch/
│   ├─ data/                                   # Particles data
│   ├─ model/                                  # Modified ConstituentNet model files
│   └─ train_evaluate.py                       # Used to train and/or evaluate Pytorch model
│
├─ scripts/
│   ├─ compare_hls_pytorch.py                  # Runs and compares HLS vs Pytorch implementation
│   ├─ extract_weights_biases.py               # Extracts weights and biases from a Pytorch model
<<<<<<< HEAD
│   └─ playground.py                           # Used for testing and debugging Pytorch implementation
│
=======
│   ├─ quantization_search.py                  # Perform post-training quantization search
│   ├─ generate_log_table.py                   # Generate precomputed log table for HLS
│   └─ playground.py                           # Used for testing and debugging Pytorch implementation
│
├─ logs/                                       # All sorts of logs and images
│
├─ reports/                                    # Synthesis reports captured at different design stages
│
>>>>>>> 9c0d86c28c83f71f1cb2ea0cb2e3aa899ae4e20c
├─ thesis/                                     # Directory used for generating the LaTeX thesis
│
├─ .gitignore                                  # gitignore
└─ README.md                                   # This file
```

<br>

## Helpful links
https://fastmachinelearning.org/hls4ml/