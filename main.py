"""Forecast GTA VI launch-day Twitch viewers, hours 2-24, as five quantiles.

Model: for each forecast hour h, fit log(viewers_h) = a_h + b_h * log(viewers_1)
by least squares over the launch-day curves of the comparables shipped in the
case file, then place the five quantiles around the fitted value from the fit
residuals (the average of the empirical residual quantiles and the matching
normal quantiles). The hour-1 print anchors the level; the fitted slope b_h
falls toward zero for late hours, which is what past launches show: the day's
peak is set by the global daytime audience, not by the size of hour 1.

Stdlib only, deterministic, no network.
"""

import json
import math
import os
from datetime import datetime

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
Z = (-1.6448536269514722, -0.6744897501960817, 0.0, 0.6744897501960817, 1.6448536269514722)
BASE_SIGMA = 0.15
MIN_CURVE_HOURS = 20
MIN_FIT_CURVES = 5


def parse_ts(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def quantile(sorted_vals, q):
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def round2(x):
    v = math.floor(x * 100 + 0.5) / 100
    return int(v) if float(v).is_integer() else v


def is_target_history(comp):
    text = " ".join(str(comp.get(k) or "") for k in ("name", "unlock")).lower()
    return "target-history" in text or "not a launch" in text or "before release" in text


def comparable_curves(case):
    curves = []
    comps = sorted(case.get("comparables") or [], key=lambda c: str(c.get("name") or ""))
    for comp in comps:
        if is_target_history(comp):
            continue
        try:
            day_start = parse_ts(comp["day_start"])
        except (KeyError, TypeError, ValueError):
            continue
        hours = {}
        for pt in comp.get("hourly") or []:
            try:
                t = parse_ts(pt["from"])
                viewers = pt["viewers"]
            except (KeyError, TypeError, ValueError):
                continue
            h = int((t - day_start).total_seconds() // 3600) + 1
            if 1 <= h <= 24 and h not in hours and viewers is not None:
                hours[h] = max(1.0, float(viewers))
        if 1 in hours and len(hours) >= MIN_CURVE_HOURS:
            curves.append(hours)
    return curves


def fit_hour(curves, h):
    """Least-squares fit of log viewers_h on log viewers_1.

    Returns (intercept, slope, sorted residuals).
    """
    xs = []
    ys = []
    for hours in curves:
        if h in hours:
            xs.append(math.log(hours[1]))
            ys.append(math.log(hours[h]))
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx > 0 else 0.0
    a = my - b * mx
    residuals = sorted(y - (a + b * x) for x, y in zip(xs, ys))
    return a, b, residuals


def hour_quantiles(p1, curves, h):
    fit = [c for c in curves if h in c]
    if len(fit) < MIN_FIT_CURVES:
        out = []
        prev = 0.0
        for z in Z:
            q = round2(min(max(p1 * math.exp(z * BASE_SIGMA * math.sqrt(h - 1)), 1.0), 1_000_000_000.0))
            q = max(q, prev)
            out.append(q)
            prev = q
        return out
    a, b, residuals = fit_hour(fit, h)
    n = len(residuals)
    mu = sum(residuals) / n
    var = sum((r - mu) ** 2 for r in residuals) / max(1, n - 2)
    sigma = math.sqrt(var) if var > 0 else BASE_SIGMA * math.sqrt(h - 1)
    pred = a + b * math.log(p1)
    out = []
    prev = 0.0
    for tau, z in zip(LEVELS, Z):
        emp = quantile(residuals, tau)
        norm = mu + z * sigma
        q = round2(min(max(math.exp(pred + 0.5 * emp + 0.5 * norm), 1.0), 1_000_000_000.0))
        q = max(q, prev)
        out.append(q)
        prev = q
    return out


def hour1_print(case):
    for row in case.get("known") or []:
        if row.get("hour") == 1 and row.get("viewers") is not None:
            return max(1.0, float(row["viewers"]))
    hist = case.get("history_hourly") or []
    if hist:
        v = hist[-1].get("viewers")
        if v is not None:
            return max(1.0, float(v))
    return 1.0


def forecast_case(case):
    p1 = hour1_print(case)
    curves = comparable_curves(case)
    hours = []
    seen = set()
    for row in case.get("forecast") or []:
        h = int(row["hour"])
        if h < 2 or h > 24 or h in seen:
            continue
        seen.add(h)
        hours.append({"hour": h, "q": hour_quantiles(p1, curves, h)})
    hours.sort(key=lambda r: r["hour"])
    return {"hours": hours}


def main():
    input_dir = os.environ.get("MAKEFUN_INPUT_DIR") or "/input/"
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output/"
    os.makedirs(output_dir, exist_ok=True)
    names = sorted(n for n in os.listdir(input_dir) if n.endswith(".in"))
    for name in names:
        with open(os.path.join(input_dir, name), encoding="utf-8") as f:
            case = json.load(f)
        forecast = forecast_case(case)
        out_name = name[:-3] + ".out"
        with open(os.path.join(output_dir, out_name), "w", encoding="utf-8") as f:
            f.write(json.dumps(forecast, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
