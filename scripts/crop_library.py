"""
MOUSUMI — Bangladesh crop library & rotation engine
===================================================
Crop parameters are compiled from canonical FAO sources and Bangladesh
agricultural research literature. Every salinity number carries a provenance
flag: "fao29" = FAO Irrigation & Drainage Paper 29 (Ayers & Westcot 1985)
canonical value; "brri" = Bangladesh Rice Research Institute variety
documentation; "indicative" = literature-based estimate for crops FAO-29 does
not tabulate — flagged as user-editable in the dashboard (this is deliberate
scientific transparency, and doubles as the tool's "local calibration" input).

Kc (crop coefficients) & stage lengths: FAO-56 Tables 11-12 (Allen et al. 1998),
adjusted to typical Bangladesh cycle lengths reported by BRRI/BARI variety
leaflets. Gross margins: indicative 2023-25 farm-gate level estimates
(BBS Agricultural Statistics scale), editable by users.
"""

# Growth windows are expressed in "month.half" units (e.g. 11.5 = mid-November).
# Bangladesh seasons: Kharif-2 (Jul-Oct), Rabi (Nov-Apr), Kharif-1 (Apr-Jun).

CROPS = {
    # ---- Kharif-2 (monsoon) crops ------------------------------------------------
    "t_aman": {
        "en": "T. Aman rice", "bn": "আউশ-আমন ধান (ট্রান্সপ্লান্টেড আমন)",
        "family": "cereal", "slot": "kharif2",
        "sow": 7.0, "harvest": 11.5, "days": 135,
        "kc_avg": 1.10,  # FAO-56 paddy
        "ect_dsm": 3.0, "slope_pct": 12.0, "sal_source": "fao29",
        "heat_sensitive_window": [9.5, 10.5], "heat_sens": 1.0,
        "irrigation": "rainfed",
        "gross_margin_bdt_ha": 55000, "gm_flag": "indicative",
        "soil": 0.0, "note_bn": "বর্ষাকালীন প্রধান ফসল; সেচ লাগে না",
        "note_en": "Main monsoon rice; rainfed",
    },
    "k2_fallow": {
        "en": "Fallow (Kharif-2)", "bn": "পতিত (খরিফ-২)",
        "family": "fallow", "slot": "kharif2",
        "sow": 7.0, "harvest": 11.5, "days": 0,
        "kc_avg": 0.0, "ect_dsm": 99, "slope_pct": 0, "sal_source": "n/a",
        "irrigation": "none", "gross_margin_bdt_ha": 0, "gm_flag": "n/a",
        "soil": -0.5, "heat_sens": 0.0,
        "note_en": "No crop grown (missed monsoon opportunity)",
    },
    # ---- Rabi (dry winter) crops --------------------------------------------------
    "boro_hyv": {
        "en": "Boro rice (HYV)", "bn": "বোরো ধান (উচ্চ ফলনশীল)",
        "family": "cereal", "slot": "rabi",
        "sow": 12.5, "harvest": 4.5, "days": 145,
        "kc_avg": 1.15,  # FAO-56 paddy (flooded)
        "ect_dsm": 3.0, "slope_pct": 12.0, "sal_source": "fao29",
        "heat_sensitive_window": [3.0, 4.5], "heat_sens": 1.5,
        "irrigation": "full",
        "gross_margin_bdt_ha": 75000, "gm_flag": "indicative",
        "soil": -0.2,
        "note_en": "Irrigated dry-season rice; highest water demand; standard HYVs (e.g. BRRI dhan28/29) are salinity-sensitive at flowering",
    },
    "boro_salt": {
        "en": "Boro rice (salt-tolerant)", "bn": "বোরো ধান (লবণ সহিষ্ণু)",
        "family": "cereal", "slot": "rabi",
        "sow": 12.5, "harvest": 4.5, "days": 145,
        "kc_avg": 1.15,
        "ect_dsm": 8.0, "slope_pct": 12.0, "sal_source": "brri",  # BRRI dhan67: 8-10 dS/m vegetative
        "heat_sensitive_window": [3.0, 4.5], "heat_sens": 1.5,
        "irrigation": "full",
        "gross_margin_bdt_ha": 68000, "gm_flag": "indicative",
        "soil": -0.2,
        "note_en": "Salt-tolerant Boro (BRRI dhan67: 8-10 dS/m vegetative stage, 4.5-5.0 t/ha); similar water use, survives coastal salinity",
    },
    "wheat": {
        "en": "Wheat", "bn": "গম",
        "family": "cereal", "slot": "rabi",
        "sow": 11.5, "harvest": 3.5, "days": 110,
        "kc_avg": 0.80,  # FAO-56 wheat season-average
        "ect_dsm": 6.0, "slope_pct": 7.1, "sal_source": "fao29",
        "heat_sensitive_window": [2.5, 3.5], "heat_sens": 1.8,  # grain fill heat
        "irrigation": "partial",
        "gross_margin_bdt_ha": 55000, "gm_flag": "indicative",
        "soil": -0.1,
        "note_en": "FAO-29: moderately salt tolerant (ECt 6.0 dS/m)",
    },
    "maize": {
        "en": "Maize (winter)", "bn": "ভুট্টা (রবি)",
        "family": "cereal", "slot": "rabi",
        "sow": 11.5, "harvest": 4.0, "days": 135,
        "kc_avg": 0.95,
        "ect_dsm": 1.7, "slope_pct": 12.0, "sal_source": "fao29",
        "heat_sensitive_window": [3.0, 4.0], "heat_sens": 1.6,
        "irrigation": "partial",
        "gross_margin_bdt_ha": 95000, "gm_flag": "indicative",
        "soil": -0.1,
        "note_en": "High profit but FAO-29 salinity-sensitive (ECt 1.7) and heat-sensitive at silking",
    },
    "potato": {
        "en": "Potato", "bn": "আলু",
        "family": "tuber", "slot": "rabi",
        "sow": 11.0, "harvest": 2.0, "days": 90,
        "kc_avg": 0.85,
        "ect_dsm": 1.7, "slope_pct": 12.0, "sal_source": "fao29",
        "heat_sensitive_window": [1.5, 2.0], "heat_sens": 1.0,
        "irrigation": "partial",
        "gross_margin_bdt_ha": 130000, "gm_flag": "indicative",
        "soil": -0.1,
        "note_en": "High value; salinity-sensitive (FAO-29 ECt 1.7); early harvest avoids heat",
    },
    "mustard": {
        "en": "Mustard", "bn": "সরিষা",
        "family": "oilseed", "slot": "rabi",
        "sow": 11.0, "harvest": 1.5, "days": 80,
        "kc_avg": 0.75,
        "ect_dsm": 5.0, "slope_pct": 14.0, "sal_source": "indicative",
        "heat_sensitive_window": [1.0, 1.5], "heat_sens": 0.8,
        "irrigation": "light",
        "gross_margin_bdt_ha": 65000, "gm_flag": "indicative",
        "soil": 0.0,
        "note_en": "Short-cycle oilseed; widely grown in coastal Bangladesh; moderate salinity tolerance (indicative value - edit locally)",
    },
    "lentil": {
        "en": "Lentil", "bn": "মসুর ডাল",
        "family": "legume", "slot": "rabi",
        "sow": 11.5, "harvest": 3.0, "days": 105,
        "kc_avg": 0.70,
        "ect_dsm": 1.5, "slope_pct": 20.0, "sal_source": "indicative",
        "heat_sensitive_window": [2.5, 3.0], "heat_sens": 1.0,
        "irrigation": "none",
        "gross_margin_bdt_ha": 52000, "gm_flag": "indicative",
        "soil": 1.5,  # legume: nitrogen fixation
        "note_en": "Rainfed on residual soil moisture; fixes nitrogen; salinity-sensitive (indicative)",
    },
    "chickpea": {
        "en": "Chickpea", "bn": "ছোলা",
        "family": "legume", "slot": "rabi",
        "sow": 11.5, "harvest": 3.0, "days": 105,
        "kc_avg": 0.70,
        "ect_dsm": 1.3, "slope_pct": 14.0, "sal_source": "indicative",
        "heat_sensitive_window": [2.5, 3.0], "heat_sens": 1.0,
        "irrigation": "none",
        "gross_margin_bdt_ha": 48000, "gm_flag": "indicative",
        "soil": 1.5,
        "note_en": "Barind tract favourite; legume rotation benefit",
    },
    "onion": {
        "en": "Onion", "bn": "পিঁয়াজ",
        "family": "vegetable", "slot": "rabi",
        "sow": 11.5, "harvest": 3.5, "days": 110,
        "kc_avg": 0.85,
        "ect_dsm": 1.2, "slope_pct": 16.0, "sal_source": "fao29",
        "heat_sensitive_window": [3.0, 3.5], "heat_sens": 0.8,
        "irrigation": "partial",
        "gross_margin_bdt_ha": 150000, "gm_flag": "indicative",
        "soil": -0.1,
        "note_en": "High value; FAO-29 salinity-sensitive (ECt 1.2)",
    },
    "sunflower": {
        "en": "Sunflower", "bn": "সূর্যমুখী",
        "family": "oilseed", "slot": "rabi",
        "sow": 12.0, "harvest": 4.0, "days": 115,
        "kc_avg": 0.85,
        "ect_dsm": 4.5, "slope_pct": 12.0, "sal_source": "indicative",
        "heat_sensitive_window": [3.0, 4.0], "heat_sens": 0.8,
        "irrigation": "light",
        "gross_margin_bdt_ha": 72000, "gm_flag": "indicative",
        "soil": 0.0,
        "note_en": "Promoted for coastal saline soils; deep taproot; moderate salinity tolerance (indicative)",
    },
    "groundnut": {
        "en": "Groundnut", "bn": "চিনাবাদাম",
        "family": "legume", "slot": "rabi",
        "sow": 1.0, "harvest": 4.5, "days": 120,
        "kc_avg": 0.75,
        "ect_dsm": 3.2, "slope_pct": 29.0, "sal_source": "fao29",
        "heat_sensitive_window": [4.0, 4.5], "heat_sens": 0.6,
        "irrigation": "light",
        "gross_margin_bdt_ha": 85000, "gm_flag": "indicative",
        "soil": 1.2,
        "note_en": "FAO-29 moderate tolerance (ECt 3.2); legume; coastal favourite on raised beds",
    },
    "sesame": {
        "en": "Sesame", "bn": "তিল",
        "family": "oilseed", "slot": "rabi",
        "sow": 11.0, "harvest": 2.0, "days": 85,
        "kc_avg": 0.65,
        "ect_dsm": 2.5, "slope_pct": 14.0, "sal_source": "indicative",
        "heat_sensitive_window": [1.5, 2.0], "heat_sens": 0.5,
        "irrigation": "none",
        "gross_margin_bdt_ha": 45000, "gm_flag": "indicative",
        "soil": 0.0,
        "note_en": "Short-cycle, drought-hardy; grown on residual moisture",
    },
    "rabi_fallow": {
        "en": "Fallow (Rabi)", "bn": "পতিত (রবি)",
        "family": "fallow", "slot": "rabi",
        "sow": 11.0, "harvest": 4.5, "days": 0,
        "kc_avg": 0.0, "ect_dsm": 99, "slope_pct": 0, "sal_source": "n/a",
        "irrigation": "none", "gross_margin_bdt_ha": 0, "gm_flag": "n/a",
        "soil": -0.8, "heat_sens": 0.0,
        "note_en": "No crop grown; soil exposed, salinity builds unchecked",
    },
    # ---- Kharif-1 (pre-monsoon) crops ---------------------------------------------
    "mungbean": {
        "en": "Mungbean", "bn": "মুগ ডাল",
        "family": "legume", "slot": "kharif1",
        "sow": 4.0, "harvest": 6.0, "days": 60,
        "kc_avg": 0.70,
        "ect_dsm": 2.0, "slope_pct": 15.0, "sal_source": "indicative",
        "heat_sensitive_window": [5.5, 6.0], "heat_sens": 0.8,
        "irrigation": "none",
        "gross_margin_bdt_ha": 58000, "gm_flag": "indicative",
        "soil": 1.5,
        "note_en": "Short pre-monsoon legume; fits between Rabi harvest and T. Aman; salinity-sensitive (indicative)",
    },
    "jute": {
        "en": "Jute", "bn": "পাট",
        "family": "fiber", "slot": "kharif1",
        "sow": 4.0, "harvest": 7.0, "days": 100,
        "kc_avg": 0.95,
        "ect_dsm": 3.0, "slope_pct": 14.0, "sal_source": "indicative",
        "heat_sensitive_window": [6.0, 7.0], "heat_sens": 0.4,
        "irrigation": "none",
        "gross_margin_bdt_ha": 78000, "gm_flag": "indicative",
        "soil": -0.2,
        "note_en": "Natural fibre cash crop; tolerant of wet acidic soils",
    },
    "k1_fallow": {
        "en": "Fallow (Kharif-1)", "bn": "পতিত (খরিফ-১)",
        "family": "fallow", "slot": "kharif1",
        "sow": 4.0, "harvest": 6.5, "days": 0,
        "kc_avg": 0.0, "ect_dsm": 99, "slope_pct": 0, "sal_source": "n/a",
        "irrigation": "none", "gross_margin_bdt_ha": 0, "gm_flag": "n/a",
        "soil": -0.3, "heat_sens": 0.0,
        "note_en": "No crop grown in pre-monsoon window",
    },
}

