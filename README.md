# MOUSUMI 🌾
### Farming with the Shifting Seasons — NASA-powered Crop Rotation Advisor for Bangladesh

**মৌসুমী — বদলে যাওয়া ঋতুর সাথে চাষাবাদ**

> **NASA Space Apps Challenge 2026** · Challenge: **Field Shift: Adapting Farms with NASA Data**
> Team **Cou_Black_Forest** — Sakhawat Hossen & Shamim Hasan · Cumilla, Bangladesh

---

## What is MOUSUMI?

MOUSUMI (Bangla: *মৌসুমী* — "of the seasons") is a decision-support tool that helps Bangladeshi farmers and agricultural extension officers explore **climate-adapted crop rotation strategies** — exactly what the *Field Shift* challenge asks for. It combines:

- **NASA Earth observations** — 45 years (1981–2025) of NASA POWER agroclimatology for **all 64 districts** of Bangladesh (live-fetched from the official POWER API)
- **Local soil information** — SRDI-informed district baseline soil salinity, *editable by the user* (enter your own soil-test value)
- **Crop characteristics** — 15 Bangladesh crops with FAO-56 crop coefficients, FAO-29 salt-tolerance parameters (Maas-Hoffman model), BRRI salt-tolerant varieties (BRRI dhan67)
- **Farmer priorities** — interactive sliders re-rank every rotation plan live: water saving, salinity survival, income, soil health, risk

The output is a ranked set of feasible annual rotation plans (Kharif-2 → Rabi → Kharif-1) with, for each plan: irrigation requirement (mm), salinity-adjusted expected yield (%), expected gross margin (৳/ha), soil-health score, heat-risk index — always shown **versus the district's current practice**.

## Quick start

The dashboard is a **single self-contained HTML file** — no build step, no server, works offline after download.

```bash
# 1. Open the dashboard
open index.html          # or double-click it in any modern browser

# 2. (Optional) Re-fetch the latest NASA POWER data (needs internet, ~3 min)
pip install -r requirements.txt   # only needed for the scripts
python3 scripts/fetch_power.py    # re-downloads all 64 districts

# 3. (Optional) Re-run the full analysis pipeline
python3 scripts/analyze.py        # rebuilds data/processed/mousumi_data.json
python3 - <<'EOF'                 # regenerate the .js wrapper for offline use
import json
d = json.load(open('data/processed/mousumi_data.json'))
with open('data/processed/mousumi_data.js','w') as f:
    f.write('window.MOUSUMI_DATA = '); json.dump(d,f,separators=(',',':'),ensure_ascii=False); f.write(';\n')
EOF
```

To host online (recommended for judges): push this folder to GitHub and enable **GitHub Pages** — `index.html` works as-is.

## Repository structure

```
mousumi/
├── index.html                      # the dashboard (open in any browser)
├── README.md
├── LICENSE (MIT)
├── requirements.txt
├── scripts/
│   ├── districts.py                # 64 districts: coordinates, zones, baselines
│   ├── fetch_power.py              # NASA POWER API fetcher (real data, resumable)
│   ├── crop_library.py             # crop parameters + rotation engine
│   └── analyze.py                  # science pipeline (MK/Sen, FAO-56, water balance)
├── data/
│   ├── raw/                        # 128 NASA POWER API responses (64 monthly + 64 daily)
│   └── processed/
│       ├── mousumi_data.json       # analysis output (954 KB)
│       └── mousumi_data.js         # offline wrapper for the dashboard
└── docs/
    └── screenshot_*.png            # dashboard screenshots
```

## The science inside (and where each number comes from)

| Component | Method | Source |
|---|---|---|
| Reference evapotranspiration (ETo) | FAO-56 Penman-Monteith, monthly step | Allen et al. 1998, FAO I&D Paper 56 |
| Crop water use | ETc = Kc × ETo | FAO-56 Tables 11–12 |
| Effective rainfall | FAO AGLW monthly method | FAO |
| Crop salt tolerance | Yrel = 100 − b·(ECe − ECt) | Maas & Hoffman 1977; FAO I&D Paper 29 (Ayers & Westcot 1985) |
| Salt-tolerant rice | BRRI dhan67, 8–10 dS/m (vegetative), 4.5–5.0 t/ha | BRRI variety documentation |
| Trend testing | Mann-Kendall (tie-corrected) + Theil-Sen slope, 2011–2025 | Mann 1945; Kendall 1975; Sen 1968 |
| Monsoon calendar | Onset: first day after 25 May with ≥60 mm/10 d AND ≥40 mm in next 10 d; withdrawal: last ≥60 mm/10-d window after 15 Sep | transparent criterion, documented |
| Heat risk | Days with Tmax ≥ 35 °C (rice anthesis-sterility threshold) | Yoshida 1981 (IRRI) |
| District baseline salinity | compiled from SRDI (2010) survey as reported in Dasgupta et al. 2015 | SRDI; World Bank PRWP 7140 |
| Data source | NASA POWER v8 API, monthly + daily, 1981–2025 | NASA Langley Research Center |

