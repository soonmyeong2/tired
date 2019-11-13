import matplotlib.pyplot as plt
import numpy as np
from drawnow import drawnow


class MakeGraph:
    def __init__(self, x, y, mean):
        plt.ion()  # enable interactivity
        self.fig = plt.figure()  # make a figure
        self.x = x
        self.y = y
        self.idx = len(self.x)
        self.mean = [mean] * len(self.x)
        
                 
    def makeFig(self):
        plt.plot(self.x, self.y)  # I think you meant this
        plt.plot(self.x, self.mean)


    def makeDraw(self, y, mean):
        self.x.append(self.idx)
        self.y.append(y)  # or any arbitrary update to your figure's data
        self.x.pop(0)
        self.y.pop(0)
        self.idx += 1
        self.mean = [mean] * len(self.x)

        drawnow(self.makeFig)
       

# example       
'''
m = MakeGraph([10]*10, [20]*10, 10)

for i in range(1000):
    m.makeDraw(np.random.random(), np.random.random())
'''
    
