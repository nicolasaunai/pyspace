import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor
import numpy as np






class SynchedMultiCursor(MultiCursor):
    def __init__(self, *args, **kwargs):
        self._enabled = True
        MultiCursor.__init__(self, *args, **kwargs)

    def onmove(self, event):
        if self._enabled:
            MultiCursor.onmove(self, event)

    def enable(self):
        self._enabled = True
        self.clear(None) # Recapture the new background

    def disable(self):
        self._enabled = False
        if self.background is not None:
            self.canvas.restore_region(self.background)







class Zones(object):
    """
    this class allows the user to draw rectangular zones
    across several axes and get the corresponding intervals
    """



    def __init__(self,axes, nbzones=4):
        """create an area made of 'nbzone' zone

        @param nbzones : max number of rectangular zones to be drawn
        @param axes    : one or several axes in a list [ax1,]

        Exemple  : Zone(axes, nbzones=5)

        Creation : 2013-11-13 09:08:45.239114
        """
        self.axes    = axes                 # the list of axes
        self.fig     = axes[0].figure       # the (only) associated figure

        self.cursor = SynchedMultiCursor(self.fig.canvas, self.axes)

        # events : press, released, motion
        self.pressid = self.fig.canvas.mpl_connect('button_press_event',
                                                    self._on_click)
        self.releaid = self.fig.canvas.mpl_connect('button_release_event',
                                                    self._on_release)
        self.motioid = self.fig.canvas.mpl_connect('motion_notify_event',
                                                    self._on_motion)

        #will count the number of defined zones
        self.count = 0
        self.nbzones = nbzones  # max number of defined zones

        # will store the defined intervals
        self.intervals = np.ndarray(shape=(nbzones,2))


        self.enabled = False
        self.ispressed = False


    def _on_click(self,event):
        if event.inaxes not in self.axes:
            return

        if self.enabled == True:

            self.cursor.disable()
            # It's easier to use `axvspan` than a rectangle, i.m.o.
            # The main advantage is that this will always span the full y-range
            # even if the user later pans/zooms the plot
            region = lambda ax: ax.axvspan(event.xdata, event.xdata + 1e-5,
                                           alpha=0.3, color='green')
            self.rects = [region(ax) for ax in self.axes]
            self._draw_rects()

            # Save the background of each axes
            canvas = self.fig.canvas
            self.bckgs = [canvas.copy_from_bbox(ax.bbox) for ax in self.axes]

            self.ispressed = True



    def _update_rects(self, event):
        """Updates the width of the selected region on all axes based on a
        mouse motion event."""
        for rect in self.rects:
            xy = rect.get_xy()
            xy[2:4, 0] = event.xdata
            rect.set_xy(xy)

        return xy[0,0], event.xdata



    def _draw_rects(self):
        """Draws the selected region on all axes."""
        for ax, rect in zip(self.axes, self.rects):
            ax.draw_artist(rect)



    def _on_release(self,event):

        if self.enabled == True:

            if event.inaxes in self.axes:
                x0, x1 = self._update_rects(event)

                # now store the interval and increment the
                # total number of defined zones
                self.intervals[self.count,:2] = x0, x1
                self.count+=1

                # if we have reached the max number of zones
                # then we stop listening to events
                if self.count == self.nbzones:
                    self.fig.canvas.mpl_disconnect(self.pressid)
                    self.fig.canvas.mpl_disconnect(self.releaid)
                    self.fig.canvas.mpl_disconnect(self.motioid)
                    print 'all intervals defined!'

                self.cursor.enable()
                self.ispressed = False



    def _on_motion(self,event):
        """ on_motion event
        Creation : 2013-11-13 09:21:59.747476
        """
        if event.inaxes not in self.axes:
            return

        if self.enabled == True:

            # this event must apply only when the mouse button is pressed
            #if event.button is not None:
            if self.ispressed == True:
                for bckg in self.bckgs:
                    self.fig.canvas.restore_region(bckg)

                self._update_rects(event)
                self._draw_rects()

                self.fig.canvas.blit(self.fig.bbox)



    def get_intervals(self):
        """ returns an array of all the intervals (zones)
        @return: ndarray shape = (nbzones,2)

        Exemple  : intervals = myzones.get_intervals()

        Creation : 2013-11-13 09:23:44.147194
        """
        self.intervals.sort() # we want x0 < x1
        return self.intervals


    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False



def main():
    fig, axes = plt.subplots(nrows=4)

    for ax in axes:
        ax.axis([0, 10, 0, 10])

    z = Zones(axes, nbzones=6)

    plt.show()
    return z

if __name__ == '__main__':
    main()




