
import numpy as np
import cupy

source_str = r'''
extern "C"{

__global__
void mymul(int n,
    const double* x1, const double* x2, double* y)
{
    int tid = blockDim.x * blockIdx.x + threadIdx.x;
    if (tid < n)
    {
        y[tid] = x1[tid] * x2[tid];
    }
}

}'''
module = cupy.RawModule(code=source_str)
mymul_kernel = module.get_function('mymul')

x1 = np.array([1,2,3,4], dtype=np.float64)
x2 = np.array([7,8,9,10], dtype=np.float64)

x1_dev = cupy.array(x1)
x2_dev = cupy.array(x2)
y_dev = cupy.zeros_like(x1_dev)

mymul_kernel(grid=(1,), block=(len(x1),),
        args=(len(x1), x1_dev, x2_dev, y_dev))

y = y_dev.get()

assert np.allclose(y, x1*x2)


