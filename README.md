# ✈️ TripCraft

AI-powered US trip planner. Find your perfect destination in seconds.

## Stack
- **Frontend:** Streamlit
- **AI:** Anthropic Claude API (multi-agent, parallel)
- **Database + Auth:** Supabase (Postgres + Google OAuth)
- **Hosting:** Streamlit Cloud

## Project structure
```
tripcraft/
├── app.py                  # Entry point
├── pages/
│   ├── 1_Search.py         # Input form
│   ├── 2_Results.py        # Destination cards + share
│   ├── 3_Compare.py        # Side-by-side comparison
│   └── 4_My_Trips.py       # Saved searches + trips
├── agents/
│   ├── destination_agent.py
│   ├── weather_agent.py
│   ├── budget_agent.py
│   └── comparator_agent.py
├── utils/
│   ├── supabase_client.py
│   ├── auth.py
│   └── share.py
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

## Setup

### 1. Clone and install
```bash
git clone git@github.com:kakarla7/tripcraft.git
cd tripcraft
pip install -r requirements.txt
```

### 2. Supabase setup
1. Create a project at [supabase.com](https://supabase.com)
2. Run this SQL in the Supabase SQL editor:

```sql
-- Users (auto-managed by Supabase Auth)

-- Saved searches
create table saved_searches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  search_params jsonb not null,
  results jsonb not null,
  share_slug text unique not null,
  created_at timestamptz default now()
);

-- Saved trips (Phase 2)
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

-- Owners can read/write their own rows
create policy "owner access" on saved_searches
  for all using (auth.uid() = user_id);

-- Anyone can read via share slug (public share links)
create policy "public read by slug" on saved_searches
  for select using (true);

create policy "owner access" on saved_trips
  for all using (auth.uid() = user_id);

create policy "public read by slug" on saved_trips
  for select using (true);
```

3. Enable Google OAuth in Supabase: Auth → Providers → Google

### 3. Secrets
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in:
```toml
[anthropic]
api_key = "sk-ant-..."

[supabase]
url = "https://your-project.supabase.co"
anon_key = "your-anon-key"
service_role_key = "your-service-role-key"

app_url = "http://localhost:8501"  # Change to your Streamlit Cloud URL after deploy
```

### 4. Run locally
```bash
streamlit run app.py
```

### 5. Deploy to Streamlit Cloud
1. Push to `github.com/kakarla7/tripcraft` (private)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set main file as `app.py`
4. Add secrets in Streamlit Cloud settings
5. Update `app_url` in secrets to your `.streamlit.app` URL

## Phases
- **Phase 1** ✅ Discovery — multi-agent search, destination cards, save + share
- **Phase 2** 🔜 Full plan — itinerary, hotels, budget breakdown, airport selector
- **Phase 3** 🔜 Personal space — travel map, journal, reviews, photos
