#!/usr/bin/env python3
"""
MOUSUMI — NASA POWER data fetcher
=================================
Downloads REAL NASA Earth observation data for all 64 districts of Bangladesh
from the official NASA POWER API (https://power.larc.nasa.gov/docs/services/v2/)

Two products per district:
  1. MONTHLY  (1981-2026): 7 agro-meteorological parameters
     - PRECTOTCORR   : precipitation (mm, corrected)
     - T2M           : air temperature at 2m (degC)
     - T2M_MAX/MIN   : monthly mean of daily max/min temperature
     - RH2M          : relative humidity at 2m (%)
     - WS2M          : wind speed at 2m (m/s)
     - ALLSKY_SFC_SW_DWN : all-sky solar radiation at surface (MJ/m2/day)
  2. DAILY (1981-2026, Apr-May window analysis done later; full series kept):
     - T2M_MAX       : daily maximum temperature (for extreme-heat day counts)
     - PRECTOTCORR   : daily precipitation (for monsoon onset/withdrawal)

NASA POWER citation:
  Stackhouse, P. W., et al. (2023). NASA POWER v8/CRC (Prediction Of Worldwide
  Energy Resources), NASA Langley Research Center. https://power.larc.nasa.gov/

Usage:
    python3 fetch_power.py            # fetch all districts (resumable)
    python3 fetch_power.py --test     # fetch 2 districts only (quick check)
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from districts import DISTRICTS  # noqa: E402

BASE = "https://power.larc.nasa.gov/api/temporal"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)

MONTHLY_PARAMS = "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN"
DAILY_PARAMS = "PRECTOTCORR,T2M_MAX"
START, END = "19810101", "20260930"  # 45+ year record through Sep 2026


def slug(name):
    return name.lower().replace(" ", "_").replace("'", "")


def fetch(url, retries=4, timeout=180):
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MOUSUMI-SpaceApps-2026/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            if attempt == retries:
                raise
            time.sleep(2 * attempt)
    return None


def fetch_monthly(name, lat, lon):
    out = os.path.join(RAW, f"monthly_{slug(name)}.json")
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return f"{name}: cached"
    url = (f"{BASE}/monthly/point?parameters={MONTHLY_PARAMS}&community=AG"
           f"&start=1981&end=2026&latitude={lat}&longitude={lon}"
           f"&format=JSON&time-standard=LST")
    data = fetch(url)
    if data.get("header", {}).get("messages"):
        return f"{name}: ERROR {data['header']['messages']}"
    with open(out, "w") as f:
        json.dump(data, f)
    return f"{name}: monthly OK"


def fetch_daily(name, lat, lon):
    out = os.path.join(RAW, f"daily_{slug(name)}.json")
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return f"{name}: cached"
    url = (f"{BASE}/daily/point?parameters={DAILY_PARAMS}&community=AG"
           f"&start={START}&end={END}&latitude={lat}&longitude={lon}"
           f"&format=JSON&time-standard=LST")
    data = fetch(url)
    if data.get("header", {}).get("messages"):
        return f"{name}: ERROR {data['header']['messages']}"
    with open(out, "w") as f:
        json.dump(data, f)
    return f"{name}: daily OK"


def process_district(d):
    name, _div, lat, lon, _zone = d
    m = fetch_monthly(name, lat, lon)
    dly = fetch_daily(name, lat, lon)
    return f"{m} | {dly}"


def main():
    test = "--test" in sys.argv
    targets = DISTRICTS[:2] if test else DISTRICTS
    print(f"Fetching NASA POWER data for {len(targets)} districts ...")
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(process_district, d): d[0] for d in targets}
        for fut in as_completed(futs):
            try:
                results.append(fut.result())
                print(f"  [{len(results)}/{len(targets)}] {results[-1]}")
            except Exception as e:  # noqa: BLE001
                errors.append(f"{futs[fut]}: {e}")
                print(f"  ERROR {futs[fut]}: {e}")
    print(f"\nDone. OK={len(results)} ERRORS={len(errors)}")
    for e in errors:
        print(" ", e)


if __name__ == "__main__":
    main()
