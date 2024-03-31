import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches

def leadlag(X):
    '''
    Returns lead-lag-transformed stream of X

    Arguments:
        X: list, whose elements are tuples of the form
        (time, value).

    Returns:
        list of points on the plane, the lead-lag
        transformed stream of X
    '''

    l=[]

    for j in range(2*(len(X))-1):
        i1=j//2
        i2=j//2
        if j%2!=0:
            i1+=1
        l.append((X[i1][1], X[i2][1]))

    return l

def timejoined(X):
    '''
    Returns time-joined transformation of the stream of
    data X

    Arguments:
        X: list, whose elements are tuples of the form
        (time, value).

    Returns:
        list of points on the plane, the time-joined
        transformed stream of X
    '''
    X.append(X[-1])
    l=[]

    for j in range(2*(len(X))+1+2):
            if j==0:
                    l.append((X[j][0], 0))
                    continue
            for i in range(len(X)-1):
                    if j==2*i+1:
                            l.append((X[i][0], X[i][1]))
                            break
                    if j==2*i+2:
                            l.append((X[i+1][0], X[i][1]))
                            break
    return l

def plottimejoined(X):
    '''
    Plots the time-joined transfomed path X.

    Arguments:
        X: list, whose elements are tuples of the form (t, X)
    '''

    for i in range(len(X)-1):
        plt.plot([X[i][0], X[i+1][0]], [X[i][1], X[i+1][1]],
                color='k', linestyle='-', linewidth=2)

    axes=plt.gca()
    axes.set_xlim([min([p[0] for p in X]), max([p[0] for p
                  in X])+1])
    axes.set_ylim([min([p[1] for p in X]), max([p[1] for p
                  in X])+1])
    axes.get_yaxis().get_major_formatter().set_useOffset(False)
    axes.get_xaxis().get_major_formatter().set_useOffset(False)
    axes.set_aspect('equal', 'datalim')
    plt.show()