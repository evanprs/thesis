from time import sleep
import optimize_grad
import pickle
import matplotlib.pyplot as plt
from xy_interpolation import make_shape

retvals = pickle.load(open('vals.p','rb'))
xopt = retvals[0]
allvecs = retvals[-1]
allpts = []
for vec in allvecs:
    x = vec[:len(vec) // 2]
    y = vec[len(vec) // 2:]
    allpts.append((x,y))

x0 = allpts[0][0]
y0 = allpts[0][1]

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)
line, = ax.plot(x0, y0, '-')
marks, = ax.plot(x0, y0, 'x')
for pts in allpts:    
    marks.set_xdata(pts[0])
    marks.set_ydata(pts[1])
    c = make_shape(pts)
    line.set_xdata(c[0])
    line.set_ydata(c[1])    
    plt.draw()
    # sleep(0.1)