SLOT_CROPS = {
    "kharif2": ["t_aman", "k2_fallow"],
    "rabi": ["boro_hyv", "boro_salt", "wheat", "maize", "potato", "mustard",
             "lentil", "chickpea", "onion", "sunflower", "groundnut", "sesame",
             "rabi_fallow"],
    "kharif1": ["mungbean", "jute", "k1_fallow"],
}

BASELINES = {
    # "business as usual" reference sequences by zone
    "coastal-saline": ["t_aman", "rabi_fallow", "k1_fallow"],   # T.Aman + fallow
    "coastal-inland": ["t_aman", "boro_hyv", "k1_fallow"],
    "central": ["t_aman", "boro_hyv", "k1_fallow"],
    "barind": ["t_aman", "boro_hyv", "k1_fallow"],
    "haor": ["k2_fallow", "boro_hyv", "k1_fallow"],             # single Boro
    "hilly": ["t_aman", "rabi_fallow", "k1_fallow"],
}


def months_span(sow, harvest, days_hint=0):
    """Return list of month indices (1-12) covered by a growing window that may
    wrap the year end (e.g. sow 12.5 -> harvest 4.5)."""
    out = []
    m = int(sow)
    end = int(harvest)
    while True:
        out.append(((m - 1) % 12) + 1)
        if m == end:
            break
        m = ((m) % 12) + 1
        if len(out) > 12:
            break
    return out


