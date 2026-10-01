const express = require('express');
const cors    = require('cors');
const { spawn } = require('child_process');
const path    = require('path');

const app  = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// ── POST /api/predict ─────────────────────────────────────────────────────────
app.post('/api/predict', (req, res) => {
  const input = req.body;

  // Basic validation
  const required = ['brand','ram','ram_type','rom','rom_type','os','display_size','resolution_width','resolution_height'];
  for (const field of required) {
    if (input[field] === undefined || input[field] === '') {
      return res.status(400).json({ error: `Missing field: ${field}` });
    }
  }

  const mlScript = path.resolve(__dirname, '..', 'ml', 'predict.py');

  const py = spawn('python', [mlScript], { stdio: ['pipe', 'pipe', 'pipe'] });

  let stdout = '';
  let stderr = '';

  py.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
  py.stderr.on('data', (chunk) => { stderr += chunk.toString(); });

  py.on('close', (code) => {
    if (code !== 0) {
      console.error('Python error:', stderr);
      return res.status(500).json({ error: 'Prediction failed', detail: stderr });
    }
    try {
      const result = JSON.parse(stdout.trim());
      res.json(result);
    } catch (e) {
      res.status(500).json({ error: 'Invalid response from model', detail: stdout });
    }
  });

  py.stdin.write(JSON.stringify(input));
  py.stdin.end();
});

// ── GET /api/options ──────────────────────────────────────────────────────────
// Return the valid dropdown options for the frontend
app.get('/api/options', (_req, res) => {
  res.json({
    brands: [
      'AXL','Acer','Apple','Asus','Avita','Chuwi','Dell','Fujitsu','Gigabyte',
      'HP','Honor','Huawei','Infinix','LG','Lenovo','MSI','Microsoft','Ninkear',
      'Primebook','Razer','Realme','Samsung','Tecno','Ultimus','Vaio','Walker',
      'Wings','Xiaomi','Zebronics','iBall'
    ],
    ram_options: ['2GB','4GB','8GB','12GB','16GB','32GB','64GB'],
    ram_types: ['DDR3','DDR4','DDR5','LPDDR4','LPDDR4X','LPDDR5','LPDDR5X','Unified'],
    rom_options: ['32GB','64GB','128GB','256GB','512GB','1TB','2TB'],
    rom_types: ['SSD','Hard-Disk'],
    os_options: [
      'Windows 11','Windows 10','Windows','Mac OS','Ubuntu','Chrome OS','Android','DOS'
    ],
    display_sizes: ['11.6','13.3','13.4','13.5','13.6','14','14.1','14.2','15','15.3','15.6','16','16.1','16.2','17','17.3','18'],
    resolutions: [
      { label: '1366×768 (HD)',      width: 1366, height: 768  },
      { label: '1920×1080 (Full HD)',width: 1920, height: 1080 },
      { label: '1920×1200 (WUXGA)',  width: 1920, height: 1200 },
      { label: '2240×1400 (2.5K)',   width: 2240, height: 1400 },
      { label: '2560×1440 (2K/QHD)', width: 2560, height: 1440 },
      { label: '2560×1600 (WQXGA)',  width: 2560, height: 1600 },
      { label: '2560×1664',          width: 2560, height: 1664 },
      { label: '3200×2000 (3.2K)',   width: 3200, height: 2000 },
    ],
    warranty_options: ['0','1','2','3'],
  });
});

app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
