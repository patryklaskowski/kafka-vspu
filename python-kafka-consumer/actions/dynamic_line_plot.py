import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from datetime import datetime
from matplotlib.animation import FuncAnimation
from collections import deque


class DynamicLinePlot:

    matplotlib.use('macosx')
    plt.style.use('fivethirtyeight')

    def __init__(self, func, limit=100, window_size=50, time_format='%H:%M:%S', limit_func=None):
        # func() has to return single number datapoint
        self.func = func
        self.limit = int(limit)
        self.limit_func = limit_func if callable(limit_func) else None
        self.time_format = time_format
        # Data containers
        self.y = deque(maxlen=window_size)
        self.limit_values = deque(maxlen=window_size)
        self.x_labels = deque(maxlen=window_size)

        self.ani = None
        self.margin = 0.1

    def _limit_value(self):
        if self.limit_func:
            return int(self.limit_func())
        return self.limit

    def _plotting_function(self, i):
        # get data
        datapoint = self.func() or 0
        self.y.append(datapoint)
        limit = self._limit_value()
        self.limit_values.append(limit)
        self.x_labels.append(datetime.now().strftime(self.time_format))

        # clear axis
        plt.cla()

        # Plot data
        plt.plot(self.y, label=f'{type(self.func).__name__}')
        plt.plot(self.limit_values, label=f'Limit: {limit}', color='red')

        # Text annotation
        last_x, last_y = len(self.y) - 1, self.y[-1]
        plt.scatter(last_x, last_y)
        plt.text(last_x, last_y + 1, f'value: {self.y[-1]}\n'
                                     f'{self.x_labels[-1]}')

        # Limits
        # self.margin% above limit or self.margin% above highest datapoint
        y_upper_lim = int(limit + limit * self.margin) if max(self.y) < limit else int(max(self.y) + max(self.y) * self.margin)
        plt.ylim(0, y_upper_lim)

        # Labels
        plt.xticks(range(len(self.y)), self.x_labels)
        plt.xticks(rotation=45, ha='right')

        # Legend
        plt.legend(loc='upper left')

        plt.tight_layout()

    def run(self, interval_ms=100):
        """Blocking. Works only as a main thread"""
        fig = plt.figure(figsize=(12, 8))
        self.ani = FuncAnimation(fig=plt.gcf(),
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

    # Static limit
    # Using static limit argument
    # dlp = DynamicLinePlot(func=lambda: np.random.randint(0, 10), limit=10, window_size=10)
    # dlp.run(interval_ms=10)

    # or

    # Dynamic limit
    # Using limit_func argument with connection to Redis Database
    #
    from functools import partial
    from utils.redis_db_connection import RedisConnection

    rc = RedisConnection()
    get_limit_or_13 = partial(rc.get, 'limit', 13)

    dlp = DynamicLinePlot(func=lambda: np.random.randint(0, 10),
                          limit_func=get_limit_or_13,
                          window_size=10)
    dlp.run(interval_ms=10)