def effective_rain(p_mm):
    return 0.6 * p_mm if p_mm < 70 else 0.8 * p_mm - 24


def crop_water_use(crop, ctx):
    """Estimate seasonal irrigation need (mm) and rainfed share for a crop in a
    district, using monthly ETo climatology, Kc, and effective rainfall
    (FAO AGLW). Returns (irrigation_mm, etc_mm, pe_mm)."""
    months = months_span(crop["sow"], crop["harvest"])
    eto_clim = ctx["eto_clim"]          # 12 monthly ETo mm/day (recent decade)
    pre_clim = ctx["pre_clim_mm"]       # 12 monthly rainfall mm (recent decade)
    etc = pe = 0.0
    for m in months:
        e = eto_clim[m - 1] if eto_clim and eto_clim[m - 1] else None
        p = pre_clim[m - 1] if pre_clim and pre_clim[m - 1] else 0.0
        if e is None:
            continue
        # approximate day weighting for partial months at window edges
        etc += crop["kc_avg"] * e * 30
        pe += effective_rain(p)
    irr = max(0.0, etc - pe)
    # irrigation mode discount (rice flooded: standing water, higher percolation
    # is accounted by higher Kc; light-irrigation crops get 0.7 factor)
    mode = crop["irrigation"]
    if mode == "full":
        irr *= 1.15   # puddling + percolation in rice fields
    elif mode == "partial":
        irr *= 0.85
    elif mode == "light":
        irr *= 0.7
    elif mode in ("none", "rainfed"):
        irr *= 0.0 if mode == "none" else 0.5  # supplemental only for rainfed rice
    return round(irr), round(etc), round(pe)


