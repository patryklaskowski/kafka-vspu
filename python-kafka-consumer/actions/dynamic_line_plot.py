import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from datetime import datetime
from matplotlib.animation import FuncAnimation
from collections import deque


class DynamicLinePlot:

    matplotlib.use('macosx')
    plt.style.use('fivethirtyeight')

    def __init__(self, func, fargs=None, limit=100, window_size=50, time_format='%H:%M:%S'):
        # func() has to return single number datapoint
        self.func = func
        self.limit = limit
        self.time_format = time_format
        # Data containers
        self.y = deque(maxlen=window_size)
        self.limit_values = deque(maxlen=window_size)
        self.x_labels = deque(maxlen=window_size)

        self.ani = None

    def _plotting_function(self, i):
        # get data
        datapoint = self.func() or 0
        self.y.append(datapoint)
        self.limit_values.append(self.limit)
        self.x_labels.append(datetime.now().strftime(self.time_format))

        # clear axis
        plt.cla()

        # Plot data
        plt.plot(self.y, label=f'{type(self.func).__name__}')
        plt.plot(self.limit_values, label=f'Limit: {self.limit}', color='red')

        # Text annotation
        last_x, last_y = len(self.y) - 1, self.y[-1]
        plt.scatter(last_x, last_y)
        plt.text(last_x, last_y + 1, f'value: {self.y[-1]}\n'
                                     f'{self.x_labels[-1]}')

        # Limits
        # 10% above limit or 10% above highest datapoint
        y_upper_lim = int(self.limit + self.limit * 0.1) if max(self.y) < self.limit else int(max(self.y) + max(self.y) * 0.1)
        plt.ylim(0, y_upper_lim)
        # 5% to the right
        # x_right_lim = int(len(self.x_labels) + len(self.x_labels) * 0.5)
        # plt.xlim(left=0, right=x_right_lim)

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

    class Xyz:

        def data_generator(self):
            print(f'id: {id(self)}')
            return np.random.randint(0, 10)

    consumer = Xyz()

    dlp = DynamicLinePlot(func=consumer.data_generator, limit=10, window_size=10)
    dlp.run(interval_ms=10)
