from numpy import empty

# Runge-Kutta-Fehlberb Method
def RKF(f, t, h, y, tol):
    a = [ 0.25, 0.375, 12/13, 1.0, 0.5]
    bk1 = [0.25]
    bk2 = [3/32, 9/32]
    bk3 = [1932/2197, -7200/2197, 7296/2197]
    bk4 = [439/216, -8, 3680/513, -845/4104]
    bk5 = [-8/27, 2, -3544/2565, 1859/4104, -11/40]
    c = [16/135, 0, 6656/12825, 28561/56430, -9/50, 2/55]
    ce = [1/360, 0, -128/4275, -2197/75240, 1/50, 2/55]

    k1 = h*f(y, t)
    k2 = h*f(y + k1*bk1[0], t + h*a[0])
    k3 = h*f(y + k1*bk2[0] + k2*bk2[1], t + h*a[1])
    k4 = h*f(y + k1*bk3[0] + k2*bk3[1] + k3*bk3[2], t + h*a[2])
    k5 = h*f(y + k1*bk4[0] + k2*bk4[1] + k3*bk4[2] + k4*bk4[3], t + h*a[3])
    k6 = h*f(y + k1*bk5[0] + k2*bk5[1] + k3*bk5[2] + k4*bk5[3] + k5*bk5[4], t + h*a[4])
    ynew = empty(len(y), float)
    for i in range(len(y)):
        # new solution using 5th order approximation
        ynew[i] = y[i] + k1[i]*c[0] + k3[i]*c[2] + k4[i]*c[3] + k5[i]*c[4] + k6[i]*c[5]
        # relative error estimate for this i
        err = abs((k1[i]*ce[0] + k3[i]*ce[2] + k4[i]*ce[3] + k5[i]*ce[4] + k6[i]*ce[5]) / ynew[i])
        # check for division by zero in case err underflows
        if err == 0.0:
            tmp = 2*h
        else:
            tmp = h*(tol/err)**0.2
        # find smallest suggested new stepsize
        if i==0:
            hnew = tmp
        elif tmp < hnew:
            hnew = tmp

    accept = False
    if hnew>h:
        # solution is within error; accept step, update stepsize
        y = ynew
        t += h
        h = hnew
        accept = True
    else:
        # error too large, decrease step size
        htry = hnew * 0.9
        if htry < HMIN:
            # below minimum stepsize, accept anyway
            y = ynew
            t += h
            h = HMIN
            accept = True
        else:
            # update h
            h = htry

    return y,t,h,accept