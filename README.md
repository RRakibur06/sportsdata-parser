# 🏟 1xBet Live Data Parser & Dashboard

A FastAPI-based application for fetching, parsing, and displaying live sports data from the 1xBet public API.  
Includes a web dashboard with filters, live updates, and export options.

---

## 📌 Features

- **Live Data Fetching** — Pulls real-time match data from the 1xBet `/LineFeed/Get1x2_VZip` endpoint.
- **Sport Filters** — Select specific sports (Football, Cricket, Tennis, etc.) via a dropdown.
- **FastAPI Backend** — Serves API endpoints for fetching and parsing data.
- **Dashboard UI** — HTML + JavaScript frontend with controls for filtering, refreshing, and exporting.
- **Data Export** — Save parsed match data to CSV or JSON.
- **UTF‑8 Safe** — Handles non‑ASCII characters in team/league names.
- **Developer‑Friendly** — Well‑structured code with clear separation of concerns.

---

## 🗂 Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI app entrypoint
│   ├── parser.py            # BettingDataParser class
│   ├── templates/
│   │   └── dashboard.html   # Dashboard UI
├── data/
│   └── sample_data.json     # Latest fetched API data
├── run.py                   # Project setup + server runner
├── requirements.txt         # Python dependencies
└── README.md
```

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/1xbet-fastapi-parser.git
   cd 1xbet-fastapi-parser
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running the Server

```bash
python run.py
```

- **Dashboard:** [http://localhost:8000](http://localhost:8000)  
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔌 API Endpoints

### `POST /api/fetch-live`
Fetches live data from the 1xBet API.

**Query Parameters:**
| Name    | Type | Default | Description |
|---------|------|---------|-------------|
| `count` | int  | 100     | Number of matches to fetch |
| `sports`| int  | 66      | Sport ID (e.g., 1 = Football, 66 = Cricket) |

**Example:**
```bash
curl -X POST "http://localhost:8000/api/fetch-live?sports=66&count=50"
```

**Response:**
```json
{
  "success": true,
  "matches_fetched": 50,
  "saved_to": "data/api_response_20250914_173000.json",
  "timestamp": "2025-09-14T17:30:00"
}
```

---

## 🖥 Dashboard Controls

- **Sport Filter** — Choose a sport from the dropdown to fetch only that sport's matches.
- **Apply Filters** — Sends the selected sport ID to the backend.
- **Fetch Live Data** — Refreshes the data from the API.
- **Export CSV / JSON** — Downloads the current dataset.

**Example Sport IDs:**
| ID  | Sport              |
|-----|--------------------|
| 1   | Football           |
| 66  | Cricket            |
| 3   | Tennis             |
| 4   | Basketball         |
| 6   | Ice Hockey         |
| 12  | Table Tennis       |
| 9   | Volleyball         |
| 7   | Esports            |
| 8   | Baseball           |
| 5   | American Football  |

---

## 🛠 Tech Stack

- **Backend:** FastAPI, httpx (async requests)
- **Frontend:** HTML, JavaScript, Fetch API
- **Data Parsing:** Custom `BettingDataParser`
- **Export:** Pandas (CSV export)

---

## 📄 Notes

- The 1xBet API is public but may change without notice.
- Frequent polling should respect the server's rate limits.
- All JSON files are saved in `data/` with UTF‑8 encoding.

---

## 📜 License

MIT License — feel free to use and modify for your own projects.