def maas_hoffman(ect, slope, ece):
    """Relative yield (%) under soil salinity Ece (dS/m) - Maas & Hoffman 1977."""
    if ece <= ect:
        return 100.0
    return max(0.0, 100.0 - slope * (ece - ect))


def build_rotations(context):
    """Enumerate feasible annual 3-slot rotations and compute biophysical
    metrics per rotation for a district context. Returns list of dicts."""
    from itertools import product

    ctx = context
    base_sal = ctx["base_salinity"]
    # seasonal salinity envelope: dry season peak vs monsoon leached
    sal_rabi = base_sal * 1.35           # peak dry-season concentration
    sal_k2 = base_sal * 0.55             # monsoon leached
    sal_k1 = base_sal * 0.9
    heat = ctx.get("heat_days_annual")

    rows = []
    for k2, rb, k1 in product(SLOT_CROPS["kharif2"], SLOT_CROPS["rabi"],
                              SLOT_CROPS["kharif1"]):
        crops = [CROPS[k2], CROPS[rb], CROPS[k1]]
        # skip all-fallow
        if all(c["family"] == "fallow" for c in crops):
            continue
        irr_total = etc_total = pe_total = 0.0
        sal_yields = []
        heat_pen = 0.0
        gm_total = 0.0
        soil = 0.0
        n_real = 0
        for c, s_sal in zip(crops, [sal_k2, sal_rabi, sal_k1]):
            if c["family"] == "fallow":
                soil += c["soil"]
                continue
            irr, etc, pe = crop_water_use(c, ctx)
            irr_total += irr
            etc_total += etc
            pe_total += pe
            sy = maas_hoffman(c["ect_dsm"], c["slope_pct"], s_sal)
            sal_yields.append(sy)
            # expected gross margin adjusted by salinity-reduced relative yield
            gm_total += c["gross_margin_bdt_ha"] * (sy / 100.0)
            if heat:
                hs, he = c.get("heat_sensitive_window", (0, 0))
                share = max(0.0, (he - hs)) / 12.0
                heat_pen += share * c.get("heat_sens", 0) * (heat / 100.0)
            soil += c["soil"]
            n_real += 1
        sal_avg = sum(sal_yields) / len(sal_yields) if sal_yields else 100.0
        # continuous rice penalty
        if sum(1 for c in crops if c["family"] == "cereal") >= 2:
            soil -= 0.6
        families = {c["family"] for c in crops if c["family"] != "fallow"}
        rows.append({
            "k2": k2, "rabi": rb, "k1": k1,
            "names_en": [CROPS[k2]["en"], CROPS[rb]["en"], CROPS[k1]["en"]],
            "names_bn": [CROPS[k2]["bn"], CROPS[rb]["bn"], CROPS[k1]["bn"]],
            "irrigation_mm": round(irr_total),
            "etc_mm": round(etc_total),
            "rainfed_share": round(pe_total / etc_total, 2) if etc_total else 1.0,
            "salinity_yield_pct": round(sal_avg, 1),
            "heat_risk_index": round(heat_pen, 3),
            "gross_margin_bdt": round(gm_total),
            "soil_health": round(soil + 1.5, 2),  # shift to ~0..3 scale
            "diversity": len(families),
        })
    return rows


