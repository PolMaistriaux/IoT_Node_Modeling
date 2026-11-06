#%%
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from ..MyColors import *
from ..Node_description.Hardware.Footprint import FootprintVector, LOW, MID, HIGH


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _annual_fp(node, label):
    """(low, mid, high) of the annual footprint for an already-computed node."""
    ds  = node.deployment_strategy
    tot = ds.placement + ds.replacement * ds.n_replacements + ds.decom
    lo, mid, hi = tot[label]
    return lo / ds.Nyears, mid / ds.Nyears, hi / ds.Nyears


def _apply_param(node, task, paramType, value, param_setter, transport_refs):
    """Set a secondary-sweep parameter on the node."""
    if param_setter is not None:
        param_setter(node, value)
    elif paramType == "dnode" and task is not None:
        task.set_distance(value)
    elif paramType == "rsd":
        node.hardware.get_Battery().set_selfdischarge_p_year(value)
    elif paramType == "dtrans" and transport_refs:
        for t in transport_refs:
            t.km_fixed = value


def _restore_param(node, task, paramType, init_val, transport_refs):
    """Restore the secondary parameter to its initial value."""
    if paramType == "dnode" and task is not None:
        task.set_distance(init_val)
    elif paramType == "rsd":
        node.hardware.get_Battery().set_selfdischarge_p_year(init_val)
    elif paramType == "dtrans" and transport_refs:
        for t, km in zip(transport_refs, init_val):
            t.km_fixed = km


def _save_param_state(node, task, paramType, transport_refs):
    """Return the current value of the secondary parameter (for later restore)."""
    if paramType == "dnode" and task is not None:
        return task.get_distance()
    elif paramType == "rsd":
        return node.hardware.get_Battery().get_selfdischarge_p_year()
    elif paramType == "dtrans" and transport_refs:
        return [t.km_fixed for t in transport_refs]
    return None


_COLOR_LISTS = [listBlue, listTurquoise, listGreen, listOrange]


# ---------------------------------------------------------------------------
# sweep_fdata  –  sweep task transmission rate
# ---------------------------------------------------------------------------

