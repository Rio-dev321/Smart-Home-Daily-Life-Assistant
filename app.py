import streamlit as st
import pandas as pd
from datetime import date, datetime, time, timedelta
from io import BytesIO
import calendar
import re

st.set_page_config(
    page_title="Smart Home & Daily Life Assistant",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Styling --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(135deg,#f4f8ff 0%,#eef4fc 55%,#f8fbff 100%); color:#183153; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#102b52,#174578); }
[data-testid="stSidebar"] * { color:white !important; }
.hero {
 background: linear-gradient(115deg,#102b52 0%,#1763a6 72%,#55a6e8 100%);
 color:white; padding:28px 30px; border-radius:22px; margin-bottom:20px;
 box-shadow:0 12px 30px rgba(23,76,130,.16); animation: fadeIn .7s ease-out;
}
.hero h1 { color:white; font-size:30px; margin:0; font-weight:800; }
.hero p { color:#e4f1ff; margin:7px 0 0; }
@keyframes fadeIn { from {opacity:0; transform:translateY(10px)} to {opacity:1; transform:translateY(0)} }
@keyframes floatIn { from {opacity:0; transform:translateY(8px)} to {opacity:1; transform:translateY(0)} }
.panel {
 background:rgba(255,255,255,.94); border:1px solid #e1eaf5; border-radius:17px;
 padding:17px 19px; box-shadow:0 5px 18px rgba(20,58,100,.055);
 animation:floatIn .45s ease-out;
}
.metric-label { color:#6b7f99; font-size:13px; }
.metric-value { color:#12365f; font-size:26px; font-weight:800; margin-top:4px; }
.section { color:#12365f; font-size:21px; font-weight:800; margin:15px 0 10px; }
.pill { display:inline-block; background:#eaf3ff; color:#175b9a; border:1px solid #d3e6fb; padding:6px 11px; border-radius:20px; margin:3px; font-size:12px; font-weight:700; }
div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {
 border-radius:10px; border:0; background:#1763a6; color:white; font-weight:700;
 transition:all .18s ease;
}
div[data-testid="stButton"] button:hover, div[data-testid="stFormSubmitButton"] button:hover {
 background:#104879; transform:translateY(-1px); box-shadow:0 5px 12px #1763a633;
}
div[data-testid="stDownloadButton"] button { background:#e5f1ff; color:#15568f; border:1px solid #c9e0f8; border-radius:10px; font-weight:700; }
h2,h3 { color:#12365f; }
[data-testid="stMetric"] { background:white; padding:12px 14px; border:1px solid #e1eaf5; border-radius:14px; }
.stProgress > div > div > div > div { background:#2684d8; }
</style>
""", unsafe_allow_html=True)

# -------------------- State helpers --------------------
def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

init_state("shopping", [])
init_state("expenses", [])
init_state("tasks", [])
init_state("reminders", [])
init_state("notes", [])
init_state("meals", [])
init_state("goals", [])
init_state("chat", [])

def money(value):
    return f"Rs. {value:,.0f}"

def today_str():
    return date.today().isoformat()

def add_item(key, item):
    st.session_state[key].append(item)

# -------------------- Sidebar --------------------
st.sidebar.markdown("# 🏡 LifeMate AI")
st.sidebar.caption("Smart Home & Daily Life Assistant")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🛒 Shopping List", "💸 Expense Tracker", "🗓️ Daily Planner",
     "⏰ Reminders", "📝 Notes", "🥗 Meal Planner", "🎯 Daily Goals", "🤖 AI Assistant"],
    label_visibility="visible"
)
st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ Aaj ka focus")
st.sidebar.info("Chhotay steps, behtar routine aur smart planning!")
st.sidebar.caption("Data is waqt aapke current app session mein save rehta hai.")

# -------------------- Header --------------------
st.markdown("""
<div class="hero">
 <h1>🏡 Smart Home & Daily Life Assistant</h1>
 <p>Plan your day · Manage your home · Track your spending · Stay on top of goals</p>
</div>
""", unsafe_allow_html=True)

# -------------------- Home --------------------
if page == "🏠 Home":
    st.markdown('<div class="section">✨ Aapka Daily Overview</div>', unsafe_allow_html=True)
    today_tasks = [x for x in st.session_state.tasks if x["date"] == today_str()]
    done_tasks = [x for x in today_tasks if x["done"]]
    today_expenses = sum(x["amount"] for x in st.session_state.expenses if x["date"] == today_str())
    pending_reminders = [x for x in st.session_state.reminders if not x["done"]]
    active_goals = [x for x in st.session_state.goals if not x["done"]]
    cols = st.columns(4)
    metrics = [
        ("Today's Tasks", f"{len(done_tasks)}/{len(today_tasks)}", "🗓️"),
        ("Today's Spending", money(today_expenses), "💸"),
        ("Shopping Items", str(sum(not x["done"] for x in st.session_state.shopping)), "🛒"),
        ("Pending Reminders", str(len(pending_reminders)), "⏰")
    ]
    for col, (label, val, icon) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="panel"><div class="metric-label">{icon} {label}</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="section">📌 Aaj ke Tasks</div>', unsafe_allow_html=True)
        if today_tasks:
            for i, task in enumerate(today_tasks):
                status = "✅" if task["done"] else "⬜"
                st.write(f"{status} **{task['title']}** · {task['time']}")
        else:
            st.markdown('<div class="panel">Aaj ke liye abhi koi task add nahi hua. Daily Planner mein apna plan banayein.</div>', unsafe_allow_html=True)
        st.markdown('<div class="section">🎯 Goal Progress</div>', unsafe_allow_html=True)
        if st.session_state.goals:
            completed = sum(g["done"] for g in st.session_state.goals)
            progress = completed / len(st.session_state.goals)
            st.progress(progress, text=f"{completed} of {len(st.session_state.goals)} goals complete")
        else:
            st.info("Daily Goals section mein apne goals add karein.")
    with right:
        st.markdown('<div class="section">⏰ Agli Reminders</div>', unsafe_allow_html=True)
        if pending_reminders:
            for reminder in sorted(pending_reminders, key=lambda x: (x["date"], x["time"]))[:5]:
                st.markdown(f'<div class="panel" style="margin-bottom:8px;"><b>{reminder["title"]}</b><br><span style="color:#6b7f99;">{reminder["date"]} · {reminder["time"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="panel">Koi pending reminder nahi. Aapka schedule clear hai!</div>', unsafe_allow_html=True)
        st.markdown('<div class="section">💡 Smart Tip</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel">Roz subah apne 3 sab se zaroori kaam likhein. Pehle unhein complete karein, phir baqi tasks par jayein.</div>', unsafe_allow_html=True)

# -------------------- Shopping --------------------
elif page == "🛒 Shopping List":
    st.markdown('<div class="section">🛒 Smart Shopping List</div>', unsafe_allow_html=True)
    with st.form("shopping_form", clear_on_submit=True):
        c1,c2,c3 = st.columns([2,1,1])
        item = c1.text_input("Item ka naam", placeholder="Milk, Bread, Notebook...")
        qty = c2.text_input("Quantity", "1")
        category = c3.selectbox("Category", ["Grocery","Household","School","Personal","Other"])
        submitted = st.form_submit_button("＋ Add to List")
        if submitted:
            if item.strip():
                add_item("shopping", {"item":item.strip(),"qty":qty.strip(),"category":category,"done":False})
                st.success("Item shopping list mein add ho gaya!")
            else: st.warning("Pehle item ka naam likhein.")
    if st.session_state.shopping:
        for i, item_data in enumerate(st.session_state.shopping):
            c1,c2,c3 = st.columns([4,1,1])
            checked = c1.checkbox(f"{item_data['item']} · {item_data['qty']} · {item_data['category']}", value=item_data["done"], key=f"shop_{i}")
            st.session_state.shopping[i]["done"] = checked
            if c2.button("🗑️", key=f"delshop_{i}"):
                st.session_state.shopping.pop(i); st.rerun()
        st.caption(f"{sum(x['done'] for x in st.session_state.shopping)} / {len(st.session_state.shopping)} items complete")
        if st.button("Clear completed items"):
            st.session_state.shopping = [x for x in st.session_state.shopping if not x["done"]]; st.rerun()
    else: st.info("Aapki shopping list abhi khaali hai.")

# -------------------- Expenses --------------------
elif page == "💸 Expense Tracker":
    st.markdown('<div class="section">💸 Expense Tracker</div>', unsafe_allow_html=True)
    with st.form("expense_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        title = c1.text_input("Expense detail", placeholder="Groceries, transport...")
        amount = c2.number_input("Amount (Rs.)", min_value=0.0, step=50.0)
        exp_date = c3.date_input("Date", value=date.today())
        category = st.selectbox("Category", ["Food","Transport","Shopping","Bills","Education","Health","Other"])
        submitted = st.form_submit_button("＋ Add Expense")
        if submitted:
            if title.strip() and amount > 0:
                add_item("expenses", {"title":title.strip(),"amount":float(amount),"date":exp_date.isoformat(),"category":category})
                st.success("Expense save ho gaya!")
            else: st.warning("Detail aur amount enter karein.")
    if st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses)
        total = df["amount"].sum()
        st.metric("Total Recorded Spending", money(total))
        st.dataframe(df.rename(columns={"title":"Detail","amount":"Amount (Rs.)","date":"Date","category":"Category"}), use_container_width=True, hide_index=True)
        a,b = st.columns(2)
        with a:
            fig = px.pie(df, names="category", values="amount", hole=.55, title="Category-wise Spending")
            fig.update_layout(paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        with b:
            daily = df.groupby("date", as_index=False)["amount"].sum()
            fig = px.bar(daily, x="date", y="amount", title="Daily Spending", labels={"date":"Date","amount":"Rs."})
            fig.update_layout(paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Expenses CSV", csv, "expenses.csv", "text/csv")
        if st.button("Delete all expenses"):
            st.session_state.expenses = []; st.rerun()
    else: st.info("Expense add karne ke baad report yahan nazar aayegi.")

# -------------------- Planner --------------------
elif page == "🗓️ Daily Planner":
    st.markdown('<div class="section">🗓️ Daily Planner</div>', unsafe_allow_html=True)
    with st.form("task_form", clear_on_submit=True):
        c1,c2,c3 = st.columns([2,1,1])
        title = c1.text_input("Task", placeholder="Homework, exercise, room cleaning...")
        task_date = c2.date_input("Date", value=date.today())
        task_time = c3.time_input("Time", value=time(9,0))
        priority = st.selectbox("Priority", ["High","Medium","Low"])
        submitted = st.form_submit_button("＋ Add Task")
        if submitted:
            if title.strip():
                add_item("tasks", {"title":title.strip(),"date":task_date.isoformat(),"time":task_time.strftime("%H:%M"),"priority":priority,"done":False})
                st.success("Task planner mein add ho gaya!")
            else: st.warning("Task ka naam likhein.")
    chosen = st.date_input("Tasks ki date dekhein", value=date.today(), key="planner_filter").isoformat()
    selected_tasks = [(i,x) for i,x in enumerate(st.session_state.tasks) if x["date"] == chosen]
    if selected_tasks:
        for i, task in selected_tasks:
            c1,c2,c3 = st.columns([4,1,1])
            checked = c1.checkbox(f"{task['time']} · {task['title']} · {task['priority']} priority", value=task["done"], key=f"task_{i}")
            st.session_state.tasks[i]["done"] = checked
            if c2.button("🗑️", key=f"deltask_{i}"):
                st.session_state.tasks.pop(i); st.rerun()
        completed = sum(st.session_state.tasks[i]["done"] for i,_ in selected_tasks)
        st.progress(completed/len(selected_tasks), text=f"{completed}/{len(selected_tasks)} tasks complete")
    else: st.info("Is date ke liye koi task nahi mila.")

# -------------------- Reminders --------------------
elif page == "⏰ Reminders":
    st.markdown('<div class="section">⏰ Reminders</div>', unsafe_allow_html=True)
    with st.form("reminder_form", clear_on_submit=True):
        c1,c2,c3 = st.columns([2,1,1])
        title = c1.text_input("Reminder", placeholder="Assignment submit karna...")
        rem_date = c2.date_input("Date", value=date.today())
        rem_time = c3.time_input("Time", value=time(17,0))
        submitted = st.form_submit_button("＋ Set Reminder")
        if submitted:
            if title.strip():
                add_item("reminders", {"title":title.strip(),"date":rem_date.isoformat(),"time":rem_time.strftime("%H:%M"),"done":False})
                st.success("Reminder add ho gaya!")
            else: st.warning("Reminder ka title likhein.")
    if st.session_state.reminders:
        for i, rem in enumerate(st.session_state.reminders):
            c1,c2,c3 = st.columns([4,1,1])
            checked = c1.checkbox(f"⏰ {rem['title']} · {rem['date']} · {rem['time']}", value=rem["done"], key=f"rem_{i}")
            st.session_state.reminders[i]["done"] = checked
            if c2.button("🗑️", key=f"delrem_{i}"):
                st.session_state.reminders.pop(i); st.rerun()
        st.caption("Note: App ke andar reminders list aur status show hota hai. Browser band hone par push notification nahi bheji jati.")
    else: st.info("Abhi koi reminder set nahi hai.")

# -------------------- Notes --------------------
elif page == "📝 Notes":
    st.markdown('<div class="section">📝 Quick Notes</div>', unsafe_allow_html=True)
    with st.form("note_form", clear_on_submit=True):
        title = st.text_input("Note title", placeholder="Important idea...")
        body = st.text_area("Note likhein", height=130)
        submitted = st.form_submit_button("＋ Save Note")
        if submitted:
            if title.strip() or body.strip():
                add_item("notes", {"title":title.strip() or "Untitled Note","body":body.strip(),"created":datetime.now().strftime("%d %b %Y, %I:%M %p")})
                st.success("Note save ho gaya!")
            else: st.warning("Kuch note likhein.")
    for i, note in enumerate(reversed(st.session_state.notes)):
        original_i = len(st.session_state.notes)-1-i
        with st.expander(f"📌 {note['title']} · {note['created']}"):
            st.write(note["body"])
            if st.button("Delete note", key=f"delnote_{original_i}"):
                st.session_state.notes.pop(original_i); st.rerun()
    if st.session_state.notes:
        notes_text = "\n\n".join(f"{n['title']}\n{n['body']}" for n in st.session_state.notes)
        st.download_button("⬇️ Download Notes", notes_text, "my_notes.txt")

# -------------------- Meal Planner --------------------
elif page == "🥗 Meal Planner":
    st.markdown('<div class="section">🥗 Weekly Meal Planner</div>', unsafe_allow_html=True)
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    with st.form("meal_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        day = c1.selectbox("Day", days)
        meal_type = c2.selectbox("Meal", ["Breakfast","Lunch","Dinner","Snack"])
        meal = c3.text_input("Meal / Food", placeholder="Daal chawal, fruit...")
        submitted = st.form_submit_button("＋ Add Meal")
        if submitted:
            if meal.strip():
                add_item("meals", {"day":day,"type":meal_type,"meal":meal.strip()})
                st.success("Meal plan update ho gaya!")
            else: st.warning("Meal ka naam likhein.")
    if st.session_state.meals:
        meal_df = pd.DataFrame(st.session_state.meals)
        order = pd.Categorical(meal_df["day"], categories=days, ordered=True)
        meal_df = meal_df.assign(_day=order).sort_values(["_day","type"]).drop(columns="_day")
        st.dataframe(meal_df.rename(columns={"day":"Day","type":"Meal","meal":"Food"}), use_container_width=True, hide_index=True)
        for i, m in enumerate(st.session_state.meals):
            if st.button(f"Remove {m['day']} {m['type']} - {m['meal']}", key=f"delmeal_{i}"):
                st.session_state.meals.pop(i); st.rerun()
    else: st.info("Apna weekly meal plan yahan banayein.")

# -------------------- Goals --------------------
elif page == "🎯 Daily Goals":
    st.markdown('<div class="section">🎯 Daily Goals</div>', unsafe_allow_html=True)
    with st.form("goal_form", clear_on_submit=True):
        goal = st.text_input("Aaj ka goal", placeholder="30 minutes reading...")
        submitted = st.form_submit_button("＋ Add Goal")
        if submitted:
            if goal.strip():
                add_item("goals", {"goal":goal.strip(),"done":False})
                st.success("Goal add ho gaya!")
            else: st.warning("Goal enter karein.")
    if st.session_state.goals:
        for i, g in enumerate(st.session_state.goals):
            c1,c2 = st.columns([5,1])
            checked = c1.checkbox(g["goal"], value=g["done"], key=f"goal_{i}")
            st.session_state.goals[i]["done"] = checked
            if c2.button("🗑️", key=f"delgoal_{i}"):
                st.session_state.goals.pop(i); st.rerun()
        done = sum(g["done"] for g in st.session_state.goals)
        st.progress(done/len(st.session_state.goals), text=f"{done} / {len(st.session_state.goals)} goals complete")
        st.balloons() if done == len(st.session_state.goals) else None
    else: st.info("Chhotay aur achievable goals add karein.")

# -------------------- AI Assistant --------------------
elif page == "🤖 AI Assistant":
    st.markdown('<div class="section">🤖 LifeMate Smart Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">Yeh built-in smart helper aapki lists, planner aur daily routine ke hawale se basic suggestions deta hai. Is version ko external AI API ki zaroorat nahi.</div>', unsafe_allow_html=True)
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Apna sawal likhein... misal: Mera din kaise plan karun?")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        q = prompt.lower()
        if any(word in q for word in ["budget","expense","kharcha","spending"]):
            total = sum(x["amount"] for x in st.session_state.expenses)
            answer = f"Aapka recorded total kharcha {money(total)} hai. Behtar budget ke liye expenses ko categories mein track karein aur zaroori kharchon ko pehle rakhein."
        elif any(word in q for word in ["task","plan","routine","schedule","din"]):
            pending = [x for x in st.session_state.tasks if not x["done"]]
            answer = f"Aapke {len(pending)} tasks abhi pending hain. Pehle high-priority task complete karein, phir chhotay tasks karein. Har kaam ke liye realistic time rakhein."
        elif any(word in q for word in ["shopping","list","khareed"]):
            pending = [x for x in st.session_state.shopping if not x["done"]]
            answer = f"Aapki shopping list mein {len(pending)} items baqi hain. Store jane se pehle list check karein aur zaroorat ke mutabiq items ko categories mein rakhein."
        elif any(word in q for word in ["meal","food","khana"]):
            answer = "Meal planning ke liye har din breakfast, lunch aur dinner pehle decide karein. Sabzi, fruit, protein aur pani ko apni routine ka hissa banayein."
        elif any(word in q for word in ["goal","motivate","motivation"]):
            answer = "Aaj sirf 2 ya 3 chhotay goals choose karein. Unhein complete hone par tick karein. Consistency perfection se zyada important hai."
        else:
            answer = "Main aapki daily planning, shopping, expenses, meals aur goals mein madad kar sakta hoon. Apna sawal thora specific likhein, jaise 'Mera budget kitna hai?' ya 'Aaj ke tasks kya hain?'"
        st.session_state.chat.append({"role":"assistant","content":answer})
        st.rerun()
    if st.button("Clear chat"):
        st.session_state.chat = []; st.rerun()

st.markdown("---")
st.markdown("<p style='text-align:center;color:#71839b;font-size:12px;'>LifeMate AI · Smart Home & Daily Life Assistant · Session-based demo</p>", unsafe_allow_html=True)
