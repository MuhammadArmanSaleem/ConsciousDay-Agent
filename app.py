import streamlit as st
import bcrypt
from agent.ref_agent import analyze_inputs
from db.utils import (
    create_table,
    upgrade_table_if_needed,
    insert_entry,
    get_all_entries,
    delete_entry
)
from db.user_utils import create_users_table, add_user, get_user

# 🔐 Initialize DBs and upgrade schema
create_table()
create_users_table()
upgrade_table_if_needed()

st.title("🧘 ConsciousDay - Morning Reflection Agent")

# ================== 🔐 AUTH SECTION ==================
st.sidebar.title("👤 Login or Register")

if 'username' not in st.session_state:
    register_mode = st.sidebar.checkbox("🆕 Register new account?")
    name_input = st.sidebar.text_input("Your Name")
    password_input = st.sidebar.text_input("Your Password", type="password")

    if register_mode:
        if st.sidebar.button("Register"):
            if not name_input or not password_input:
                st.sidebar.warning("❌ Please enter both name and password.")
            elif get_user(name_input):
                st.sidebar.warning("❌ That name is already taken.")
            else:
                hashed_password = bcrypt.hashpw(password_input.encode(), bcrypt.gensalt()).decode()
                add_user(username=name_input, name=name_input, email="", password_hash=hashed_password)
                st.sidebar.success(f"✅ '{name_input}' registered successfully!")
                st.session_state['username'] = name_input
                st.rerun()
    else:
        if st.sidebar.button("Login"):
            user = get_user(name_input)
            if not user:
                st.sidebar.error("❌ User not found.")
            else:
                stored_hash = user[3]
                if bcrypt.checkpw(password_input.encode(), stored_hash.encode()):
                    st.session_state['username'] = name_input
                    st.sidebar.success(f"✅ Welcome {user[1]}!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Incorrect password")
else:
    st.sidebar.success(f"✅ Logged in as: {st.session_state['username']}")
    if st.sidebar.button("Logout"):
        del st.session_state['username']
        st.cache_data.clear()
        st.rerun()

# ================== 🔒 JOURNAL SECTION ==================
if 'username' in st.session_state:

    @st.cache_data(ttl=60)
    def cached_get_all_entries(username):
        return get_all_entries(username)

    st.sidebar.subheader("📝 Past Entries")
    entries = cached_get_all_entries(st.session_state['username'])

    selected_id = None
    if entries:
        selected_id = st.sidebar.selectbox(
            "Pick an entry to view",
            options=[row[0] for row in entries],
            format_func=lambda id_: next((e[1] for e in entries if e[0] == id_), "")
        )
    else:
        st.sidebar.info("No entries found yet.")

    if selected_id:
        entry = next((e for e in entries if e[0] == selected_id), None)
        if entry:
            st.markdown(f"## 🪞 Reflection on {entry[1]}")
            st.markdown(f"**📝 Journal:** {entry[2]}")
            st.markdown(f"**🎯 Intention:** {entry[3]}")
            st.markdown(f"**💤 Dream:** {entry[4]}")
            st.markdown(f"**📌 Priorities:** {entry[5]}")
            st.markdown("### 💡 Reflection Summary")
            st.write(entry[6])
            st.markdown("### 🗓 Suggested Day Strategy")
            st.write(entry[7])

            st.markdown("---")
            confirm_key = f"confirm_delete_{selected_id}"
            confirm_delete = st.checkbox("✅ Confirm delete?", key=confirm_key)
            if confirm_delete and st.button("🗑️ Delete Entry"):
                delete_entry(selected_id)
                st.success("Entry deleted successfully!")
                st.session_state[confirm_key] = False
                st.cache_data.clear()
                st.rerun()

    # ================== ✍️ ENTRY FORM ==================
    st.markdown("---")
    st.subheader("📝 Create a new Entry")

    with st.form("entry_form"):
        journal = st.text_area("🌄 Morning Journal")
        dream = st.text_area("💤 Dream")
        intention = st.text_input("🎯 Intention of the Day")
        priorities = st.text_input("📌 Top 3 Priorities (comma-separated)")

        if st.form_submit_button("Generate Insight"):
            with st.spinner("Thinking..."):
                result = analyze_inputs(journal, dream, intention, priorities)

            st.subheader("🪞 Reflection Summary")
            st.write(result.get("reflection", "No reflection available."))
            st.subheader("🗓 Suggested Day Strategy")
            st.write(result.get("strategy", "No strategy generated."))

            insert_entry(
                st.session_state['username'],
                journal,
                intention,
                dream,
                priorities,
                result.get("reflection"),
                result.get("strategy")
            )
            st.success("Saved successfully!")
            st.cache_data.clear()
else:
    st.warning("🔐 Please login to access your journal.")
