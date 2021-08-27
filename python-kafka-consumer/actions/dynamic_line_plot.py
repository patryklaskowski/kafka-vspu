"""
Live plot action for notification system of VSPU project
Plots stream of incoming data provided by callable object.
Possible to set limit value (both static and dynamic).

pip install matplotlib

@author: Patryk Jacek Laskowski
"""
# TODO: Make sure negative values won't cause problems
# TODO: Make DynamicLinePlot dockerable using Dash Plotly and exposing feature as web app

import matplotlib
import matplotlib.pyplot as plt

from datetime import datetime
from matplotlib.animation import FuncAnimation
from collections import deque


class DynamicLinePlot:

    matplotlib.use('macosx')
    plt.style.use('fivethirtyeight')
    label_font_size = 13

    def __init__(self, func, limit=None, window_size=30, time_format='%H:%M:%S', limit_func=None, interval_ms=500):
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
        self.interval_ms = interval_ms
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
        plt.plot(self.y, label=f'{type(self.func).__name__}', lw=3)

        # Text annotation
        last_x, last_x_y = len(self.y) - 1, self.y[-1]
        plt.scatter(last_x, last_x_y)
        plt.text(last_x, last_x_y, f'value: {self.y[-1]}\n{self.x_labels[-1]}', size=self.label_font_size)

        # Limits
        # y_upper_lim: self.margin% above limit or self.margin% above highest datapoint
        if self.limit or self.limit_func:
            limit = self._limit_value()
            self.limit_values.append(limit)
            plt.plot(self.limit_values, label=f'Limit: {limit}', color='red')

            # Limit value text annotation
            last_x, last_lim_y = len(self.y) - 1, self.limit_values[-1]
            plt.scatter(last_x, last_lim_y)
            plt.text(last_x, last_lim_y, f'value: {self.y[-1]}', size=self.label_font_size)

            recently_max_lim = max(self.limit_values)
            y_upper_lim = int(recently_max_lim + recently_max_lim * self.margin) \
                if max(self.y) < recently_max_lim else\
                int(max(self.y) + max(self.y) * self.margin)
        else:
            y_upper_lim = int(max(self.y) + max(self.y) * self.margin)

        plt.ylim(0, y_upper_lim)

        # Labels
        plt.xticks(range(len(self.y)), self.x_labels)
        plt.xticks(rotation=45, ha='right', size=self.label_font_size)
        plt.yticks(size=self.label_font_size)

        plt.title(f'Window size: {self.window_size}, Interval (ms): {self.interval_ms}', size=self.label_font_size)

        # Legend
        plt.legend(loc='upper left')

        plt.tight_layout()

    def run(self):
        """Blocking. Works only as a main thread"""
        print(f'Setting up {str(self)}')
        fig = plt.figure(figsize=(12, 8))
        self.animation = FuncAnimation(fig=fig,  # possibly also plt.gcf()
                                       func=self._plotting_function,
                                       interval=self.interval_ms)
        print('Running plot...')
        try:
            plt.show(block=True)
        except KeyboardInterrupt:
            print('Plot has been keyboard interrupted, closing...')
            plt.close(fig='all')
            raise KeyboardInterrupt
        except BaseException as e:
            raise BaseException('Unexpected exception occurred.') from e


if __name__ == '__main__':

    import random

    dlp = DynamicLinePlot(func=lambda: random.randint(0, 10), limit=None, window_size=50, limit_func=None)
    dlp.run()
