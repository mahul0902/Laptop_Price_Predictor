import pandas as pd
import numpy as np
import re
import pickle
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, r2_score

# ── 1. Load data ──────────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data.csv'))
print(f"Loaded {len(df)} rows")

# ── 2. Feature engineering ────────────────────────────────────────────────────

# Extract RAM GB as integer
df['ram_gb'] = df['Ram'].str.extract(r'(\d+)').astype(int)

# Extract ROM GB as integer (TB → GB)
def parse_rom(val):
    val = str(val).strip()
    if 'TB' in val:
        return int(re.search(r'(\d+)', val).group(1)) * 1024
    return int(re.search(r'(\d+)', val).group(1))

df['rom_gb'] = df['ROM'].apply(parse_rom)

# Normalise RAM type (collapse minor variants)
def norm_ram_type(t):
    t = str(t).strip().upper().replace('-', '')
    if 'LPDDR5' in t:   return 'LPDDR5'
    if 'LPDDR4' in t:   return 'LPDDR4'
    if 'DDR5'   in t:   return 'DDR5'
    if 'DDR4'   in t:   return 'DDR4'
    if 'DDR3'   in t:   return 'DDR3'
    if 'DDR'    in t:   return 'DDR'
    return 'Other'

df['ram_type_clean'] = df['Ram_type'].apply(norm_ram_type)

# Normalise OS
def norm_os(o):
    o = str(o).strip().lower()
    if 'mac'     in o: return 'Mac OS'
    if 'windows 11' in o: return 'Windows 11'
    if 'windows 10' in o: return 'Windows 10'
    if 'windows' in o: return 'Windows'
    if 'ubuntu'  in o: return 'Ubuntu'
    if 'chrome'  in o: return 'Chrome OS'
    if 'android' in o: return 'Android'
    if 'dos'     in o: return 'DOS'
    return 'Other'

df['os_clean'] = df['OS'].apply(norm_os)

# Extract dedicated GPU VRAM (0 = integrated)
def parse_gpu_vram(g):
    g = str(g)
    match = re.search(r'(\d+)\s*GB', g)
    if match:
        return int(match.group(1))
    return 0

df['gpu_vram_gb'] = df['GPU'].apply(parse_gpu_vram)

# Is discrete GPU?
def is_discrete(g):
    g = str(g).lower()
    return int(any(k in g for k in ['nvidia', 'radeon rx', 'geforce', 'quadro', 'rtx', 'gtx']))

df['has_discrete_gpu'] = df['GPU'].apply(is_discrete)

# Processor generation (extract leading number like "12th" → 12)
def proc_gen(p):
    m = re.search(r'(\d+)(st|nd|rd|th)', str(p))
    return int(m.group(1)) if m else 0

df['proc_gen'] = df['processor'].apply(proc_gen)

# Processor tier: i9/Ryzen9/M2 > i7/Ryzen7/M1 > i5/Ryzen5 > i3/Ryzen3 > Celeron/Atom/other
def proc_tier(p):
    p = str(p).lower()
    if any(k in p for k in ['i9', 'ryzen 9', 'ryzen9', 'm2', 'm3', 'core ultra 9']): return 5
    if any(k in p for k in ['i7', 'ryzen 7', 'ryzen7', 'm1', 'core ultra 7']):        return 4
    if any(k in p for k in ['i5', 'ryzen 5', 'ryzen5', 'core ultra 5']):              return 3
    if any(k in p for k in ['i3', 'ryzen 3', 'ryzen3']):                              return 2
    if any(k in p for k in ['celeron', 'pentium', 'atom', 'athlon']):                 return 1
    return 2

df['proc_tier'] = df['processor'].apply(proc_tier)

# Display size as float
df['display_size'] = pd.to_numeric(df['display_size'], errors='coerce').fillna(15.6)

# Pixel count
df['pixel_count'] = df['resolution_width'].astype(int) * df['resolution_height'].astype(int)

# Warranty as int
df['warranty'] = pd.to_numeric(df['warranty'], errors='coerce').fillna(1).astype(int)

# ── 3. Select features ────────────────────────────────────────────────────────
CAT_FEATURES = ['brand', 'ram_type_clean', 'rom_type', 'os_clean']
NUM_FEATURES = [
    'ram_gb', 'rom_gb', 'gpu_vram_gb', 'has_discrete_gpu',
    'proc_gen', 'proc_tier', 'display_size', 'pixel_count', 'warranty'
]

# rename ROM_type column for consistency
df = df.rename(columns={'ROM_type': 'rom_type'})

X = df[CAT_FEATURES + NUM_FEATURES]
y = df['price']

# ── 4. Build pipeline ─────────────────────────────────────────────────────────
cat_pipe = Pipeline([
    ('enc', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
])
num_pipe = Pipeline([
    ('scaler', StandardScaler())
])

preprocessor = ColumnTransformer([
    ('cat', cat_pipe, CAT_FEATURES),
    ('num', num_pipe, NUM_FEATURES),
])

model_pipe = Pipeline([
    ('prep', preprocessor),
    ('model', GradientBoostingRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        random_state=42
    ))
])

# ── 5. Train / evaluate ───────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
model_pipe.fit(X_train, y_train)

preds = model_pipe.predict(X_test)
print(f"MAE  : Rs.{mean_absolute_error(y_test, preds):,.0f}")
print(f"R2   : {r2_score(y_test, preds):.4f}")

# ── 6. Save artefacts ─────────────────────────────────────────────────────────
out_dir = os.path.dirname(__file__)
with open(os.path.join(out_dir, 'model.pkl'), 'wb') as f:
    pickle.dump(model_pipe, f)

# Save metadata so the backend knows valid categories
meta = {
    'brands':     sorted(df['brand'].unique().tolist()),
    'ram_types':  sorted(df['ram_type_clean'].unique().tolist()),
    'rom_types':  sorted(df['rom_type'].unique().tolist()),
    'os_list':    sorted(df['os_clean'].unique().tolist()),
    'cat_features': CAT_FEATURES,
    'num_features': NUM_FEATURES,
}
with open(os.path.join(out_dir, 'meta.pkl'), 'wb') as f:
    pickle.dump(meta, f)

print("Model and metadata saved to ml/")
