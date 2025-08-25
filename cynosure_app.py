
import json, re, datetime
import streamlit as st

st.set_page_config(page_title="Cynosure 2025 – Search", layout="wide")

@st.cache_resource
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

db = load_data()
events = db["events"]

st.title("🔎 Cynosure 2025 – Universal Search")
st.caption("Search by person (teacher), event, domain, date, age group, venue… anything!")

q = st.text_input("Type to search (e.g., 'Ms Vidya Nair', 'Basketball', '27 Sep', '9th to 12th')")

cols = st.columns(4)
date_filter = cols[0].multiselect("Date", ["2025-09-26","2025-09-27","Both"])
domain_filter = cols[1].multiselect("Domain", ["Literary","Fine Arts","Commerce","Performing Arts","Cynoshow","Sports"])
restricted_filter = cols[2].multiselect("Restricted?", ["Yes","No"])
age_pin = cols[3].text_input("Age/Category contains", placeholder="e.g., 6th-8th or 9th to 12th")

def norm(s):
    return (s or "").lower()

def matches(e, q):
    if not q:
        return True
    hay = " ".join([
        e.get("event_name",""),
        e.get("domain",""),
        e.get("date",""),
        e.get("time","") or "",
        e.get("venue","") or "",
        e.get("age_category","") or "",
        e.get("teacher_in_charge","") or "",
        str(e.get("capacity_schools","") or ""),
        " ".join(e.get("categories") or []),
        json.dumps(e.get("category_participants") or {}, ensure_ascii=False),
        e.get("brochure_extract","") or "",
    ]).lower()
    return all(term in hay for term in q.lower().split())

def apply_filters(rows):
    out = []
    for e in rows:
        if date_filter and e["date"] not in date_filter:
            continue
        if domain_filter and e["domain"] not in domain_filter:
            continue
        if restricted_filter:
            flag = "Yes" if e.get("restricted") else "No"
            if flag not in restricted_filter:
                continue
        if age_pin and (age_pin.lower() not in norm(e.get("age_category"))):
            continue
        out.append(e)
    return out

rows = [e for e in events if matches(e, q)]
rows = apply_filters(rows)

st.write(f"**{len(rows)}** result(s).")

def pill(label, value):
    if not value:
        return ""
    return f"<span style='padding:4px 8px; border-radius:999px; border:1px solid #ddd; font-size:0.8rem;'>{label}: {value}</span>"

for e in rows:
    with st.container(border=True):
        header_cols = st.columns([0.5,0.5,0.3,0.3,0.4])
        header_cols[0].markdown(f"### {e['event_name']}")
        header_cols[1].markdown(pill("Domain", e["domain"]), unsafe_allow_html=True)
        header_cols[2].markdown(pill("Date", e["date"]), unsafe_allow_html=True)
        header_cols[3].markdown(pill("Time", e.get("time")), unsafe_allow_html=True)
        header_cols[4].markdown(pill("Venue", e.get("venue")), unsafe_allow_html=True)

        st.markdown(
            " | ".join([
                pill("Age", e.get("age_category")),
                pill("Teacher-in-charge", e.get("teacher_in_charge")),
                pill("Restricted", "Yes" if e.get("restricted") else "No"),
                pill("Capacity (schools)", str(e.get("capacity_schools") or "")),
                pill("Participants/school", str(e.get("participants_per_school") or "")),
            ]),
            unsafe_allow_html=True
        )

        if e.get("categories"):
            st.write("**Categories:** " + ", ".join(e["categories"]))
        if e.get("category_participants"):
            st.write("**Participants per category:**")
            st.json(e["category_participants"])

        if e.get("brochure_extract"):
            with st.expander("Brochure extract / details"):
                st.write(e["brochure_extract"])

st.divider()
st.subheader("Quick Day-wise Timelines")
c1, c2 = st.columns(2)

def timeline(day):
    timeline_rows = [e for e in events if e["date"] in (day, "Both")]
    timeline_rows.sort(key=lambda x: (x["time"] or "zzz", x["event_name"]))
    for e in timeline_rows:
        st.markdown(f"- **{e['time'] or 'Full-day'}** — {e['event_name']}  _(Venue: {e.get('venue') or 'TBA'})_")

with c1:
    st.markdown("**Day 1 – Friday, 26 Sep 2025**")
    timeline("2025-09-26")
with c2:
    st.markdown("**Day 2 – Saturday, 27 Sep 2025**")
    timeline("2025-09-27")

st.divider()
st.caption("Tip: To find a person, type their name (e.g., 'Vidya Nair' or 'Mrs. Vidya'). To see everything on a date, filter by Date.")