## Scientific integrity: the data audit

We did **not** take the 45-year NASA POWER record at face value. Our homogeneity audit (visible in the dashboard's *District Dashboard → transparency view* and *Data & Methods* tab) found **large multi-decadal discontinuities** in POWER v8 over Bangladesh: e.g., the Sylhet grid cell's decadal-mean rainfall roughly doubles between 1981–90 and 2021–25, and 1980s daily Tmax is warm-biased by ~2–3 °C versus gauge climatology — consistent with known limitations of reanalysis-based products in the tropics.

**Methodological consequences (deliberate design choices):**
1. Current-condition modelling (water balance, rotation engine) uses the recent, internally consistent **2016–2025 window**.
2. Tendencies are computed over **2011–2025** and labelled *indicative*.
3. Long-term climate-change direction is cited from peer-reviewed literature (IPCC AR6; World Bank salinity projections), **not** extrapolated from an inhomogeneous reanalysis.
4. The full 45-year record stays visible in the dashboard **for transparency**, next to the audit table.

We believe a tool that advises farmers must audit its data first. This is a feature, not an apology.

## Verified details worth knowing

- NASA POWER monthly `PRECTOTCORR` is a **mm/day rate** (we verified empirically: monthly-value × days-in-month reproduces daily sums to ratio 1.000).
- NASA POWER monthly `T2M_MAX` is a **monthly extreme**, not the mean of daily maxima (verified empirically against the daily product) — so we compute monthly mean Tmax from the daily product, and estimate mean Tmin as 2·T2M − Tmax for FAO-56.
- POWER grid resolution is 0.5° × 0.625°, so neighbouring districts within one cell share values — district-level precision comes from the user's own soil input, which is precisely the "local soil information" the challenge asks the tool to incorporate.

## Assumptions & limitations (honest list)

1. Salinity envelope: rabi peak ≈ 1.35 × baseline; monsoon-leached ≈ 0.55 × baseline (first-order seasonalisation of the salt cycle; full salt-transport modelling is future work).
2. Gross margins are indicative 2023–25 farm-gate estimates — editable, and the tool explicitly encourages local calibration with DAE/BBS figures.
3. Salinity thresholds marked `indicative` in the crop table apply where FAO-29 does not tabulate a crop.
4. MOUSUMI is a planning-support and education tool, not a substitute for professional agronomic advice.
5. The Mann-Kendall implementation does not pre-whiten for serial correlation; with 15-year windows this is a known, documented simplification.

## Complementary NASA data (extension path)

The core pipeline runs on NASA POWER (open, no authentication, ideal for a hackathon). The architecture is designed to absorb, without code changes to the engine:
- **GPM IMERG** (higher-resolution rainfall; GES DISC, free Earthdata account)
- **SMAP** surface soil moisture (NSIDC) for dry-season soil-moisture stress
- **MODIS/VIIRS** NDVI & LST (AppEEARS/FIRMS) for in-season crop condition
- **NASA Earthdata Worldview** snapshots for visual context

## References

- Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998). *Crop evapotranspiration*. FAO I&D Paper 56.
- Ayers, R.S., Westcot, D.W. (1985). *Water quality for agriculture*. FAO I&D Paper 29.
- Maas, E.V., Hoffman, G.J. (1977). Crop salt tolerance — current assessment. *J. Irrig. Drain. Div.* 103(IR2).
- Mann, H.B. (1945); Kendall, M.G. (1975); Sen, P.K. (1968) — trend tests.
- Dasgupta, S., Hossain, M.M., Huq, M., Wheeler, D. (2015). *Climate change, soil salinity, and the economics of high-yield rice production in coastal Bangladesh*. World Bank PRWP 7140.
- SRDI (2010). *Saline soils of Bangladesh*. Soil Resource Development Institute.
- Yoshida, S. (1981). *Fundamentals of rice crop science*. IRRI.
- BRRI variety leaflets (BRRI dhan67).
- Stackhouse, P.W. et al. NASA POWER v8. NASA Langley Research Center. https://power.larc.nasa.gov
- IPCC (2022). AR6 WGII Chapter 10: Asia.

## License

MIT — use it, improve it, plant with it. 🌱
