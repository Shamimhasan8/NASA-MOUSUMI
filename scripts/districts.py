"""
MOUSUMI — Bangladesh district reference data
All 64 districts (zila) of Bangladesh with:
  - approximate geographic centroid (lat, lon) — used for NASA POWER point queries
  - division membership
  - agro-ecological stress class (for narrative layering, analysis is data-driven)

Coordinates are district centroids accurate enough for 0.5° x 0.625° POWER grid cells.
Sources: Bangladesh Bureau of Statistics district maps; coordinates rounded to 2 dp.
"""

DISTRICTS = [
    # --- Dhaka Division ---
    ("Dhaka",        "Dhaka",       23.81, 90.41, "central"),
    ("Faridpur",     "Dhaka",       23.60, 89.83, "central"),
    ("Gazipur",      "Dhaka",       24.00, 90.42, "central"),
    ("Gopalganj",    "Dhaka",       23.01, 89.83, "coastal-inland"),
    ("Kishoreganj",  "Dhaka",       24.44, 90.78, "haor"),
    ("Madaripur",    "Dhaka",       23.16, 90.19, "coastal-inland"),
    ("Manikganj",    "Dhaka",       23.86, 90.00, "central"),
    ("Munshiganj",   "Dhaka",       23.54, 90.53, "central"),
    ("Narayanganj",  "Dhaka",       23.62, 90.50, "central"),
    ("Narsingdi",    "Dhaka",       23.92, 90.72, "central"),
    ("Rajbari",      "Dhaka",       23.76, 89.64, "central"),
    ("Shariatpur",   "Dhaka",       23.21, 90.35, "coastal-inland"),
    ("Tangail",      "Dhaka",       24.25, 89.92, "central"),
    # --- Chattogram Division ---
    ("Bandarban",    "Chattogram",  22.20, 92.22, "hilly"),
    ("Brahmanbaria", "Chattogram",  23.96, 91.11, "haor"),
    ("Chandpur",     "Chattogram",  23.23, 90.65, "coastal-inland"),
    ("Chattogram",   "Chattogram",  22.34, 91.83, "coastal"),
    ("Cumilla",      "Chattogram",  23.46, 91.18, "central"),
    ("Cox's Bazar",  "Chattogram",  21.44, 92.00, "coastal"),
    ("Feni",         "Chattogram",  23.02, 91.40, "coastal"),
    ("Khagrachhari", "Chattogram",  23.12, 91.98, "hilly"),
    ("Lakshmipur",   "Chattogram",  22.94, 90.83, "coastal"),
    ("Noakhali",     "Chattogram",  22.87, 91.10, "coastal"),
    ("Rangamati",    "Chattogram",  22.66, 92.17, "hilly"),
    # --- Rajshahi Division (incl. drought-prone Barind Tract) ---
    ("Bogura",       "Rajshahi",    24.85, 89.37, "barind"),
    ("Chapainawabganj","Rajshahi",  24.60, 88.28, "barind"),
    ("Joypurhat",    "Rajshahi",    25.10, 89.02, "barind"),
    ("Naogaon",      "Rajshahi",    24.94, 88.93, "barind"),
    ("Natore",       "Rajshahi",    24.42, 89.00, "barind"),
    ("Pabna",        "Rajshahi",    24.00, 89.24, "central"),
    ("Rajshahi",     "Rajshahi",    24.37, 88.60, "barind"),
    ("Sirajganj",    "Rajshahi",    24.45, 89.70, "central"),
    # --- Khulna Division (coastal salinity belt) ---
    ("Bagerhat",     "Khulna",      22.65, 89.79, "coastal-saline"),
    ("Chuadanga",    "Khulna",      23.64, 88.84, "central"),
    ("Jashore",      "Khulna",      23.17, 89.21, "central"),
    ("Jhenaidah",    "Khulna",      23.54, 89.17, "central"),
    ("Khulna",       "Khulna",      22.82, 89.55, "coastal-saline"),
    ("Kushtia",      "Khulna",      23.90, 89.12, "central"),
    ("Magura",       "Khulna",      23.49, 89.42, "central"),
    ("Meherpur",     "Khulna",      23.77, 88.63, "central"),
    ("Narail",       "Khulna",      23.17, 89.50, "central"),
    ("Satkhira",     "Khulna",      22.72, 89.07, "coastal-saline"),
    # --- Barishal Division (coastal) ---
    ("Barguna",      "Barishal",    22.16, 90.13, "coastal-saline"),
    ("Barishal",     "Barishal",    22.70, 90.37, "coastal-inland"),
    ("Bhola",        "Barishal",    22.69, 90.64, "coastal-saline"),
    ("Jhalokati",    "Barishal",    22.64, 90.20, "coastal-inland"),
    ("Patuakhali",   "Barishal",    22.36, 90.33, "coastal-saline"),
    ("Pirojpur",     "Barishal",    22.58, 89.97, "coastal-saline"),
    # --- Sylhet Division (haor wetlands) ---
    ("Habiganj",     "Sylhet",      24.38, 91.42, "haor"),
    ("Moulvibazar",  "Sylhet",      24.48, 91.78, "haor"),
    ("Sunamganj",    "Sylhet",      25.07, 91.39, "haor"),
    ("Sylhet",       "Sylhet",      24.90, 91.87, "haor"),
    # --- Rangpur Division ---
    ("Dinajpur",     "Rangpur",     25.63, 88.64, "barind"),
    ("Gaibandha",    "Rangpur",     25.33, 89.55, "central"),
    ("Kurigram",     "Rangpur",     25.81, 89.65, "central"),
    ("Lalmonirhat",  "Rangpur",     25.99, 89.45, "barind"),
    ("Nilphamari",   "Rangpur",     25.93, 88.86, "barind"),
    ("Panchagarh",   "Rangpur",     26.34, 88.56, "barind"),
    ("Rangpur",      "Rangpur",     25.75, 89.25, "barind"),
    ("Thakurgaon",   "Rangpur",     26.03, 88.47, "barind"),
    # --- Mymensingh Division ---
    ("Jamalpur",     "Mymensingh",  24.92, 89.94, "central"),
    ("Mymensingh",   "Mymensingh",  24.75, 90.40, "haor"),
    ("Netrokona",    "Mymensingh",  24.88, 90.73, "haor"),
    ("Sherpur",      "Mymensingh",  25.02, 90.02, "central"),
]

