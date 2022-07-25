from turtle import bgcolor
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot

class Dash:
    
    def __init__(self):
        pass
        
    def plot_gauge(self, value, title):
        data = go.Indicator(
                mode = "gauge + number",
                value = value,
                title = {'text': title, 'font': {'size': 20}},
                domain={'x': [0, 1], 'y': [0, 1]},
                number = {"font_size": 40},
                gauge= {
                    "bar": {"color": "#156064", "thickness": 0.5},
                    "steps": [
                        {"range": [0, value], "color": 'white'},
                        {"range": [0, value*1.5], "color": 'white'},
                    ],
                    "threshold": {
                        "line": {"color": "#D9D9D9", "width": 7},
                        "thickness": 0.8,
                        "value": 3,
                    }
                }
            )
        layout = go.Layout(
            margin=dict(l=50, r=50, t=50, b=50),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            height=300, width= 400  
        )
        return plot({'data': data, 'layout': layout},output_type='div', show_link=False, config=dict(displayModeBar=False))
        
    
    def plot_bar(self, x, y):
        data = go.Bar(
            x=x, 
            y=y,
            marker_color='rgb(0, 196, 154)', 
            marker_line_color='rgb(254, 113, 56)',
            marker_line_width=1.5,
            opacity=1, 
            orientation='h'
        )
        layout = go.Layout(
            xaxis_tickfont_size=14,
            yaxis=dict(
                titlefont_size=16,
                tickfont_size=14,
            ),
            width=600,
            height=600,
            margin=dict(l=5, r=5, t=10, b=10),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            # paper_bgcolor='rgba(0, 0, 0, 0)',
        )
        return plot({'data': data, 'layout': layout},output_type='div', show_link=False, config=dict(displayModeBar=False))
    
    def get_lead_line(self, event_ev, event_cs, tot):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=event_ev['date'],
            y=event_ev['client_id__count'],
            name='Lead EV'
        ))
        fig.add_trace(go.Scatter(
            x=event_cs['date'],
            y=event_cs['client_id__count'],
            name='Lead CS'
        ))
        fig.add_trace(go.Scatter(
            x=tot['date'],
            y=tot['total'],
            name='Total'
        ))
        fig.update_layout(
            title='Leads', 
            yaxis_title='Conversions',
            width=1200,
            height=800,
            margin=dict(l=5, r=5, t=40, b=10),
            plot_bgcolor='rgba(0, 0, 0, 0)',
        )
        return plot(fig, output_type='div', show_link=False, config=dict(displayModeBar=False))
