"""
Notification system action for VSPU project

@author: Patryk Jacek Laskowski
"""

import matplotlib
import matplotlib.pyplot as plt

from datetime import datetime
from matplotlib.animation import FuncAnimation
from collections import deque


class DynamicLinePlot:

    matplotlib.use('macosx')
    plt.style.use('fivethirtyeight')

    def __init__(self, func, limit=None, window_size=50, time_format='%H:%M:%S', limit_func=None):
        """

        Limit
        Static limit:
            use limit arg to set static limit value
        Dynamic limit:
            use limit_func to set dynamic limit behavior. limit_func argument has to be callable object.
            When limit_func is called single number needs to be returned.
        """
        # func() has to return single number datapoint
        self.func = func
        self.limit = limit and int(limit)
        self.limit_func = limit_func if callable(limit_func) else None
        self.time_format = time_format
        self.window_size = window_size
        # Data containers
        self.y = deque(maxlen=window_size)
        self.limit_values = deque(maxlen=window_size)
        self.x_labels = deque(maxlen=window_size)

        self.animation = None
        self.margin = 0.1

    def __str__(self):
        text = f'{self.__class__.__name__}'
        arguments = '\n'.join([f'- {key}={val}' for key, val in vars(self).items()])
        return '\n'.join([text, arguments])

    def _limit_value(self) -> int:
        """limit_func is superior to static limit value
        Returns int or raises an Exception"""
        if self.limit_func:
            limit = self.limit_func()  # This may cause delay if requires network connection
            return int(limit) if limit else 0
        return self.limit

    def _plotting_function(self, i):
        # get data
        datapoint = self.func() or 0
        self.y.append(datapoint)
        self.x_labels.append(datetime.now().strftime(self.time_format))

        # clear axis
        plt.cla()

        # Plot data
        plt.plot(self.y, label=f'{type(self.func).__name__}')

        # Text annotation
        last_x, last_y = len(self.y) - 1, self.y[-1]
        plt.scatter(last_x, last_y)
        plt.text(last_x, last_y, f'value: {self.y[-1]}\n'
                                 f'{self.x_labels[-1]}')

        # Limits
        # y_upper_lim: self.margin% above limit or self.margin% above highest datapoint
        if self.limit or self.limit_func:
            limit = self._limit_value()
            self.limit_values.append(limit)
            plt.plot(self.limit_values, label=f'Limit: {limit}', color='red')
            y_upper_lim = int(limit + limit * self.margin) if max(self.y) < max(self.limit_values) else\
                int(max(self.y) + max(self.y) * self.margin)
        else:
            y_upper_lim = int(max(self.y) + max(self.y) * self.margin)

        plt.ylim(0, y_upper_lim)

        # Labels
        plt.xticks(range(len(self.y)), self.x_labels)
        plt.xticks(rotation=45, ha='right')

        # Legend
        plt.legend(loc='upper left')

        plt.tight_layout()

    def run(self, interval_ms=100):
        """Blocking. Works only as a main thread"""
        print(f'Running {str(self)}')
        fig = plt.figure(figsize=(12, 8))
        self.animation = FuncAnimation(fig=fig,  # possibly also plt.gcf()
                                       func=self._plotting_function,
                                       interval=interval_ms)
        print('Running plot...')
        try:
            plt.show(block=True)
        except KeyboardInterrupt:
            print('Plot has been keyboard interrupted, closing...')
            plt.close(fig='all')
            raise KeyboardInterrupt


if __name__ == '__main__':

    import random

    dlp = DynamicLinePlot(func=lambda: random.randint(0, 10), limit=None, window_size=50)
    dlp.run(interval_ms=10)
