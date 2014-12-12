

# this module displays a vertical line on top of a list of axis
# at the cursor position

import numpy as np
import matplotlib.pyplot as plt


class CursorLine(object):

    #==========================================================
    #==========================================================
    def __init__(self, axes):
        """
        Creation : 2013-11-13 17:17:30.790306

        """
        self.axes     = axes
        self.fig      = axes[0].figure
        self.cursors  = []

        self.evmotid  = self.fig.canvas.mpl_connect('motion_notify_event',
                                                    self._on_motion)
        self.evaxenid = self.fig.canvas.mpl_connect('axes_enter_event',
                                                     self._on_axenter)
        self.evaxlvid = self.fig.canvas.mpl_connect('axes_leave_event',
                                                     self._on_axleave)
        self._isdrawn = False
        self._isonaxe = False
    #==========================================================


    #==========================================================
    #==========================================================
    def _on_axenter(self, event):
        """on ax enter event
        Creation : 2013-11-13 21:04:01.479037

        """
        self._isonaxe = True
    #==========================================================


    #==========================================================
    #==========================================================
    def _on_axleave(self, event):
        """on axe leave event
        Creation : 2013-11-13 21:04:40.550946

        """
        self._isonaxe = False
    #==========================================================


    #==========================================================
    #==========================================================
    def _on_motion(self, event):
        """o_nmotion event
        Creation : 2013-11-13 17:19:44.162194
        """

        if self._isonaxe == True:

            if self._isdrawn == False:
                for ax in self.axes:
                    ymin,ymax = ax.get_ylim()

                    line = plt.Line2D(np.array([event.xdata,event.xdata]),
                                      np.array([ymin,ymax]),
                                      color='k',linewidth=2)

                    ax.add_line(line)
                    self.cursors.append(line)

                self._isdrawn = True

            else:
                for line in self.cursors:
                    line.set_xdata(np.array([event.xdata,event.xdata]))

            self.fig.canvas.draw()

    #==========================================================