# default farmer-priority weights (the dashboard exposes these as sliders)
DEFAULT_WEIGHTS = {
    "water": 0.20, "salinity": 0.25, "profit": 0.20,
    "soil": 0.15, "risk": 0.20,
}


def score_rotations(rotations, context=None, weights=None):
    """Normalize metrics to 0-100 and compute weighted score."""
    w = weights or DEFAULT_WEIGHTS
    if not rotations:
        return []
    irr = [r["irrigation_mm"] for r in rotations]
    sal = [r["salinity_yield_pct"] for r in rotations]
    gm = [r["gross_margin_bdt"] for r in rotations]
    sh = [r["soil_health"] for r in rotations]
    hr = [r["heat_risk_index"] for r in rotations]

    def norm(v, lo, hi):
        if hi - lo < 1e-9:
            return 50.0
        return 100.0 * (v - lo) / (hi - lo)

    lo_i, hi_i = min(irr), max(irr)
    lo_s, hi_s = min(sal), max(sal)
    lo_g, hi_g = min(gm), max(gm)
    lo_h, hi_h = min(sh), max(sh)
    lo_r, hi_r = min(hr), max(hr)

    for r in rotations:
        s_water = 100 - norm(r["irrigation_mm"], lo_i, hi_i)
        s_sal = norm(r["salinity_yield_pct"], lo_s, hi_s)
        s_prof = norm(r["gross_margin_bdt"], lo_g, hi_g)
        s_soil = norm(r["soil_health"], lo_h, hi_h)
        s_risk = 100 - norm(r["heat_risk_index"], lo_r, hi_r)
        score = (w["water"] * s_water + w["salinity"] * s_sal +
                 w["profit"] * s_prof + w["soil"] * s_soil + w["risk"] * s_risk)
        r["scores"] = {"water": round(s_water), "salinity": round(s_sal),
                       "profit": round(s_prof), "soil": round(s_soil),
                       "risk": round(s_risk)}
        r["score"] = round(score, 1)
    rotations.sort(key=lambda r: -r["score"])
    return rotations