def sweep_fdata(node, task, label="GWP",
                fmin=1, fmax=100, f_step=1,
                nAA=None, param_values=None, paramType=None,
                param_setter=None, transport_refs=None,
                replacementCategories=False,
                figsize=(7, 6), filename=None, figAppend=None, xlim= None, ylim =None):
    """Plot annual `label` footprint as a function of `task` rate.

    Mirrors the behaviour of ``lora_deployment_sweep_fdata`` / ``deployment_sweep_fdata``
    from the legacy framework, adapted to the new ``Node_description`` API.

    Parameters
    ----------
    node : Node_description
        A fully configured node.  ``node.compute()`` must have been called at
        least once so that the deployment strategy is initialised.
    task : Task
        The task whose daily rate is swept (msg/day).
    label : str
        Impact label to plot (must exist in ``node.hardware.footprintStructure``).
    fmin, fmax, f_step : int
        Sweep range.
    nAA : list of float, optional
        Battery-capacity multipliers (e.g. ``[1, 3]``).  Battery capacity *and*
        its footprint factors are scaled proportionally.  ``None`` → ``[1]``.
    param_values : list, optional
        Values for the secondary parameter sweep.
    paramType : str, optional
        ``"dnode"``  → ``task.set_distance(value)``
        ``"rsd"``    → battery self-discharge rate
        ``"dtrans"`` → ``km_fixed`` of every ``Transport`` in ``transport_refs``
    param_setter : callable (node, value), optional
        Custom setter; overrides ``paramType``.
    transport_refs : list of Transport, optional
        ``Transport`` objects updated when ``paramType == "dtrans"``.
    replacementCategories : tuple | None | False
        Temporarily overrides ``deployment_strategy.ReplacementStrategy``.
        ``False`` (default) keeps the existing setting.
    figsize, filename, figAppend : figure controls.

    Returns
    -------
    fig, ax
    """
    # --- save state ----------------------------------------------------------
    batt      = node.hardware.Battery
    f0        = node.profile.get_task_rate(task)
    capa0     = batt.get_capacity_mAh()
    rsd0      = batt.get_selfdischarge_p_year()
    factors0  = batt.factors
    rep0      = node.deployment_strategy.ReplacementStrategy
    param0    = _save_param_state(node, task, paramType, transport_refs)

    if replacementCategories is not False:
        node.deployment_strategy.ReplacementStrategy = replacementCategories
    if nAA is None:
        nAA = [1]
    if not param_values:
        param_values = [None]

    fdata   = np.arange(fmin, fmax, f_step)
    results = np.zeros((len(nAA), len(param_values), len(fdata), 3))  # low/mid/high

    # --- sweep ---------------------------------------------------------------
    for ip, pv in enumerate(param_values):
        if pv is not None:
            _apply_param(node, task, paramType, pv, param_setter, transport_refs)

        for iAA, AA in enumerate(nAA):
            batt.set_capacity_mAh(capa0 * AA)
            if factors0 is not None:
                batt.factors = factors0 * AA

            for iff, f in enumerate(fdata):
                node.profile.change_task_rate(task, f)
                node.compute()
                results[iAA, ip, iff] = _annual_fp(node, label)

    # --- restore state -------------------------------------------------------
    node.profile.change_task_rate(task, f0)
    batt.set_capacity_mAh(capa0)
    batt.set_selfdischarge_p_year(rsd0)
    batt.factors = factors0
    if replacementCategories is not False:
        node.deployment_strategy.ReplacementStrategy = rep0
    if param0 is not None:
        _restore_param(node, task, paramType, param0, transport_refs)

    # --- plot ----------------------------------------------------------------
    unit   = node.hardware.footprintStructure.units[list(node.hardware.footprintStructure.labels).index(label)]
    ylabel = f"Annual {label} [{unit}/yr]" if unit else f"Annual {label} [/yr]"

    if figAppend is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig, ax = figAppend

    ax.set_xlabel("Transmission rate [msg/day]")
    ax.set_ylabel(ylabel)

    for iAA, AA in enumerate(nAA):
        col_list = _COLOR_LISTS[iAA % len(_COLOR_LISTS)]
        for ip, pv in enumerate(param_values):
            color = col_list[-(ip + 1)]
            mid   = results[iAA, ip, :, MID]
            lbl   = (f"×{AA} batt" if len(nAA) > 1 else "") + \
                    (f", {pv}" if pv is not None and len(param_values) > 1 else "")
            ax.plot(fdata, mid, color=color, label=lbl.strip(", "))

    if figAppend is None:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
        ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
        ax.set_ylim(ylim)
        ax.set_xlim(xlim)
        for ref in [1, 24, 24 * 12]:
            if fmin <= ref <= fmax:
                ax.axvline(ref, linestyle="dashed", color="black", linewidth=0.8)
        nyears = node.deployment_strategy.Nyears
        ax.set_title(f"Annual {label} vs TX rate  ({nyears} yr)")
        ax.tick_params(axis='x', labelsize=12)
        if len(nAA) > 1 or (param_values and param_values[0] is not None and len(param_values) > 1):
            ax.legend(fontsize=11)

    if filename is not None:
        fig.savefig(filename + ".svg", format="svg")

    return fig, ax


# ---------------------------------------------------------------------------
# sweep_ebatt  –  sweep battery capacity
# ---------------------------------------------------------------------------

