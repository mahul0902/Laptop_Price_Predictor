import sys
import json
import pickle
import os
import re

# ── helpers (same logic as train_model.py) ───────────────────────────────────

def norm_ram_type(t):
    t = str(t).strip().upper().replace('-', '')
    if 'LPDDR5' in t:   return 'LPDDR5'
    if 'LPDDR4' in t:   return 'LPDDR4'
    if 'DDR5'   in t:   return 'DDR5'
    if 'DDR4'   in t:   return 'DDR4'
    if 'DDR3'   in t:   return 'DDR3'
    if 'DDR'    in t:   return 'DDR'
    return 'Other'

def norm_os(o):
    o = str(o).strip().lower()
    if 'mac'        in o: return 'Mac OS'
    if 'windows 11' in o: return 'Windows 11'
    if 'windows 10' in o: return 'Windows 10'
    if 'windows'    in o: return 'Windows'
    if 'ubuntu'     in o: return 'Ubuntu'
    if 'chrome'     in o: return 'Chrome OS'
    if 'android'    in o: return 'Android'
    if 'dos'        in o: return 'DOS'
    return 'Other'

def parse_rom(val):
    val = str(val).strip()
    if 'TB' in val:
        return int(re.search(r'(\d+)', val).group(1)) * 1024
    return int(re.search(r'(\d+)', val).group(1))

def proc_gen(p):
    m = re.search(r'(\d+)(st|nd|rd|th)', str(p))
    return int(m.group(1)) if m else 0

def proc_tier(p):
    p = str(p).lower()
    if any(k in p for k in ['i9', 'ryzen 9', 'ryzen9', 'm2', 'm3', 'core ultra 9']): return 5
    if any(k in p for k in ['i7', 'ryzen 7', 'ryzen7', 'm1', 'core ultra 7']):        return 4
    if any(k in p for k in ['i5', 'ryzen 5', 'ryzen5', 'core ultra 5']):              return 3
    if any(k in p for k in ['i3', 'ryzen 3', 'ryzen3']):                              return 2
    if any(k in p for k in ['celeron', 'pentium', 'atom', 'athlon']):                 return 1
    return 2

def gpu_vram(g):
    m = re.search(r'(\d+)\s*GB', str(g))
    return int(m.group(1)) if m else 0

def is_discrete(g):
    g = str(g).lower()
    return int(any(k in g for k in ['nvidia', 'radeon rx', 'geforce', 'quadro', 'rtx', 'gtx']))

# ── load artefacts ────────────────────────────────────────────────────────────
base = os.path.dirname(__file__)
with open(os.path.join(base, 'model.pkl'), 'rb') as f:
    model = pickle.load(f)

# ── read input from stdin (JSON) ──────────────────────────────────────────────
data = json.loads(sys.stdin.read())

import pandas as pd

row = {
    'brand':          data['brand'],
    'ram_type_clean': norm_ram_type(data['ram_type']),
    'rom_type':       data['rom_type'],
    'os_clean':       norm_os(data['os']),
    'ram_gb':         int(re.search(r'(\d+)', data['ram']).group(1)),
    'rom_gb':         parse_rom(data['rom']),
    'gpu_vram_gb':    gpu_vram(data.get('gpu', '')),
    'has_discrete_gpu': is_discrete(data.get('gpu', '')),
    'proc_gen':       proc_gen(data.get('processor', '')),
    'proc_tier':      proc_tier(data.get('processor', '')),
    'display_size':   float(data['display_size']),
    'pixel_count':    int(data['resolution_width']) * int(data['resolution_height']),
    'warranty':       int(data.get('warranty', 1)),
}

X = pd.DataFrame([row])
price = model.predict(X)[0]
print(json.dumps({'price': round(float(price), 2)}))
