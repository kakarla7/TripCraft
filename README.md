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
| 4 | Fix Supabase client | `feat/supabase-client` | ✅ Done |
| 5 | Email/password auth | `feat/google-auth` | ✅ Done |
| 6 | Save search with custom name | `feat/save-compare-bucket` | ✅ Done |
| 7 | Add to compare button + bucket | `feat/save-compare-bucket` | ✅ Done |
| 8 | Amazon-style compare page | `feat/save-compare-bucket` | ✅ Done |
| 9 | My Trips / Profile page | `feat/profile-share` | 🟡 In progress |
| 10 | Share via link / iMessage / AirDrop | `feat/profile-share` | 🟡 In progress |
| 11 | Password reset + Google OAuth | end of Phase 1 | 🔜 Planned |

---

## 🏗️ Tech stack

| Layer | Tool | Notes |
|---|---|---|
| Frontend | Streamlit | Multi-page app |
| AI agents | Anthropic `claude-sonnet-4-6` | 4 parallel agents Phase 1 |
| Auth | Supabase Auth | Email/password · Google OAuth end of Phase 1 |
| Database | Supabase Postgres | |
| Hosting | Streamlit Cloud | Python 3.10 |
| Share | Web Share API | AirDrop · Nearby Share · iMessage |

---

## 📁 Project structure

```
tripcraft/
├── app.py
├── pages/
│   ├── 1_Search.py         # Input form
│   ├── 2_Results.py        # Destination cards + save + compare bucket
│   ├── 3_Compare.py        # Amazon-style compare table
│   ├── 4_My_Trips.py       # Profile + saved searches
│   └── 5_Login.py          # Login / signup
├── agents/
│   ├── destination_agent.py
│   ├── weather_agent.py
│   ├── budget_agent.py
│   └── comparator_agent.py
├── utils/
│   ├── supabase_client.py
│   ├── auth.py
│   ├── share.py
│   ├── cities.py
│   └── json_parser.py
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

---

## 🗄️ Database schema (Supabase)

```sql
create table saved_searches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,
  search_params jsonb not null,
  results jsonb not null,
  share_slug text unique not null,
  created_at timestamptz default now()
);

create table saved_trips (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  destination text not null,
  full_plan jsonb not null,
  share_slug text unique not null,
  created_at timestamptz default now()
);
```

---

## ⚙️ Local setup

```bash
git clone git@github.com:kakarla7/TripCraft.git
cd TripCraft
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Fill in secrets
streamlit run app.py
```

## 🔁 Daily workflow

```bash
source venv/bin/activate
git checkout main && git pull origin main
git checkout -b feat/your-feature
# work
git add . && git commit -m "feat: description"
git push -u origin feat/your-feature
# open PR on GitHub → merge → delete branch
```

---

## 🌐 Deployment

- Hosting: Streamlit Cloud
- Repo: `kakarla7/TripCraft` (public)
- Python: 3.10
- Live URL: `https://tripcraft.streamlit.app`

---

## 🔜 Phase 2 planned

- Airport selector
- Day-by-day itinerary agent
- Hotel recommendations
- Full budget breakdown
- Google Places autocomplete
- Amadeus API for real flight prices

## 🔜 Phase 3 planned

- US travel map
- Trip journal + photos
- Reviews per destination
- AI trip recap
- Share trip publicly