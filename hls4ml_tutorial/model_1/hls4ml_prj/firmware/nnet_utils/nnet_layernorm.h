//
//    rfnoc-hls-neuralnet: Vivado HLS code for neural-net building blocks
//
//    Copyright (C) 2017 EJ Kreinar
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

#ifndef NNET_LAYERNORM_H_
#define NNET_LAYERNORM_H_

#include "nnet_common.h"
#include "nnet_dense.h"
#include "hls_stream.h"
#include <math.h>

namespace nnet {

struct layernorm_config
{
    // Internal data type definitions
    typedef float bias_t;
    typedef float scale_t;
    // typedef float inverse_count_t;

    // Layer Sizes
    static const unsigned n_in = 10;
    static const unsigned n_filt = -1;
    // inverse_count_t inverse_count = 0.1;

    // Resource reuse info
    static const unsigned io_type = io_parallel;
    static const unsigned reuse_factor = 1;
    static const bool store_weights_in_bram = false;
    static const unsigned n_zeros = 0;
    // partitioning arrays cyclically to go with roll factors?
    template<class x_T, class y_T, class res_T>
    using product = nnet::product::mult<x_T, y_T, res_T>;
};

template<class data_T, class res_T, typename CONFIG_T>
void layer_normalize(
    data_T    data[CONFIG_T::n_in],
    res_T     res[CONFIG_T::n_in],
    typename CONFIG_T::scale_t  scale[CONFIG_T::n_in],
    typename CONFIG_T::bias_t   bias[CONFIG_T::n_in]
)
{
    data_T cache;
   
    // Use a function_instantiate in case it helps to explicitly optimize unchanging weights/biases
    #pragma HLS function_instantiate variable=scale,bias

    if (CONFIG_T::io_type == io_parallel) {
        // For parallel inputs:
        //   - completely partition arrays -- target fabric
        //   - if we have an unroll factor, limit number of multipliers
        #pragma HLS PIPELINE II=CONFIG_T::reuse_factor

        // #pragma HLS ARRAY_PARTITION variable=weights complete // remove this line for now, it breaks compression sometimes
        #pragma HLS ARRAY_PARTITION variable=scale complete
        #pragma HLS ARRAY_PARTITION variable=bias complete

        int multiplier_limit  = ceil(float(CONFIG_T::n_in) / float(CONFIG_T::reuse_factor));
        CONFIG_T::template product<data_T, typename CONFIG_T::scale_t, res_T>::limit(multiplier_limit);

    } else if (CONFIG_T::io_type == io_serial) {
        #pragma HLS ARRAY_RESHAPE variable=scale complete dim=1
        #pragma HLS ARRAY_RESHAPE variable=bias complete dim=1
        #pragma HLS DATAFLOW
    }

    // Calculate mean
    data_T mean = (data_T) 0.0;
    Mean: for (int imean = 0; imean < CONFIG_T::n_in; imean++) {
      mean += data[imean];
    }
    // mean *= CONFIG_T::inverse_count;
    mean /= CONFIG_T::n_in;

    // Calculate variance
    data_T var = (data_T) 0.0;
    Var: for (int ivar = 0; ivar < CONFIG_T::n_in; ivar++) {
        data_T curr_diff = data[ivar] - mean;
        var += CONFIG_T::template product<data_T, data_T, data_T>::product(curr_diff, curr_diff);
    }
    var /= (CONFIG_T::n_in - 1);

    // Calculate result
    data_T eps = (data_T) 0.00001;
    data_T denominator = std::sqrt(var + eps);
    Result: for (int ires = 0; ires < CONFIG_T::n_in; ires++) {
        if (CONFIG_T::io_type == io_serial){
            #pragma HLS UNROLL
            #pragma HLS PIPELINE
        }
        
        data_T numerator = data[ires] - mean;
        numerator /= denominator;
        if (CONFIG_T::n_filt==-1) {
            res[ires] = CONFIG_T::template product<data_T, typename CONFIG_T::scale_t, res_T>::product(numerator, scale[ires]) + bias[ires];
	    } else {
            int norm_index = ires%CONFIG_T::n_filt;
            res[ires] = CONFIG_T::template product<data_T, typename CONFIG_T::scale_t, res_T>::product(numerator, scale[norm_index]) + bias[norm_index];
        }
	}
}

}

#endif