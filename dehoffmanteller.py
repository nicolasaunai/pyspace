
import numpy as np
from scipy import linalg

def deHoffmanTeller(B,E):

    a = np.mean(B[:,1]**2+B[:,2]**2)
    b = np.mean(-B[:,0]*B[:,1])
    c = np.mean(-B[:,0]*B[:,2])
    d = np.mean(-B[:,1]*B[:,2])
    e = np.mean(B[:,0]**2 + B[:,2]**2)
    f = np.mean(B[:,0]**2 + B[:,1]**2)

    mat = np.array([[a,b,c],
                    [b,e,d],
                    [c,d,f]])


    exb1 = np.mean(E[:,1]*B[:,2] - E[:,2]*B[:,1])
    exb2 = np.mean(E[:,2]*B[:,0] - E[:,0]*B[:,2])
    exb3 = np.mean(E[:,0]*B[:,1] - E[:,1]*B[:,0])

    ExB  = np.array([[exb1],[exb2],[exb3]])

    #print mat
    #print ExB

    matI = linalg.inv(mat)


    return np.dot(matI,ExB)



