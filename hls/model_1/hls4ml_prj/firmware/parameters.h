#ifndef PARAMETERS_H_
#define PARAMETERS_H_

#include "ap_int.h"
#include "ap_fixed.h"

#include "nnet_utils/nnet_helpers.h"
// #include "nnet_utils/nnet_mult.h"
//hls-fpga-machine-learning insert includes
#include "nnet_utils/nnet_activation.h"
#include "nnet_utils/nnet_activation_stream.h"
#include "nnet_utils/nnet_dense.h"
#include "nnet_utils/nnet_dense_compressed.h"
#include "nnet_utils/nnet_dense_stream.h"
#include "nnet_utils/nnet_batchnorm.h"
#include "nnet_utils/nnet_transformer.h"

#include "nnet_utils/nnet_merge.h"
#include "nnet_utils/nnet_mult.h"


//hls-fpga-machine-learning insert weights
#include "weights/cls_token.h"
#include "weights/inp_layer_weight.h"
#include "weights/inp_layer_bias.h"
#include "weights/out_layer_1_weight.h"
#include "weights/out_layer_1_bias.h"
#include "weights/transformers_0_self_attention_qkv_weight.h"
#include "weights/transformers_0_self_attention_out_weight.h"
#include "weights/transformers_0_self_attention_out_bias.h"
#include "weights/transformers_0_linear_2_weight.h"
#include "weights/transformers_0_linear_5_weight.h"

//------- TOP -------

struct embedded_config : nnet::dense_config {
    static const unsigned n_in = N_INPUT;
    static const unsigned n_out = N_EMBEDDED;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = (N_EMBEDDED * N_EMBEDDED);
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct concat_config0 : nnet::concat_config {
    static const unsigned n_elem1_0 = N_EMBEDDED_DIM;
    static const unsigned n_elem1_1 = 1;

    static const unsigned n_elem2_0 = N_EMBEDDED;
    static const unsigned n_elem2_1 = 1;

    static const unsigned axis = -1;
};

struct normalize_config0 : nnet::layernorm_config {
    // Internal data type definitions
    typedef model_default_t bias_t;
    typedef model_default_t scale_t;

    // Layer Sizes
    static const unsigned n_in = N_EMBEDDED_DIM;
    static const unsigned n_filt = -1;
    static const unsigned n_layers = 1;
    
