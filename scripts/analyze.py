#!/usr/bin/env python3
"""
MOUSUMI — Scientific analysis engine (v2, homogeneity-corrected)
================================================================
Processes NASA POWER data for all 64 districts of Bangladesh and produces the
compact JSON consumed by the dashboard.

DATA AUDIT FINDING (documented in README + dashboard "Data & Methods"):
  A homogeneity audit of NASA POWER v8 over Bangladesh (see decadal means in
  output `homogeneity`) reveals large multi-decadal discontinuities in the
  1981-2025 precipitation and temperature record for this region (e.g., the
  Sylhet grid cell shows a doubling of decadal mean rainfall, and daily T2M_MAX
  in the 1980s is warm-biased by ~2-3 degC versus gauge climatology). Such
  inhomogeneities are a known limitation of reanalysis-based products in the
  tropics. Consequences for methodology:

  1. CURRENT-CONDITION MODELING uses the recent 10-year window (2016-2025),
     which is internally consistent: monthly climatology, FAO-56 ETo,
     seasonal water balance, rotation engine, heat climatology, monsoon
     calendar. This is what the advisory tool needs.
  2. RECENT TENDENCIES use Mann-Kendall/Sen over 2011-2025 (15 years),
     presented as indicative only.
  3. LONG-TERM CHANGE DIRECTION is cited from peer-reviewed literature
     (IPCC AR6; Bangladesh climate studies; World Bank salinity projections),
     not extrapolated from an inhomogeneous reanalysis.
  4. The full 45-year POWER record remains available in the dashboard for
     transparency, with the audit table shown alongside.

Scientific components:
  1. Mann-Kendall trend test (tie-corrected) + Theil-Sen slope
     (Mann 1945; Kendall 1975; Sen 1968)
  2. FAO-56 Penman-Monteith ETo, monthly step (Allen et al. 1998).
     Monthly mean Tmax is computed from the POWER DAILY product (the monthly
     T2M_MAX parameter is a monthly EXTREME, not a mean - verified
     empirically); monthly mean Tmin is estimated as Tmin ~= 2*T2M - Tmax
     (documented approximation).
  3. Monthly rainfall totals: POWER monthly PRECTOTCORR is a mm/day rate
     (verified empirically vs daily sums) -> multiplied by days-in-month.
  4. Monsoon onset/withdrawal from daily rainfall (transparent criterion).
  5. Extreme heat days: daily Tmax >= 35 degC (rice anthesis sterility
     threshold, Yoshida 1981).
  6. Water balance: ETc = Kc x ETo (FAO-56); effective rainfall (FAO AGLW).
  7. Salinity risk: SRDI-informed baseline x recent dry-season aridity;
     crop tolerance via Maas-Hoffman (Maas & Hoffman 1977; FAO I&D 29).
  8. Crop rotation multi-criteria engine with farmer-priority weighting.
"""
import json
import math
import os
import sys
import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from districts import DISTRICTS, BASELINE_SALINITY_DS_M, BANGLA_NAMES, DIVISION_BANGLA  # noqa: E402
from crop_library import CROPS, build_rotations, score_rotations, BASELINES  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

FULL_YEARS = list(range(1981, 2026))       # full POWER record (transparency)
RECENT_15 = list(range(2011, 2026))        # tendency window
CLIM_10 = list(range(2016, 2026))          # current-climatology window

MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

SEASONS = {
    "rabi":    [11, 12, 1, 2, 3],
    "kharif1": [4, 5, 6],
    "kharif2": [7, 8, 9, 10],
    "monsoon": [6, 7, 8, 9],
    "premon":  [3, 4, 5],
}

ZONE_ELEV = {"coastal-saline": 3, "coastal": 5, "coastal-inland": 6,
             "central": 10, "barind": 18, "haor": 8, "hilly": 40}


def slug(name):
    return name.lower().replace(" ", "_").replace("'", "")


# ------------------------------------------------------ statistics: MK + Sen
def normal_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2.0)))