assert len(DISTRICTS) == 64, f"Expected 64 districts, got {len(DISTRICTS)}"

# District-level baseline soil salinity context (dS/m, approximate median of the
# 0-30 cm root zone in saline-affected upazilas, dry season).
# Sources: SRDI (2010) salinity survey as reported in Dasgupta et al. (2015),
# World Bank Policy Research Working Paper 7140; FAO country reports.
# Non-coastal districts: baseline ~1-2 dS/m (not salinity constrained).
# These are EDITABLE defaults in the tool; users can enter measured values
# from their own soil tests (the "local soil information" input).
BASELINE_SALINITY_DS_M = {
    "Satkhira": 6.0, "Khulna": 5.0, "Bagerhat": 4.5, "Patuakhali": 4.0,
    "Barguna": 4.0, "Bhola": 3.5, "Pirojpur": 3.0, "Jhalokati": 2.5,
    "Barishal": 2.5, "Gopalganj": 2.5, "Madaripur": 2.5, "Shariatpur": 2.0,
    "Jashore": 2.5, "Narail": 2.0, "Chuadanga": 2.0, "Magura": 1.5,
    "Meherpur": 1.8, "Jhenaidah": 1.8, "Kushtia": 1.5,
    "Noakhali": 3.5, "Lakshmipur": 3.0, "Feni": 2.5, "Chandpur": 2.0,
    "Cox's Bazar": 3.0, "Chattogram": 2.0, "Brahmanbaria": 1.2,
    # inland districts (indicative low baseline)
    "_default_inland": 1.2,
}

BANGLA_NAMES = {
    "Dhaka": "ঢাকা", "Faridpur": "ফরিদপুর", "Gazipur": "গাজীপুর",
    "Gopalganj": "গোপালগঞ্জ", "Kishoreganj": "কিশোরগঞ্জ", "Madaripur": "মাদারীপুর",
    "Manikganj": "মানিকগঞ্জ", "Munshiganj": "মুন্সিগঞ্জ", "Narayanganj": "নারায়ণগঞ্জ",
    "Narsingdi": "নরসিংদী", "Rajbari": "রাজবাড়ী", "Shariatpur": "শরীয়তপুর",
    "Tangail": "টাঙ্গাইল", "Bandarban": "বান্দরবান", "Brahmanbaria": "ব্রাহ্মণবাড়িয়া",
    "Chandpur": "চাঁদপুর", "Chattogram": "চট্টগ্রাম", "Cumilla": "কুমিল্লা",
    "Cox's Bazar": "কক্সবাজার", "Feni": "ফেনী", "Khagrachhari": "খাগড়াছড়ি",
    "Lakshmipur": "লক্ষ্মীপুর", "Noakhali": "নোয়াখালী", "Rangamati": "রাঙ্গামাটি",
    "Bogura": "বগুড়া", "Chapainawabganj": "চাঁপাইনবাবগঞ্জ", "Joypurhat": "জয়পুরহাট",
    "Naogaon": "নওগাঁ", "Natore": "নাটোর", "Pabna": "পাবনা", "Rajshahi": "রাজশাহী",
    "Sirajganj": "সিরাজগঞ্জ", "Bagerhat": "বাগেরহাট", "Chuadanga": "চুয়াডাঙ্গা",
    "Jashore": "যশোর", "Jhenaidah": "ঝিনাইদহ", "Khulna": "খুলনা", "Kushtia": "কুষ্টিয়া",
    "Magura": "মাগুরা", "Meherpur": "মেহেরপুর", "Narail": "নড়াইল",
    "Satkhira": "সাতক্ষীরা", "Barguna": "বরগুনা", "Barishal": "বরিশাল",
    "Bhola": "ভোলা", "Jhalokati": "ঝালকাঠি", "Patuakhali": "পটুয়াখালী",
    "Pirojpur": "পিরোজপুর", "Habiganj": "হবিগঞ্জ", "Moulvibazar": "মৌলভীবাজার",
    "Sunamganj": "সুনামগঞ্জ", "Sylhet": "সিলেট", "Dinajpur": "দিনাজপুর",
    "Gaibandha": "গাইবান্ধা", "Kurigram": "কুড়িগ্রাম", "Lalmonirhat": "লালমনিরহাট",
    "Nilphamari": "নীলফামারী", "Panchagarh": "পঞ্চগড়", "Rangpur": "রংপুর",
    "Thakurgaon": "ঠাকুরগাঁও", "Jamalpur": "জামালপুর", "Mymensingh": "ময়মনসিংহ",
    "Netrokona": "নেত্রকোণা", "Sherpur": "শেরপুর",
}

DIVISION_BANGLA = {
    "Dhaka": "ঢাকা", "Chattogram": "চট্টগ্রাম", "Rajshahi": "রাজশাহী",
    "Khulna": "খুলনা", "Barishal": "বরিশাল", "Sylhet": "সিলেট",
    "Rangpur": "রংপুর", "Mymensingh": "ময়মনসিংহ",
}
