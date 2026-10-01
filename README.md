# Laptop Price Predictor

A full-stack web app that predicts laptop prices using a **Gradient Boosting Regression** model trained on 893 real laptop listings.

## Stack

| Layer    | Technology                         |
|----------|------------------------------------|
| ML       | Python · scikit-learn · pandas      |
| Backend  | Node.js · Express.js               |
| Frontend | React (Vite)                        |

---

## Project Structure

```
.
├── data.csv                  # Training dataset (893 laptops)
├── ml/
│   ├── train_model.py        # Train & save the regression model
│   ├── predict.py            # Called by Express for inference
│   ├── model.pkl             # Saved trained pipeline (generated)
│   └── meta.pkl              # Category metadata (generated)
├── backend/
│   ├── server.js             # Express API server
│   └── package.json
└── frontend/
    ├── src/
    │   ├── App.jsx           # Main React component
    │   └── index.css         # Styles
    └── package.json
```

---

## Setup & Run

### 1 · Install Python dependencies

```bash
pip install pandas scikit-learn numpy
```

### 2 · Train the model  *(only needed once)*

```bash
python ml/train_model.py
```

Expected output:
```
Loaded 893 rows
MAE  : Rs.10,098
R2   : 0.9363
Model and metadata saved to ml/
```

### 3 · Start the Express backend

```bash
cd backend
npm install
npm start        # runs on http://localhost:5000
```

### 4 · Start the React frontend

In a **separate terminal**:

```bash
cd frontend
npm install
npm run dev      # opens http://localhost:5173
```

Open **http://localhost:5173** in your browser.

---

## API Endpoints

### `POST /api/predict`

**Request body (JSON):**

| Field              | Type   | Example                          |
|--------------------|--------|----------------------------------|
| `brand`            | string | `"HP"`                           |
| `processor`        | string | `"12th Gen Intel Core i5 12450H"`|
| `ram`              | string | `"8GB"`                          |
| `ram_type`         | string | `"DDR4"`                         |
| `rom`              | string | `"512GB"`                        |
| `rom_type`         | string | `"SSD"`                          |
| `gpu`              | string | `"Intel Iris Xe"`                |
| `display_size`     | string | `"15.6"`                         |
| `resolution_width` | number | `1920`                           |
| `resolution_height`| number | `1080`                           |
| `os`               | string | `"Windows 11"`                   |
| `warranty`         | string | `"1"`                            |

**Response:**
```json
{ "price": 54358.82 }
```

### `GET /api/options`

Returns all valid dropdown values for the form.

---

## ML Details

- **Algorithm:** Gradient Boosting Regressor (500 estimators, depth 5)  
- **Features engineered from raw columns:**
  - RAM / ROM parsed to numeric GB  
  - GPU VRAM extracted (0 = integrated)  
  - Processor generation and tier (i3→2, i5→3, i7→4, i9→5)  
  - Display pixel count (width × height)  
  - OS and RAM type normalised  
- **Test R²:** 0.936 · **MAE:** ~₹10,098
