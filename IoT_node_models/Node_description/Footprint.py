import numpy as np


class FootprintStructure:
    """Shared, ordered, immutable set of impact categories."""

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
        """Build an FootprintVector. Missing labels default to 0.

        Accepts a dict and/or keyword arguments:
            structure.vector(GWP=1.2)
            structure.vector({"GWP": 1.2, "Water use": 0.02})  # labels that aren't valid identifiers
        """
        values = {**(values or {}), **kwargs}
        unknown = set(values) - set(self._labels)
        if unknown:
            raise KeyError(f"Unknown impact labels: {sorted(unknown)}")
        data = np.zeros(len(self._labels))
        for label, v in values.items():
            data[self._idx[label]] = v
        return FootprintVector(self, data)

    def zeros(self):
        return FootprintVector(self, np.zeros(len(self._labels)))


class FootprintVector:
    __slots__ = ("structure", "data")

    def __init__(self, structure, data):
        data = np.asarray(data, dtype=float)
        if data.shape[0] != len(structure):
            raise ValueError("data length does not match structure")
        self.structure = structure
        self.data = data  # shape (n_labels,) or (n_labels, n_samples)

    def _check(self, other):
        if not isinstance(other, FootprintVector) or other.structure is not self.structure:
            raise ValueError("Footprint vectors use different structures")

    def __add__(self, other):
        self._check(other)
        return FootprintVector(self.structure, self.data + other.data)

    def __radd__(self, other):  # lets built-in sum() start from 0
        if other == 0:
            return self
        return self.__add__(other)

    def __mul__(self, k):
        return FootprintVector(self.structure, self.data * k)

    __rmul__ = __mul__

    def __getitem__(self, label):
        return self.data[self.structure._idx[label]]

    def as_dict(self):
        return dict(zip(self.structure.labels, self.data.tolist()))

    def __repr__(self):
        items = ", ".join(f"{l}={v:g}" for l, v in zip(self.structure.labels, self.data))
        return f"FootprintVector({items})"

