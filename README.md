# ✈️ TripCraft

AI-powered US trip planner. Find your perfect destination in seconds.

---

## 🗺️ Product phases

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Discovery — multi-agent destination search | 🟡 In progress |
| Phase 2 | Full plan — itinerary, hotels, budget, airport | 🔜 Planned |
| Phase 3 | Personal space — journal, map, reviews, photos | 🔜 Planned |

---

## ✅ Build progress

### Phase 1 — Discovery

| Step | Feature | Branch | Status |
|---|---|---|---|
| 1 | Project setup + multi-agent search | `main` | ✅ Done |
| 2 | Destination cards + results page | `main` | ✅ Done |
| 3 | Deploy to Streamlit Cloud | `main` | ✅ Done |
| 4 | Fix Supabase client (real import) | `feat/supabase-client` | ✅ Done |
| 5 | Real Google OAuth login | `feat/google-auth` | 🟡 In progress |
| 6 | Save search with custom name | `feat/save-search` | 🔜 Planned |
| 7 | Add to compare button on cards | `feat/compare-bucket` | 🔜 Planned |
| 8 | Amazon-style compare page | `feat/compare-page` | 🔜 Planned |
| 9 | My Trips page polish | `feat/my-trips-polish` | 🔜 Planned |

---

## 🏗️ Tech stack

| Layer | Tool | Notes |
|---|---|---|
| Frontend | Streamlit | Multi-page app |
| AI agents | Anthropic `claude-sonnet-4-6` | 4 parallel agents |
| Auth | Supabase Auth + Google OAuth | |
| Database | Supabase Postgres | |
| Hosting | Streamlit Cloud | Python 3.10 |
| Share | Web Share API (browser native) | AirDrop + Nearby Share |

---

## 📁 Project structure

```
tripcraft/
├── app.py                      # Entry point
├── pages/
│   ├── 1_Search.py             # Input form — city, month, days, interests
│   ├── 2_Results.py            # Destination cards + save + share + compare bucket
│   ├── 3_Compare.py            # Amazon-style compare table
│   └── 4_My_Trips.py           # Saved searches + trips
├── agents/
│   ├── destination_agent.py    # Finds 5 best US destinations
│   ├── weather_agent.py        # Weather per destination per month
│   ├── budget_agent.py         # Flight + total cost estimates
│   └── comparator_agent.py     # Merges + ranks into final cards
├── utils/
│   ├── supabase_client.py      # DB read/write helpers
│   ├── auth.py                 # Google OAuth via Supabase
│   ├── share.py                # Share link + Web Share API
│   ├── cities.py               # US city list for autocomplete
│   └── json_parser.py          # Robust Claude JSON parser
└── .streamlit/
    ├── config.toml             # Theme + server config
    └── secrets.toml.example    # Template — copy to secrets.toml
```

---

## 🗄️ Database schema (Supabase)

```sql
-- Saved searches
create table saved_searches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,                    -- user-defined e.g. "Family October trip"
  search_params jsonb not null,          -- origin, month, days, interests etc.
  results jsonb not null,                -- full cards array from comparator agent
  share_slug text unique not null,       -- short ID for share links
  created_at timestamptz default now()
);

-- Saved trip plans (Phase 2)
create table saved_trips (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  destination text not null,
  full_plan jsonb not null,
  share_slug text unique not null,
  created_at timestamptz default now()
);

-- Row Level Security
alter table saved_searches enable row level security;
alter table saved_trips enable row level security;

create policy "owner access" on saved_searches
  for all using (auth.uid() = user_id);

create policy "public read by slug" on saved_searches
  for select using (true);

create policy "owner access" on saved_trips
  for all using (auth.uid() = user_id);

create policy "public read by slug" on saved_trips
  for select using (true);
```

---

## ⚙️ Local setup

### 1. Clone and create venv
```bash
git clone git@github.com:kakarla7/tripcraft.git
cd tripcraft
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Secrets
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Fill in your Anthropic API key and Supabase credentials.

### 3. Run locally
```bash
streamlit run app.py
```

### 4. Daily workflow
```bash
# Start of session
source venv/bin/activate
git checkout main && git pull origin main

# New feature
git checkout -b feat/your-feature-name

# Push + PR
git add . && git commit -m "feat: description"
git push -u origin feat/your-feature-name
# Open PR on github.com/kakarla7/tripcraft
```

---

## 🌐 Deployment

- **Hosting:** Streamlit Cloud
- **Repo:** `kakarla7/tripcraft` (private)
- **Python:** 3.10
- **Secrets:** set in Streamlit Cloud dashboard (never committed to repo)
- **Live URL:** `https://tripcraft.streamlit.app`

---

## 🔜 Phase 2 planned features

- Airport selector (triggered when user picks a destination)
- Day-by-day itinerary agent
- Hotel recommendations (budget / mid / luxury)
- Full budget breakdown
- Google Places autocomplete for city search
- Amadeus API for real flight prices

## 🔜 Phase 3 planned features

- US travel map (mark visited states)
- Trip journal with photos
- Reviews per destination
- AI trip recap
- Share trip publicly