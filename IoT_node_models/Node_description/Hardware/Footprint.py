import numpy as np

LOW, MID, HIGH = 0, 1, 2


def _parse_factor(label, v):
    """Float -> (v, v, v); 3-sequence -> (low, mid, high), validated."""
    if np.isscalar(v):
        v = float(v)
        return (v, v, v)
    try:
        lo, mid, hi = (float(x) for x in v)
    except (TypeError, ValueError):
        raise ValueError(f"{label}: expected a float or a 3-entry (low, mid, high) sequence, got {v!r}")
    if not lo <= mid <= hi:
        raise ValueError(f"{label}: bounds must satisfy low <= mid <= high, got {(lo, mid, hi)}")
    return (lo, mid, hi)


class FootprintStructure:
    __slots__ = ("_labels", "_units", "_idx")

    def __init__(self, labels, units=None):
        labels = tuple(labels)
        if len(set(labels)) != len(labels):
            raise ValueError("Duplicate impact labels")
        units = tuple(units) if units is not None else ("",) * len(labels)
        if len(units) != len(labels):
            raise ValueError("units must match labels")
        self._labels = labels
        self._units = units
        self._idx = {l: i for i, l in enumerate(labels)}

    @property
    def labels(self):
        return self._labels

    @property
    def units(self):
        return self._units

    def __len__(self):
        return len(self._labels)

    def __repr__(self):
        return f"FootprintStructure({list(self._labels)})"

    def vector(self, values=None, **kwargs):
        """Missing labels default to 0. Each value is a float or (low, mid, high)."""
        values = {**(values or {}), **kwargs}
        unknown = set(values) - set(self._labels)
        if unknown:
            raise KeyError(f"Unknown impact labels: {sorted(unknown)}")
        data = np.zeros((len(self._labels), 3))
        for label, v in values.items():
            data[self._idx[label]] = _parse_factor(label, v)
        return FootprintVector(self, data)

    def zeros(self):
        return FootprintVector(self, np.zeros((len(self._labels), 3)))


class FootprintVector:
    __slots__ = ("structure", "data")

    def __init__(self, structure, data):
        data = np.asarray(data, dtype=float)
        if data.shape != (len(structure), 3):
            raise ValueError(f"data must have shape ({len(structure)}, 3), got {data.shape}")
        self.structure = structure
        self.data = data  # columns: low, mid, high

    # --- access -----------------------------------------------------------
    @property
    def low(self):
        return self.data[:, LOW]

    @property
    def mid(self):
        return self.data[:, MID]

    @property
    def high(self):
        return self.data[:, HIGH]

    @property
    def is_fixed(self):
        """Boolean mask: True where low == mid == high."""
        return (self.low == self.mid) & (self.mid == self.high)

    def __getitem__(self, label):
        return tuple(self.data[self.structure._idx[label]])

    def as_dict(self, which="bounds"):
        """which: 'bounds' -> {label: (lo, mid, hi)}; 'low'/'mid'/'high' -> {label: float}."""
        if which == "bounds":
            return {l: tuple(row) for l, row in zip(self.structure.labels, self.data.tolist())}
        col = {"low": LOW, "mid": MID, "high": HIGH}[which]
        return dict(zip(self.structure.labels, self.data[:, col].tolist()))

    # --- arithmetic (interval arithmetic on bounds) ------------------------
    def _check(self, other):
        if not isinstance(other, FootprintVector) or other.structure is not self.structure:
            raise ValueError("Impact vectors use different structures")

    def __add__(self, other):
        self._check(other)
        return FootprintVector(self.structure, self.data + other.data)

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __mul__(self, k):
        if not np.isscalar(k):
            raise TypeError("FootprintVector can only be multiplied by a scalar")
        out = self.data * k
        if k < 0:                       # negative scaling swaps the bounds
            out = out[:, ::-1]
        return FootprintVector(self.structure, out)

    __rmul__ = __mul__


    def __repr__(self):
        def fmt(row):
            lo, mid, hi = row
            return f"{mid:g}" if lo == mid == hi else f"[{lo:g}, {mid:g}, {hi:g}]"
        items = ", ".join(f"{l}={fmt(r)}" for l, r in zip(self.structure.labels, self.data))
        return f"FootprintVector({items})"