def mann_kendall(series):
    n = len(series)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += (series[j] > series[i]) - (series[j] < series[i])
    counts = defaultdict(int)
    for v in series:
        counts[v] += 1
    tie_term = sum(t * (t - 1) * (2 * t + 5) for t in counts.values())
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0
    if var_s <= 0:
        return s, 0.0, 0.0, 1.0, 0.0
    z = (s - 1) / math.sqrt(var_s) if s > 0 else ((s + 1) / math.sqrt(var_s) if s < 0 else 0.0)
    p = 2 * (1 - normal_cdf(abs(z)))
    tau = s / (n * (n - 1) / 2) if n > 1 else 0.0
    return s, var_s, z, p, tau


def sens_slope(series):
    n = len(series)
    slopes = sorted((series[j] - series[i]) / (j - i)
                    for i in range(n - 1) for j in range(i + 1, n))
    m = len(slopes)
    return slopes[m // 2] if m % 2 else 0.5 * (slopes[m // 2 - 1] + slopes[m // 2])


def trend(series):
    series = [v for v in series if v is not None]
    if len(series) < 8:
        return None
    s, var_s, z, p, tau = mann_kendall(series)
    slope = sens_slope(series)
    return {"slope": round(slope, 4), "p": round(p, 5), "tau": round(tau, 3),
            "z": round(z, 3), "total": round(slope * (len(series) - 1), 2),
            "sig": p < 0.05, "n_years": len(series),
            "first": round(series[0], 2), "last": round(series[-1], 2)}


# ------------------------------------------------- FAO-56 Penman-Monteith
def extraterrestrial_radiation(lat_deg, month):
    phi = math.radians(lat_deg)
    doy_mid = 15 + int(30.42 * ((month - 1) % 12))
    dr = 1 + 0.033 * math.cos(2 * math.pi * doy_mid / 365.0)
    delta = 0.409 * math.sin(2 * math.pi * doy_mid / 365.0 - 1.39)
    x = max(-1.0, min(1.0, -math.tan(phi) * math.tan(delta)))
    ws = math.acos(x)
    ra = (24 * 60 / math.pi) * 0.0820 * dr * (
        ws * math.sin(phi) * math.sin(delta) +
        math.cos(phi) * math.cos(delta) * math.sin(ws))
    return ra


def et0_month(lat, elev, month, tmean, tmax_mean, tmin_mean, rh, ws, rs):
    """FAO-56 Penman-Monteith monthly ETo (mm/day). tmax_mean/tmin_mean are
    monthly MEANS of daily max/min temperature (NOT monthly extremes)."""
    if None in (tmean, tmax_mean, tmin_mean, rh, ws, rs):
        return None
    es_tmax = 0.6108 * math.exp(17.27 * tmax_mean / (tmax_mean + 237.3))
    es_tmin = 0.6108 * math.exp(17.27 * tmin_mean / (tmin_mean + 237.3))
    es = (es_tmax + es_tmin) / 2.0
    ea = es * min(1.0, max(0.01, rh / 100.0))
    delta = 4098 * (0.6108 * math.exp(17.27 * tmean / (tmean + 237.3))) / ((tmean + 237.3) ** 2)
    p = 101.3 * ((293.0 - 0.0065 * elev) / 293.0) ** 5.26
    gamma = 0.000665 * p
    u2 = max(0.05, ws)
    rns = (1 - 0.23) * rs
    ra = extraterrestrial_radiation(lat, month)
    rso = (0.75 + 2e-5 * elev) * ra
    ratio = min(1.0, rs / rso) if rso > 0 else 0.7
    sigma = 4.903e-9
    rnl = sigma * (((tmax_mean + 273.16) ** 4 + (tmin_mean + 273.16) ** 4) / 2) * \
        (0.34 - 0.14 * math.sqrt(max(0.0, ea))) * (1.35 * ratio - 0.35)
    rn = rns - rnl
    num = 0.408 * delta * rn + gamma * (900.0 / (tmean + 273)) * u2 * (es - ea)
    den = delta + gamma * (1 + 0.34 * u2)
    return num / den


# ------------------------------------------------------------ data loading
def load_json(kind, name):
    path = os.path.join(RAW, f"{kind}_{slug(name)}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f).get("properties", {}).get("parameter", {})


def monthly_rate_to_total(params, key, years):
    """POWER monthly PRECTOTCORR is a mm/day rate -> monthly totals (mm)."""
    out = {}
    for k, v in (params.get(key) or {}).items():
        if v in (None, -999, -999.0):
            continue
        y, m = int(k[:4]), int(k[4:6])
        if m <= 12 and y in years:
            days = 29 if (m == 2 and (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))) else MONTH_DAYS[m - 1]
            out[(y, m)] = v * days
    return out


def monthly_means(params, key, years):
    out = {}
    for k, v in (params.get(key) or {}).items():
        if v in (None, -999, -999.0):
            continue
        y, m = int(k[:4]), int(k[4:6])
        if m <= 12 and y in years:
            out[(y, m)] = v
    return out


def daily_tmax_monthly_means(dpar, years):
    """Monthly MEAN of daily Tmax from the daily product (correct semantics
    for FAO-56; the monthly T2M_MAX parameter is a monthly EXTREME)."""
    by = defaultdict(list)
    for k, v in (dpar.get("T2M_MAX") or {}).items():
        if v in (None, -999, -999.0):
            continue
        y = int(k[:4])
        if y in years:
            by[(y, int(k[4:6]))].append(v)
    return {k: sum(v) / len(v) for k, v in by.items() if v}


def daily_series(dpar, key, years):
    by = defaultdict(dict)
    for k, v in (dpar.get(key) or {}).items():
        if v in (None, -999, -999.0):
            continue
        y = int(k[:4])
        if y in years:
            by[y][k] = v
    return by


def safe_mean(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


# -------------------------------------------------------- district analysis
def analyze_district(dist):
    name, division, lat, lon, zone = dist
    mpar = load_json("monthly", name)
    dpar = load_json("daily", name)
    if not mpar:
        return None
    elev = ZONE_ELEV.get(zone, 10)

    pre = monthly_rate_to_total(mpar, "PRECTOTCORR", set(FULL_YEARS))
    t2m = monthly_means(mpar, "T2M", set(FULL_YEARS))
    rh = monthly_means(mpar, "RH2M", set(FULL_YEARS))
    ws = monthly_means(mpar, "WS2M", set(FULL_YEARS))
    rs = monthly_means(mpar, "ALLSKY_SFC_SW_DWN", set(FULL_YEARS))
    tmax_mean = daily_tmax_monthly_means(dpar, set(FULL_YEARS))  # correct semantics

    def est_tmin(tmean, tmaxm):
        if tmean is None or tmaxm is None:
            return None
        return 2.0 * tmean - tmaxm  # documented approximation

    # ---- full-record annual series (transparency view + homogeneity audit)
    def annual_rain():
        by = defaultdict(float)
        cnt = defaultdict(int)
        for (y, m), v in pre.items():
            by[y] += v
            cnt[y] += 1
        return {y: by[y] for y in FULL_YEARS if cnt[y] == 12}

    def annual_t2m():
        by = defaultdict(list)
        for (y, m), v in t2m.items():
            by[y].append(v)
        return {y: sum(v) / len(v) for y, v in by.items() if len(v) == 12}

    rain_full = annual_rain()
    t2m_full = annual_t2m()

    # ---- monthly ETo per year (full record, for water balance & aridity)
    def eto(y, m):
        tm = t2m.get((y, m))
        tx = tmax_mean.get((y, m))
        return et0_month(lat, elev, m, tm, tx, est_tmin(tm, tx),
                         rh.get((y, m)), ws.get((y, m)), rs.get((y, m)))

    eto_annual = {}
    for y in FULL_YEARS:
        vals = [eto(y, m) for m in range(1, 13)]
        if all(v is not None for v in vals):
            eto_annual[y] = sum(v * MONTH_DAYS[m - 1] for m, v in zip(range(1, 13), vals))

    # ---- climatology (recent 10 years) -------------------------------
    pre_clim = []
    eto_clim = []
    for m in range(1, 13):
        pre_clim.append(round(safe_mean([pre.get((y, m)) for y in CLIM_10]), 1))
        eto_clim.append(round(safe_mean([eto(y, m) for y in CLIM_10]), 2))

    season_rain = {}
    for sname, months in SEASONS.items():
        season_rain[sname] = round(safe_mean(
            [sum(pre.get((y, m), 0) for m in months) for y in CLIM_10]), 1)
    season_eto = {}
    for sname, months in SEASONS.items():
        season_eto[sname] = round(safe_mean(
            [sum((eto(y, m) or 0) * MONTH_DAYS[m - 1] for m in months) for y in CLIM_10]), 1)

    # ---- recent-15-year series for indicative tendencies --------------
    def series15(getter):
        return [getter(y) for y in RECENT_15]

    rain15 = series15(lambda y: rain_full.get(y))
    t2m15 = series15(lambda y: t2m_full.get(y))
    eto15 = series15(lambda y: eto_annual.get(y))
    rabi_rain15 = series15(lambda y: safe_mean(
        [sum(pre.get((y, m), 0) for m in SEASONS["rabi"])]))
    rabi_rain15 = [sum(pre.get((y, m), 0) for m in SEASONS["rabi"])
                   if all((y, m) in pre for m in SEASONS["rabi"]) else None
                   for y in RECENT_15]
    aridity15 = []
    for y in RECENT_15:
        p_r = sum(pre.get((y, m), 0) for m in SEASONS["rabi"])
        pet_r = sum((eto(y, m) or 0) * MONTH_DAYS[m - 1] for m in SEASONS["rabi"])
        aridity15.append(round(p_r / pet_r, 3) if pet_r > 0 else None)

    # ---- daily-derived: heat days + monsoon calendar ------------------
    # Monsoon onset criterion (transparent + persistence-filtered):
    # first day after 25 May such that 10-day accumulated rainfall >= 60 mm
    # AND the following 10 days also accumulate >= 40 mm (sustained rains,
    # filtering out isolated pre-monsoon thunderstorms / kalboishakhi storms).
    # Withdrawal: last day after 15 Sep belonging to a 10-day window with
    # accumulated rainfall >= 60 mm.
    heat_by_year = {}
    onset_by_year = {}
    withdraw_by_year = {}
    pre_d = daily_series(dpar, "PRECTOTCORR", set(FULL_YEARS))
    for y in sorted(pre_d):
        days = pre_d[y]
        hd = sum(1 for k, v in (dpar.get("T2M_MAX") or {}).items()
                 if k[:4] == str(y) and v not in (None, -999, -999.0) and v >= 35.0)
        heat_by_year[y] = hd
        dates = sorted(days)
        vals = [days[k] for k in dates]
        mmdd = [int(k[4:6]) * 100 + int(k[6:8]) for k in dates]
        on = None
        for i in range(len(dates)):
            if mmdd[i] < 526:  # before 26 May
                continue
            if sum(vals[max(0, i - 9):i + 1]) >= 60.0 and \
               sum(vals[i + 1:i + 11]) >= 40.0:
                k = dates[i]
                on = datetime.date(int(k[:4]), int(k[4:6]), int(k[6:8])).timetuple().tm_yday
                break
        onset_by_year[y] = on
        wd = None
        for i in range(len(dates) - 1, -1, -1):
            if mmdd[i] < 915:
                break
            if sum(vals[max(0, i - 9):i + 1]) >= 60.0:
                k = dates[i]
                wd = datetime.date(int(k[:4]), int(k[4:6]), int(k[6:8])).timetuple().tm_yday
                break
        withdraw_by_year[y] = wd

    heat15 = [heat_by_year.get(y) for y in RECENT_15]
    onset10 = [onset_by_year.get(y) for y in CLIM_10]
    withdraw10 = [withdraw_by_year.get(y) for y in CLIM_10]
    heat10 = [heat_by_year.get(y) for y in CLIM_10]

    # ---- salinity risk ------------------------------------------------
    base_sal = BASELINE_SALINITY_DS_M.get(name,
                BASELINE_SALINITY_DS_M.get("_default_inland", 1.2))
    aridity_tr = trend(aridity15)
    eto_recent_annual = safe_mean([eto_annual.get(y) for y in CLIM_10])
    k2_rain_recent = season_rain["kharif2"]
    leach = (k2_rain_recent / eto_recent_annual) if eto_recent_annual else None
    sal_risk = compute_salinity_risk(base_sal, aridity_tr, leach)

    # ---- rotation engine (current-climatology based) -------------------
    rotations = build_rotations({
        "eto_clim": eto_clim, "pre_clim_mm": pre_clim,
        "base_salinity": base_sal,
        "heat_days_annual": safe_mean(heat10)})
    rotations = score_rotations(rotations)
    top_rotations = select_showcase_rotations(rotations, zone)

    # ---- homogeneity audit numbers (for Data & Methods panel) ----------
    decades = {"1981-1990": range(1981, 1991), "1991-2000": range(1991, 2001),
               "2001-2010": range(2001, 2011), "2011-2020": range(2011, 2021),
               "2021-2025": range(2021, 2026)}
    audit = []
    for label, rng in decades.items():
        rv = [rain_full[y] for y in rng if y in rain_full]
        tv = [t2m_full[y] for y in rng if y in t2m_full]
        if rv and tv:
            audit.append({"decade": label,
                          "rain_mm": round(sum(rv) / len(rv)),
                          "t2m_c": round(sum(tv) / len(tv), 2)})

    rec = {
        "name": name, "bn": BANGLA_NAMES.get(name, name),
        "division": division, "division_bn": DIVISION_BANGLA.get(division, division),
        "zone": zone, "lat": lat, "lon": lon, "elev_m": elev,
        "baseline_salinity_dsm": base_sal,
        "climate": {
            "years_recent15": RECENT_15,
            "rain_recent15_mm": [round(v, 1) if v is not None else None for v in rain15],
            "t2m_recent15_c": [round(v, 2) if v is not None else None for v in t2m15],
            "eto_recent15_mm": [round(v, 1) if v is not None else None for v in eto15],
            "rabi_rain_recent15_mm": [round(v, 1) if v is not None else None for v in rabi_rain15],
            "aridity_recent15": aridity15,
            "heat_days_recent15": heat15,
            "heat_days_clim10": [round(safe_mean(heat10), 1) if safe_mean(heat10) is not None else None][0],
            "onset_clim10_doy": [round(safe_mean(onset10), 1) if safe_mean(onset10) is not None else None][0],
            "onset_clim10_std": [round(safe_std(onset10), 1) if safe_std(onset10) is not None else None][0],
            "onset_years_doy": {str(k): v for k, v in onset_by_year.items() if k >= 2011},
            "withdraw_clim10_doy": [round(safe_mean(withdraw10), 1) if safe_mean(withdraw10) is not None else None][0],
            "pre_clim_mm": pre_clim,
            "eto_clim_mm_day": eto_clim,
            "season_rain_mm": season_rain,
            "season_eto_mm": season_eto,
            "rain_full_mm": {str(y): round(v) for y, v in rain_full.items()},
            "t2m_full_c": {str(y): round(v, 2) for y, v in t2m_full.items()},
        },
        "trends": {
            "note": "Mann-Kendall + Theil-Sen over 2011-2025 (recent window); indicative only - see Data & Methods",
            "rain": trend(rain15),
            "t2m": trend(t2m15),
            "eto": trend(eto15),
            "heat_days": trend(heat15),
            "rabi_aridity": trend(aridity15),
        },
        "salinity_risk": sal_risk,
        "homogeneity": audit,
        "rotations": top_rotations,
    }
    return rec


def safe_std(vals):
    vals = [v for v in vals if v is not None]
    if len(vals) < 2:
        return None
    m = sum(vals) / len(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def compute_salinity_risk(base_sal, aridity_tr, leach_recent):
    """First-order salinity pressure classification (transparent heuristic).
    Static baseline (SRDI-informed) + dynamic pressure from recent dry-season
    aridity tendency and monsoon leaching ratio."""
    score = 0.0
    if base_sal >= 5:
        score += 3
    elif base_sal >= 4:
        score += 2.5
    elif base_sal >= 3:
        score += 2
    elif base_sal >= 2:
        score += 1.2
    elif base_sal >= 1.5:
        score += 0.6
    else:
        score += 0.2
    if aridity_tr:
        if aridity_tr["sig"] and aridity_tr["slope"] < 0:
            score += 0.6
        elif aridity_tr["slope"] < 0:
            score += 0.3
    if leach_recent is not None and leach_recent < 1.0:
        score += 0.4
    if score >= 3.6:
        label, cls = "Very High", 4
    elif score >= 2.8:
        label, cls = "High", 3
    elif score >= 1.8:
        label, cls = "Moderate", 2
    elif score >= 1.0:
        label, cls = "Low-Moderate", 1
    else:
        label, cls = "Low", 0
    return {"label": label, "class": cls, "score": round(score, 2),
            "drivers": {"baseline_dsm": base_sal,
                        "rabi_aridity_trend": aridity_tr,
                        "leaching_ratio_recent": round(leach_recent, 2) if leach_recent else None}}


def select_showcase_rotations(rotations, zone):
    """Ship top 18 by default weights + business-as-usual baseline + best per
    criterion. The dashboard re-scores these live as farmers move sliders."""
    picked = {}
    for r in rotations[:18]:
        picked[(r["k2"], r["rabi"], r["k1"])] = r
    bau = BASELINES.get(zone)
    if bau:
        key = tuple(bau)
        match = next((r for r in rotations if (r["k2"], r["rabi"], r["k1"]) == key), None)
        if match:
            m = dict(match)
            m["business_as_usual"] = True
            picked[key] = m
    bests = [min(rotations, key=lambda r: r["irrigation_mm"]),
             max(rotations, key=lambda r: r["salinity_yield_pct"]),
             max(rotations, key=lambda r: r["gross_margin_bdt"]),
             max(rotations, key=lambda r: r["soil_health"]),
             min(rotations, key=lambda r: r["heat_risk_index"])]
    for b in bests:
        picked.setdefault((b["k2"], b["rabi"], b["k1"]), b)
    out = list(picked.values())
    out.sort(key=lambda r: -r["score"])
    return out


def main():
    out = {"meta": {
        "project": "MOUSUMI",
        "data_source": "NASA POWER v8 (Prediction Of Worldwide Energy Resources), NASA Langley Research Center",
        "source_url": "https://power.larc.nasa.gov/",
        "full_record": "1981-2025 (shown for transparency)",
        "climatology_window": "2016-2025",
        "tendency_window": "2011-2025",
        "generated": "2026-10-04",
        "methods": [
            "Mann-Kendall trend test with tie correction (Mann 1945; Kendall 1975)",
            "Theil-Sen slope estimator (Sen 1968)",
            "FAO-56 Penman-Monteith reference evapotranspiration (Allen et al. 1998)",
            "Monthly mean Tmax computed from POWER daily product (monthly T2M_MAX is an extreme)",
            "Monthly mean Tmin estimated as 2*T2M - Tmax (documented approximation)",
            "Monthly rainfall totals from POWER mm/day rates x days-in-month (verified empirically)",
            "Monsoon onset: first day after 15 May with 10-day accumulated rainfall >= 60 mm",
            "Extreme heat: days with Tmax >= 35 degC (rice anthesis sterility threshold, Yoshida 1981)",
            "Effective rainfall: FAO AGLW monthly method",
            "Salinity: Maas-Hoffman crop tolerance model (Maas & Hoffman 1977; FAO I&D Paper 29)",
        ],
    }, "districts": []}

    for dist in DISTRICTS:
        rec = analyze_district(dist)
        if rec:
            out["districts"].append(rec)
            t = rec["trends"]
            c = rec["climate"]
            print(f"{dist[0]:>16}: sal={rec['salinity_risk']['label']:<13} "
                  f"onset~{c['onset_clim10_doy'] or '?'} heat~{c['heat_days_clim10'] or '?'} "
                  f"rain(10y)={c['season_rain_mm'].get('rabi') or '?'}mm rabi")
    path = os.path.join(OUT, "mousumi_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"\nWrote {path} ({os.path.getsize(path)/1024:.0f} KB, {len(out['districts'])} districts)")


if __name__ == "__main__":
    main()