def sweep_ebatt(node, label="GWP",
                nAAmin=1, nAAmax=6, nAA_step=1,
                param_values=None, paramType=None,
                param_setter=None, transport_refs=None,
                replacementCategories=False,
                figsize=(7, 6), filename=None, figAppend=None,xlim= None, ylim =None):
    """Plot annual `label` footprint as a function of battery capacity.

    Mirrors ``deployment_sweep_ebatt`` from the legacy framework.

    Parameters
    ----------
    node : Node_description
        A fully configured node with deployment strategy computed.
    label : str
        Impact label to plot.
    nAAmin, nAAmax, nAA_step : float
        Battery-capacity sweep expressed as multiples of the node's initial
        capacity (e.g. 1–7 × 2800 mAh).
    param_values : list, optional
        Secondary sweep values.
    paramType : str, optional
        ``"rsd"`` → battery self-discharge, ``"dtrans"`` → transport distance.
    param_setter : callable (node, value), optional
        Custom setter; overrides ``paramType``.
    transport_refs : list of Transport, optional
        Updated when ``paramType == "dtrans"``.
    replacementCategories : tuple | None | False
        Temporarily overrides ``deployment_strategy.ReplacementStrategy``.
    figsize, filename, figAppend : figure controls.

    Returns
    -------
    fig, ax
    """
    # --- save state ----------------------------------------------------------
    batt      = node.hardware.Battery
    capa0     = batt.get_capacity_mAh()
    rsd0      = batt.get_selfdischarge_p_year()
    factors0  = batt.factors
    rep0      = node.deployment_strategy.ReplacementStrategy
    param0    = _save_param_state(node, None, paramType, transport_refs)

    if replacementCategories is not False:
        node.deployment_strategy.ReplacementStrategy = replacementCategories
    if not param_values:
        param_values = [None]

    nAA_arr = np.arange(nAAmin, nAAmax + nAA_step * 0.5, nAA_step)
    results = np.zeros((len(param_values), len(nAA_arr), 3))  # low/mid/high

    # --- sweep ---------------------------------------------------------------
    for ip, pv in enumerate(param_values):
        if pv is not None:
            _apply_param(node, None, paramType, pv, param_setter, transport_refs)

        for iAA, AA in enumerate(nAA_arr):
            batt.set_capacity_mAh(capa0 * AA)
            if factors0 is not None:
                batt.factors = factors0 * AA
            node.compute()
            results[ip, iAA] = _annual_fp(node, label)

    # --- restore state -------------------------------------------------------
    batt.set_capacity_mAh(capa0)
    batt.set_selfdischarge_p_year(rsd0)
    batt.factors = factors0
    if replacementCategories is not False:
        node.deployment_strategy.ReplacementStrategy = rep0
    if param0 is not None:
        _restore_param(node, None, paramType, param0, transport_refs)

    # --- plot ----------------------------------------------------------------
    unit   = node.hardware.footprintStructure.units[list(node.hardware.footprintStructure.labels).index(label)]
    ylabel = f"Annual {label} [{unit}/yr]" if unit else f"Annual {label} [/yr]"

    if figAppend is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig, ax = figAppend

    x_capa = capa0 * nAA_arr
    ax.set_xlabel("Battery capacity [mAh]")
    ax.set_ylabel(ylabel)

    col_list = _COLOR_LISTS[0]
    for ip, pv in enumerate(param_values):
        color = col_list[-(ip + 1)]
        mid   = results[ip, :, MID]
        lbl   = str(pv) if pv is not None and len(param_values) > 1 else ""
        ax.plot(x_capa, mid, color=color, label=lbl)
        iopt = int(np.argmin(mid))
        ax.scatter(x_capa[iopt], mid[iopt], color=color, marker="s", zorder=5)

    if figAppend is None:
        yvals = results[:, :, MID]
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
        ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xticks(capa0 * np.arange(np.ceil(nAAmin), np.floor(nAAmax) + 1))
        nyears = node.deployment_strategy.Nyears
        ax.set_title(f"Annual {label} vs battery size  ({nyears} yr)")
        ax.tick_params(axis='x', labelsize=12)
        if param_values and param_values[0] is not None and len(param_values) > 1:
            ax.legend(fontsize=11)

    if filename is not None:
        fig.savefig(filename + ".svg", format="svg")

    return fig, ax


# ---------------------------------------------------------------------------
# sweep_dnode  –  sweep node-to-gateway distance
# ---------------------------------------------------------------------------

