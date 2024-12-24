import plotly.graph_objects as go

def create_plot(x, y, title="My Plot", x_label="X-axis", y_label="Y-axis"):
    """
    Membuat plot dengan Plotly.

    Args:
        x (list): Data untuk sumbu X.
        y (list): Data untuk sumbu Y.
        title (str): Judul plot.
        x_label (str): Label untuk sumbu X.
        y_label (str): Label untuk sumbu Y.

    Returns:
        str: HTML dari plot.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name='Data'))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label
    )
    return fig.to_html(full_html=False)