    // Resource reuse info
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 1;
    static const bool store_weights_in_bram = false;
    static const unsigned n_zeros = 0;
    // partitioning arrays cyclically to go with roll factors?
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct mlp_config : nnet::dense_config {
    static const unsigned n_in = N_EMBEDDED_DIM;
    static const unsigned n_out = N_LABELS;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = (N_EMBEDDED_DIM * N_LABELS);
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct softmax_config0 : nnet::activ_config {
    static const unsigned n_in = N_LABELS;
    static const unsigned table_size = N_BIG_TABLE_SIZE;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 1;
    static const unsigned axis = -1;
    static const nnet::softmax_implementation implementation = nnet::softmax_implementation::latency;
    typedef general_table_t exp_table_t;
    typedef general_table_t inv_table_t;
    typedef general_table_t log_table_t;
};

//------- TOP -------

//------- TRANSFORMER -------

struct transformer_config0 : nnet::transformer_config {
    static const unsigned n_in = N_TRANSFORMER;
    static const unsigned n_out = N_TRANSFORMER;

    static const unsigned n_particles = (N_PARTICLES + 1);
    static const unsigned n_el = N_EMBEDDED_DIM;
    static const unsigned n_el_doubled = (N_EMBEDDED_DIM * 2);

    static const unsigned n_SA_norm_weight = N_EMBEDDED_DIM;
    static const unsigned n_SA_norm_bias = N_EMBEDDED_DIM;
    static const unsigned n_SA_QKV_weight = (N_EMBEDDED_DIM * 3 * N_EMBEDDED_DIM); // 3 x N_EMBEDDED_DIM -> N_EMBEDDED_DIM
    static const unsigned n_SA_dense_weight = (N_EMBEDDED_DIM * N_EMBEDDED_DIM); // N_EMBEDDED_DIM -> N_EMBEDDED_DIM
    static const unsigned n_SA_dense_bias = N_EMBEDDED_DIM;

    static const unsigned n_norm0_weight = N_EMBEDDED_DIM;
    static const unsigned n_norm0_bias = N_EMBEDDED_DIM;
    static const unsigned n_dense0_weight = (N_EMBEDDED_DIM * 2 * N_EMBEDDED_DIM); // N_EMBEDDED_DIM -> 2 x N_EMBEDDED_DIM
    static const unsigned n_norm1_weight = (N_EMBEDDED_DIM * 2);
    static const unsigned n_norm1_bias = (N_EMBEDDED_DIM * 2);
    static const unsigned n_dense1_weight = (N_EMBEDDED_DIM * N_EMBEDDED_DIM * 2); // 2 x N_EMBEDDED_DIM -> N_EMBEDDED_DIM

    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const bool store_weights_in_bram = false;

    typedef model_default_t accum_t;

    typedef model_default_t SA_norm_weight_t;
    typedef model_default_t SA_norm_bias_t;
    typedef model_default_t SA_QKV_weight_t;
    typedef model_default_t SA_dense_weight_t;
    typedef model_default_t SA_dense_bias_t;

    typedef model_default_t norm0_weight_t;
    typedef model_default_t norm0_bias_t;
    typedef model_default_t dense0_weight_t;
    typedef model_default_t norm1_weight_t;
    typedef model_default_t norm1_bias_t;
    typedef model_default_t dense1_weight_t;

    // typedef model_default_t bias_t;
    // typedef model_default_t scale_t;
    // typedef model_default_t norm1_bias_t;
    // typedef model_default_t norm1_weight_t;
    // typedef model_default_t ff_weight_t;
    // typedef model_default_t ff_bias_t;
    // typedef model_default_t Q_weight_t;
    // typedef model_default_t K_weight_t;
    // typedef model_default_t V_weight_t;
    // typedef model_default_t inv_sqrt_d_k_t;
    typedef model_default_t exp_table_t;
    typedef model_default_t inv_table_t;
    typedef model_default_t table_t;
    typedef model_default_t weight_t;
    typedef model_default_t data_T;
    typedef model_default_t res_T;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct normalize_config1 : nnet::layernorm_config {
    // Internal data type definitions
    typedef model_default_t bias_t;
    typedef model_default_t scale_t;

    // Layer Sizes
    static const unsigned n_in = N_EMBEDDED_DIM;
    static const unsigned n_filt = -1;
    static const unsigned n_layers = (N_PARTICLES + 1);
    
    // Resource reuse info
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 1;
    static const bool store_weights_in_bram = false;
    static const unsigned n_zeros = 0;
    // partitioning arrays cyclically to go with roll factors?
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

// TODO rename sigmoid0 config to silu0 config? or just activ0 config?
struct sigmoid_config0 : nnet::activ_config {
    // IO size
    static const unsigned n_in = N_EMBEDDED_DIM;

    // Internal info
    static const unsigned table_size = N_SMALL_TABLE_SIZE;

    // Resource reuse info
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 1;

    // Internal data type definitions
    typedef general_table_t table_t;

    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct transformer_dense_config0 : nnet::dense_config {
    static const unsigned n_in = N_EMBEDDED_DIM;
    static const unsigned n_out = (N_EMBEDDED_DIM * 2);
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = (N_EMBEDDED_DIM * 2 * N_EMBEDDED_DIM);
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct normalize_config2 : nnet::layernorm_config {
    // Internal data type definitions
    typedef model_default_t bias_t;
    typedef model_default_t scale_t;

    // Layer Sizes
    static const unsigned n_in = (N_EMBEDDED_DIM * 2);
    static const unsigned n_filt = -1;
    static const unsigned n_layers = (N_PARTICLES + 1);
    
    // Resource reuse info
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 1;
    static const bool store_weights_in_bram = false;
    static const unsigned n_zeros = 0;
    // partitioning arrays cyclically to go with roll factors?
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct sigmoid_config1 : nnet::activ_config {
    // IO size
    static const unsigned n_in = (N_EMBEDDED_DIM * 2);

    // Internal info
    static const unsigned table_size = N_SMALL_TABLE_SIZE;

    // Resource reuse info
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 1;

    // Internal data type definitions
    typedef general_table_t table_t;

    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct transformer_dense_config1 : nnet::dense_config {
    static const unsigned n_in = (N_EMBEDDED_DIM * 2);
    static const unsigned n_out = N_EMBEDDED_DIM;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = (N_EMBEDDED_DIM * 2 * N_EMBEDDED_DIM);
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

//------- TRANSFORMER -------

//------- SELF ATTENTION -------

struct self_attention_config0 : nnet::self_attention_config {
    typedef model_default_t norm_weight_t;
    typedef model_default_t norm_bias_t;
    typedef model_default_t QKV_weight_t;
    typedef model_default_t dense_weight_t;
    typedef model_default_t dense_bias_t;

    static const unsigned n_norm_weight = N_EMBEDDED_DIM;
    static const unsigned n_norm_bias = N_EMBEDDED_DIM;
    static const unsigned n_QKV_weight = (N_EMBEDDED_DIM * 3 * N_EMBEDDED_DIM);
    static const unsigned n_dense_weight = (N_EMBEDDED_DIM * N_EMBEDDED_DIM);
    static const unsigned n_dense_bias = N_EMBEDDED_DIM;

    // Internal data type definitions
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef model_default_t accum_t;

    typedef model_default_t inv_sqrt_d_k_t;
    
    // static const inv_sqrt_d_k_t inv_sqrt_d_k = 0.0883883476483; //TODO:

    // Layer Sizes
    static const unsigned n_in = N_TRANSFORMER;
    static const unsigned n_out = N_TRANSFORMER;

    static const unsigned n_particles = (N_PARTICLES + 1);

    static const unsigned n_norm_el = N_EMBEDDED_DIM;
    static const unsigned n_el = N_EMBEDDED_DIM;

    static const unsigned n_qkv_in_el = N_EMBEDDED_DIM;
    static const unsigned n_qkv_out_el = (N_EMBEDDED_DIM * 3);

    static const unsigned n_qkv = (N_EMBEDDED_DIM * 3 * (N_PARTICLES + 1));
    static const unsigned n_q = N_EMBEDDED_DIM;
    static const unsigned n_k = N_EMBEDDED_DIM;
    static const unsigned n_v = N_EMBEDDED_DIM;
    static const unsigned n_energy = (2 * (N_PARTICLES + 1));
    static const unsigned n_attention = (N_PARTICLES + 1);
    static const unsigned n_scaled_attention = N_EMBEDDED_DIM;

    // Resource reuse info
    static const unsigned io_type =  nnet::io_parallel;
    static const unsigned strategy =  nnet::latency; 
    static const unsigned reuse_factor = 1;
    static const bool store_weights_in_bram = false;
    static const unsigned n_zeros = 0;
    // partitioning arrays cyclically to go with roll factors?
    // Product function to use
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct sa_norm_config0 : nnet::layernorm_config {
    // Internal data type definitions
    typedef model_default_t bias_t;
    typedef model_default_t scale_t;

    // Layer Sizes
    static const unsigned n_in = N_EMBEDDED_DIM;
    static const unsigned n_filt = -1;
    static const unsigned n_layers = (N_PARTICLES + 1);
    
    // Resource reuse info
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 1;
    static const bool store_weights_in_bram = false;
    static const unsigned n_zeros = 0;
    // partitioning arrays cyclically to go with roll factors?
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct sa_dense_config0 : nnet::dense_config {
    static const unsigned n_in = N_EMBEDDED_DIM;
    static const unsigned n_out = (N_EMBEDDED_DIM * 3);
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = (N_EMBEDDED_DIM * 3 * N_EMBEDDED_DIM);
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct sa_transpose_config0 : nnet::transpose_config {
    static const unsigned height = (N_EMBEDDED_DIM / 2);
    static const unsigned width = 2;
};

// TODO, THIS IS REPLACED BY MATMUL 
struct sa_dense_config1 : nnet::dense_config {
    static const unsigned n_in = 128;
    static const unsigned n_out = 4;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = 128;
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct sa_softmax_config0 : nnet::activ_config {
    static const unsigned n_in = 2;
    static const unsigned table_size = N_BIG_TABLE_SIZE;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 1;
    static const unsigned axis = -1;
    static const nnet::softmax_implementation implementation = nnet::softmax_implementation::latency;
    typedef general_table_t exp_table_t;
    typedef general_table_t inv_table_t;
};

// TODO, THIS IS REPLACED BY MATMUL 
struct sa_dense_config2 : nnet::dense_config {
    static const unsigned n_in = 4;
    static const unsigned n_out = 128;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = 128;
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

struct sa_dense_config3 : nnet::dense_config {
    static const unsigned n_in = N_EMBEDDED_DIM;
    static const unsigned n_out = N_EMBEDDED_DIM;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 0;
    static const unsigned n_nonzeros = (N_EMBEDDED_DIM * N_EMBEDDED_DIM);
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef model_default_t bias_t;
    typedef model_default_t weight_t;
    typedef ap_uint<1> index_t;
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

//------- SELF ATTENTION -------
#endif