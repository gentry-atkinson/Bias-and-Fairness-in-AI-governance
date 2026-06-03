"""Plotting helpers for reusable EDA charts."""


def apply_axis_labels(axis, title, x_label, y_label):
    """Set common axis labels for reusable figures."""

    axis.set_title(title)
    axis.set_xlabel(x_label)
    axis.set_ylabel(y_label)
    return axis