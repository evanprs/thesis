from xy_interpolation import *
from scipy.optimize import fmin


def evalTestFreq(flatpts):
    assert len(flatpts)%2==0
    x = flatpts[:len(flatpts)//2]
    y = flatpts[len(flatpts)//2:]
    pts = (x,y)
    try:
        s = make_shape(pts,max_output_len=50)
        fq, _, _ = find_eigenmodes(s, 5)
        fit = fitness(fq[:4],np.array([.5,1.0,1.5,2.0]) )
        return fit
    except ValueError:
        return 100

_, (x,y) = make_random_shape(5)
flatpts = np.append(x,y)
ptsopt = fmin(evalTestFreq,flatpts,maxfun=50)

x = ptsopt[:len(ptsopt)//2]
y = ptsopt[len(ptsopt)//2:]
curveopt = (x,y)
print('curveopt=',curveopt)
curve = make_shape(curveopt,max_output_len=50)
print(find_eigenmodes(curve, 5, showshape=True))
