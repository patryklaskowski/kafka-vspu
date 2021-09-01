import random
import os
import dash
import plotly
import dash_core_components as dcc
import dash_html_components as html

from itertools import cycle

import plotly.graph_objs as go

from datetime import datetime
from collections import deque
from dash.dependencies import Output, Input


class DashDynamicLinePlot:

    colors = {
        'background': '#18191A',
        'title': '#B0B3B3',
        'annot': '#969696',
        'plot_title': '#252525',
        'xticks': '#525252',
        'white': '#FFFFFF',
    }
    common_plot_kwargs = dict(line_shape='linear', mode='lines', connectgaps=True)
    time_format = '%H:%M:%S:%f'
    DEFAULT_VALUE = 0

    def __init__(self, func, limit_func=None, max_len=50, interval_ms=100):
        assert callable(func), 'func argument has to be callable'
        assert callable(limit_func) or limit_func==None, 'if specified, limit_func argument has to be callable'

        self.func = func
        self.limit_func = limit_func

        self.max_len = int(max_len)
        self.interval_ms = int(interval_ms)

        self.data = dict(y=deque(maxlen=max_len),
                         x=deque(maxlen=max_len),
                         limit=deque(maxlen=max_len))

        self.poll_new_data()

        # Gives flicker e.g. flickering red color effect using as color='rgb(255,{val},{val})
        self.c = cycle(list(range(0, 155+1, 15)) + list(range(155-1, 0-1, -15)))

        # Build app.
        self.app = dash.Dash(__name__, title='VSPU',
                             assets_folder=os.path.join(os.curdir, os.path.join('dash_assets')))
        self.app.layout = self.create_layout()
        self._create_callbacks()

    def run(self, host='0.0.0.0', port=8050, debug=False):
        self.app.run_server(host=host, port=port, debug=debug, threaded=True)

    def poll_new_data(self):
        """Update data"""
        self.data['y'].append(self.func() or self.DEFAULT_VALUE)
        self.data['x'].append(datetime.now().strftime(self.time_format))
        if self.limit_func:
            self.data['limit'].append(self.limit_func() or self.DEFAULT_VALUE)

    def _create_callbacks(self):
        """Creates callbacks"""
        @self.app.callback(Output('live-plot', 'figure'), [Input('interval-component', 'n_intervals')])
        def refresh(n):
            """Updates graph with new data"""
            self.poll_new_data()
            updated_fig = self.create_graph_figure()
            return updated_fig

    def upper_y_limit(self, margin=0.05):
        """Returns y-axis upper limit value. Used for proper y-axis visualization"""
        if self.limit_func:
            upper = max(max(self.data['limit']), max(self.data['y']))
        else:
            upper = max(self.data['y'])
        return int(upper + upper * margin)

    def lower_y_limit(self):
        """Returns y-axis lower limit value. Used for proper y-axis visualization"""
        if self.limit_func:
            lower = min(-1, min(self.data['y']))
        else:
            lower = min(-1, min(self.data['limit']), min(self.data['y']))
        return lower

    def create_layout(self):
        """
        Creates web page HTML layout (figure + structure = layout)
        """
        # 1) Figure
        fig = self.create_graph_figure()

        # 2) Plus structure
        structure = [
            html.H1(children=['VSPU: Action system - live plot'],
                    style={'color': self.colors['title'], 'padding': '50px', 'font-family': 'Arial', 'margin': 0}),

            dcc.Graph(id='live-plot', figure=fig, animate=False, config={'displayModeBar': False},
                      style={'color': self.colors['background'],
                             "width": "95%", 'padding-left': '2.5%', 'padding-right': '2.5%'}),

            html.P(children=['@Author: Patryk Jacek Laskowski'],
                   style={'color': self.colors['title'], 'padding': '50px', 'text-align': 'right', 'margin': 0, 'font-size': 13}),

            dcc.Interval(id='interval-component', interval=self.interval_ms),
        ]

        # 3) Equals layout
        layout = html.Div(children=structure,
                          style={'background-color': self.colors['background']})

        return layout

    def create_graph_figure(self):
        """
        Creates (graph) figure object of two line plots showing values, and (optional) limit.
        """
        fig = go.Figure()

        # Receive value for color flickering effect
        flicker = next(self.c)

        # Value line with marker at the end
        y_plot_kwargs = dict(name='Sum', line={'width': 3, 'color': 'royalblue'}, **self.common_plot_kwargs)
        fig.add_trace(go.Scatter(x=tuple(self.data['x']), y=tuple(self.data['y']), **y_plot_kwargs))
        fig.add_trace(go.Scatter(x=tuple(self.data['x'])[-1:], y=tuple(self.data['y'])[-1:],
                                 mode='markers',
                                 marker=dict(color=f'rgb({flicker},{flicker},255)', size=10),
                                 showlegend=False))

        fig.update_layout(
            xaxis_tickformat='%H:%M:%S',
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor=self.colors['xticks'],
                linewidth=1,
                tickangle=45,
                range=[-1, self.max_len],
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=9,
                    color=self.colors['xticks'],
                ),
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=True,
                showticklabels=True,
                range=[self.lower_y_limit(), self.upper_y_limit()],
            ),
            autosize=True,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            legend_title_text='',
            plot_bgcolor=self.colors['white'],
            paper_bgcolor=self.colors['white'],
        )

        annotations = []

        # Value line plot right-side annotations (shows the latest value)
        annotations.append(dict(x=len(self.data["y"])/self.max_len + 0.01, y=self.data["y"][-1],
                                text=f'sum: {self.data["y"][-1]}',
                                xref='paper', xanchor='left', yanchor='middle',
                                font=dict(family='Arial', size=16),
                                showarrow=False))
        # Plot title
        annotations.append(dict(x=0.0, y=1.05, text='sumTheAge output value',
                                xref='paper', yref='paper',
                                xanchor='left', yanchor='bottom',
                                font=dict(family='Arial', size=20, color=self.colors['plot_title']),
                                showarrow=False))

        if self.limit_func:
            # Flickering limit line plot with marker at the end
            limit_plot_kwargs = dict(name='Limit', line={'width': 5, 'color': f'rgb(255,{flicker},{flicker})'},
                                     **self.common_plot_kwargs)  # 'firebrick'
            fig.add_trace(plotly.graph_objs.Scatter(x=tuple(self.data['x']), y=tuple(self.data['limit']),
                                                    **limit_plot_kwargs))
            fig.add_trace(plotly.graph_objs.Scatter(x=tuple(self.data['x'])[-1:], y=tuple(self.data['limit'])[-1:],
                                                    mode='markers',
                                                    marker=dict(color=f'rgb(255,{flicker},{flicker})', size=10),
                                                    showlegend=False))
            # Limit line plot right-side annotations (shows the latest value)
            annotations.append(dict(x=len(self.data['limit'])/self.max_len + 0.01, y=self.data['limit'][-1],
                                    text=f'limit: {self.data["limit"][-1]}',
                                    xref='paper', xanchor='left', yanchor='middle',
                                    font=dict(family='Arial', size=16),
                                    showarrow=False))

        fig.update_layout(annotations=annotations)

        return fig


if __name__ == '__main__':

    get_limit = lambda: 30
    get_value = lambda: random.randint(-5, 60)

    plot = DashDynamicLinePlot(get_value, get_limit, 300)
    plot.run(port=8050)
