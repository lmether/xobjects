import xobjects as xo

context = xo.ContextCpu()
buff = context._make_buffer(capacity=1024)

Float64_3 = xo.Float64[3]

arr1 = Float64_3([1,2,3], _buffer=buff)
arr2 = Float64_3([4,5,6], _buffer=buff)

class MyStructRef(xo.Struct):
    a = xo.Field(xo.Ref(Float64_3))

assert MyStructRef._size == 8

mystructref = MyStructRef(a=arr2, _buffer=buff)

assert mystructref._size == 8

for ii in range(3):
    assert mystructref.a[ii] == arr2[ii]

