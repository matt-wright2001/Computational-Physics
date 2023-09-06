#
# integration errors for trapezoid integration
# RT Clay 2023
#
from math import sqrt
# the function to integrate
def funct(x):
    return sqrt(x)
# trapezoid rule integration
# n : number of integration points
# min : lower limit
# max : uppper limit
#
# a function f(x) must be defined
def trap(n, min, max):
    dx = (max - min) / (n-1)
    sum = 0.0
    # sum points inside interval
    for i in range(1, n - 1):
        x = min + dx * i
        sum += funct(x)
    # add endpoints
    sum += (funct(min) + funct(max))/2
    sum *= dx
    return sum
# main program
# limits and exact value of integral (used to calculate error)
#
# int_1^2 \sqrt{x}dx = \frac{2}{3}(2^{3/2} - 1)
#
def trapIntMain():
    a = 1.0
    b = 2.0
    exact = 2.0/3.0*(2**(1.5) - 1.0)

    for i in range(3,10000,2):
        r = trap(i, a, b)
        r = abs(r - exact)
        print('{:6d} {:.12e}'.format(i,r))

    # for larger N, skip some values to save time
    for i in range(1001,3000000,10000):
        r = trap(i, a, b)
        r = abs(r - exact)
        print('{:6d} {:.12e}'.format(i,r))