def sweep_dnode(node, task, label="GWP",
                dmin=5, dmax=100, d_step=1,
                param_values=None, paramType=None,
                param_setter=None, transport_refs=None,
                replacementCategories=False,
                figsize=(7, 6), filename=None,xlim= None, ylim =None):
    """Plot annual `label` footprint as a function of node-to-gateway distance.

    Mirrors ``lora_deployment_sweep_dnode`` from the legacy framework.

    Parameters
    ----------
    node : Node_description
        A fully configured node with deployment strategy computed.
    task : Task  (Transceiver_task)
        The TX task whose distance is swept.
    label : str
        Impact label to plot.
    dmin, dmax, d_step : float
        Distance sweep range [km].
    param_values : list, optional
        Secondary sweep values.
    paramType : str, optional
        ``"fdata"`` → task rate, ``"rsd"`` → battery self-discharge,
        ``"ebatt"`` → battery capacity multiplier.
    param_setter : callable (node, value), optional
        Custom setter; overrides ``paramType``.
    transport_refs : list of Transport, optional
        Updated when ``paramType == "dtrans"``.
    replacementCategories : tuple | None | False
        Temporarily overrides ``deployment_strategy.ReplacementStrategy``.
    figsize, filename : figure controls.

    Returns
    -------
    fig, ax
    """
    # --- save state ----------------------------------------------------------
    batt     = node.hardware.Battery
    d0       = task.get_distance()
    capa0    = batt.get_capacity_mAh()
    rsd0     = batt.get_selfdischarge_p_year()
    factors0 = batt.factors
    rep0     = node.deployment_strategy.ReplacementStrategy
    param0   = _save_param_state(node, task, paramType, transport_refs)

    # for fdata paramType we need the initial rate separately
    if paramType == "fdata":
        param0 = node.profile.get_task_rate(task)

    if replacementCategories is not False:
        node.deployment_strategy.ReplacementStrategy = replacementCategories
    if not param_values:
        param_values = [None]

    ddata   = np.arange(dmin, dmax, d_step)
    results = np.zeros((len(param_values), len(ddata), 3))

    # --- sweep ---------------------------------------------------------------
    for ip, pv in enumerate(param_values):
        if pv is not None:
            if paramType == "fdata":
                node.profile.change_task_rate(task, pv)
            elif paramType == "ebatt":
                batt.set_capacity_mAh(capa0 * pv)
                if factors0 is not None:
                    batt.factors = factors0 * pv
            else:
                _apply_param(node, task, paramType, pv, param_setter, transport_refs)

        for idd, d in enumerate(ddata):
            task.set_distance(d)
            node.compute()
            results[ip, idd] = _annual_fp(node, label)

    # --- restore state -------------------------------------------------------
    task.set_distance(d0)
    batt.set_capacity_mAh(capa0)
    batt.set_selfdischarge_p_year(rsd0)
    batt.factors = factors0
    if replacementCategories is not False:
        node.deployment_strategy.ReplacementStrategy = rep0
    if param0 is not None:
        if paramType == "fdata":
            node.profile.change_task_rate(task, param0)
        elif paramType == "ebatt":
            pass  # already restored above via capa0 / factors0
        else:
            _restore_param(node, task, paramType, param0, transport_refs)

    # --- plot ----------------------------------------------------------------
    unit   = node.hardware.footprintStructure.units[list(node.hardware.footprintStructure.labels).index(label)]
    ylabel = f"Annual {label} [{unit}/yr]" if unit else f"Annual {label} [/yr]"

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.set_xlabel("Node–gateway distance [km]")
    ax.set_ylabel(ylabel)

    col_list = _COLOR_LISTS[0]
    for ip, pv in enumerate(param_values):
        color = col_list[-(ip + 1)]
        mid   = results[ip, :, MID]
        lbl   = str(pv) if pv is not None and len(param_values) > 1 else ""
        ax.plot(ddata, mid, color=color, label=lbl)

    yvals = results[:, :, MID]
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(mpl.ticker.NullFormatter())
    ax.set_ylim(ylim)
    nyears = node.deployment_strategy.Nyears
    ax.set_title(f"Annual {label} vs distance  ({nyears} yr)")
    ax.tick_params(axis='x', labelsize=12)
    if param_values and param_values[0] is not None and len(param_values) > 1:
        ax.legend(fontsize=11)

    if filename is not None:
        fig.savefig(filename + ".svg", format="svg")

    return fig, ax
