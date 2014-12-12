#!/Users/nicolasaunai/anaconda/bin/python
# encoding: utf-8



import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np



class Zones(object):
    """
    this class allows the user to draw rectangular zones
    across several axes and get the corresponding intervals
    """

    #==========================================================
    #==========================================================
    def __init__(self,axes, nbzones=4):
        """create an area made of 'nbzone' zone

        @param nbzones : max number of rectangular zones to be drawn
        @param axes    : one or several axes in a list [ax1,]

        Exemple  : Zone(axes, nbzones=5)

        Creation : 2013-11-13 09:08:45.239114

        """

        self.axes    = axes                 # the list of axes
        self.fig     = axes[0].figure       # the (only) associated figure

        # events : press, released, motion
        self.pressid = self.fig.canvas.mpl_connect('button_press_event',
                                                    self._on_click)
        self.releaid = self.fig.canvas.mpl_connect('button_release_event',
                                                    self._on_release)
        self.motioid = self.fig.canvas.mpl_connect('motion_notify_event',
                                                    self._on_motion)

        self.evaxenid = self.fig.canvas.mpl_connect('axes_enter_event',
                                                     self._on_axenter)
        self.evaxlvid = self.fig.canvas.mpl_connect('axes_leave_event',
                                                     self._on_axleave)

        # allows to move the rectangle only when button is pressed
        self._is_pressed = False
        self._isonaxe = False

        #will count the number of defined zones
        self.count = 0
        self.nbzones = nbzones  # max number of defined zones

        # will store the defined intervals
        self.intervals = np.ndarray(shape=(nbzones,2))
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
    def _on_click(self,event):
        """on_click event
        Creation : 2013-11-13 09:13:37.922407

        """

        if self._isonaxe == True:

            self._is_pressed = True    # the button is now defined as pressed

            # store the rectangles for all axes
            # this will be useful because other events will loop on them
            self.rects   = []

            # for now loop on all axes and create one set of identical rectangles
            # on each one of them
            # the width of the rect. is something tiny like 1e-5 to give the
            # impression that it has 0 width before the user moves the mouse
            for ax in self.axes:
                self.rects.append(Rectangle((event.xdata,ax.get_ylim()[0]),
                                            1e-5, ax.get_ylim()[1]-ax.get_ylim()[0],
                                            alpha=0.3,
                                            color='g'))

                # add the rectangle to the current ax
                ax.add_artist(self.rects[-1])

            self.bckgs = []
            for ax in self.axes:
                self.bckgs.append(self.fig.canvas.copy_from_bbox(ax.bbox))

            # the set of rectangles is created for all axes
            # now draw them
            self.fig.canvas.draw()

    #==========================================================




    #==========================================================
    #==========================================================
    def _on_release(self,event):
        """on_release event
        Creation : 2013-11-13 09:18:04.246367
        """

        if self._isonaxe ==True:

            self._is_pressed = False # the button is now released

            # now we loop on all the rects defined last click
            # and we change their width according to the current
            # position of the cursor and x0
            for rect in self.rects:
                rect.set_width(event.xdata - rect.get_x())

            # all rects. have been updated so draw them
            self.fig.canvas.draw()

            # now store the interval and increment the
            # total number of defined zones
            self.intervals[self.count,0] = rect.get_x()
            self.intervals[self.count,1] = event.xdata
            self.count+=1

            # if we have reached the max number of zones
            # then we stop listening to events
            if self.count == self.nbzones:
                self.fig.canvas.mpl_disconnect(self.pressid)
                self.fig.canvas.mpl_disconnect(self.releaid)
                self.fig.canvas.mpl_disconnect(self.motioid)
                print 'all intervals defined!'
        #==========================================================




    #==========================================================
    #==========================================================
    def _on_motion(self,event):
        """ on_motion event
        Creation : 2013-11-13 09:21:59.747476

        """
        if self._isonaxe ==True:

            # this event must apply only when the mouse button is pressed
            if self._is_pressed == True:

                # we loop over rectangles of this click
                # and update their width according to the current
                # position of the cursor
                for ax,rect,bckg in zip(self.axes,self.rects,self.bckgs):
                    self.fig.canvas.restore_region(bckg)
                    rect.set_width(event.xdata  - rect.get_x())
                    ax.draw_artist(rect)
                    #self.fig.canvas.blit(rect.clipbox)

                self.fig.canvas.blit(self.fig.bbox)

    #==========================================================



    #==========================================================
    #==========================================================
    def get_intervals(self):
        """ returns an array of all the intervals (zones)
        @return: ndarray shape = (nbzones,2)

        Exemple  : intervals = myzones.get_intervals()

        Creation : 2013-11-13 09:23:44.147194

        """
        self.intervals.sort() # we want x0 < x1
        return self.intervals
    #==========================================================




def main():
    fig = plt.figure()
    ax1 = fig.add_subplot(411)
    ax2 = fig.add_subplot(412)
    ax3 = fig.add_subplot(413)
    ax4 = fig.add_subplot(414)

    axes = [ax1,ax2,ax3,ax4]

    for ax in axes:
        ax.set_xlim((0,10))
        ax.set_ylim((0,10))

    z = Zones(axes, nbzones=6)

    plt.show()

    return z



if __name__ == '__main__':
    main()





