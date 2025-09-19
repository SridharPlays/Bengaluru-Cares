import streamlit as st
import datetime
import event_manager

# Page Configuration
st.set_page_config(
    page_title="Bengaluru Cares",
    page_icon="🤝",
    layout="wide"
)

# Initialize Session State
# This is like a browser cookie, remembering info for a user's session.
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'enrolled_events' not in st.session_state:
    st.session_state.enrolled_events = []
if 'page' not in st.session_state:
    st.session_state.page = "All Events"

# Reusable Functions
def display_event_card(event, col):
    """A reusable function to display an event card."""
    with col:
        with st.container(border=True):
            st.subheader(event['title'])
            st.write(f"🏢 **Organization:** {event['organization']}")
            st.write(f"📅 **Date:** {event['date']}")
            
            tags_html = "".join([f"<span style='background-color:#E0F2F1; color:#00796B; border-radius:5px; padding: 2px 8px; margin:2px;'>{tag.capitalize()}</span>" for tag in event.get('tags', [])])
            st.markdown(tags_html, unsafe_allow_html=True)
            
            st.write("")
            
            # Sign up logic
            if st.session_state.user_name:
                if event['id'] in st.session_state.enrolled_events:
                    st.success("✅ You are enrolled!")
                else:
                    if st.button("Sign Up", key=f"signup_{event['id']}", type="primary"):
                        st.session_state.enrolled_events.append(event['id'])
                        st.toast(f"🎉 Enrolled in {event['title']}!", icon="✅")
                        st.rerun() # Refresh the page to update the button status
            else:
                st.warning("Please log in to sign up.")

# Sidebar for Login & Navigation
st.sidebar.title("Welcome! 👋")
user_name_input = st.sidebar.text_input("Enter your name to log in", key="login_input")
if st.sidebar.button("Log In"):
    st.session_state.user_name = user_name_input
    st.toast(f"Welcome, {st.session_state.user_name}!")
    st.rerun()

if st.session_state.user_name:
    st.sidebar.success(f"Logged in as **{st.session_state.user_name}**")
    st.sidebar.markdown("---")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["All Events", "My Events", "Add an Event"])
st.session_state.page = page

# Page: All Events
if st.session_state.page == "All Events":
    st.title("🤝 Bengaluru Cares: All Events")
    all_events = event_manager.load_events()
    # Sort events by date using a lambda function
    all_events.sort(key=lambda x: x['date'])

    cols = st.columns(2)
    event_count = 0
    for event in all_events:
        event_date = datetime.datetime.strptime(event['date'], "%Y-%m-%d").date()
        if event_date >= datetime.date.today():
            display_event_card(event, cols[event_count % 2])
            event_count += 1
    if event_count == 0:
        st.info("No upcoming events found.")

# Page: My Events
elif st.session_state.page == "My Events":
    st.title("👤 My Enrolled Events")
    if not st.session_state.user_name:
        st.warning("Please log in to see your events.")
    elif not st.session_state.enrolled_events:
        st.info("You haven't signed up for any events yet. Go to 'All Events' to find one!")
    else:
        all_events = event_manager.load_events()
        my_events = [event for event in all_events if event['id'] in st.session_state.enrolled_events]
        my_events.sort(key=lambda x: x['date']) # Sort by date

        cols = st.columns(2)
        for i, event in enumerate(my_events):
            display_event_card(event, cols[i % 2])

# Page: Add an Event
elif st.session_state.page == "Add an Event":
    st.title("✍️ Add a New Volunteer Event")
    
    # Simple password protection for this feature
    password = st.text_input("Enter Admin Password", type="password")
    if password == "admin123": # You can change this password
        with st.form(key="event_form", clear_on_submit=True):
            st.write("Fill out the details below to add a new event.")
            
            # Form fields
            title = st.text_input("Event Title*")
            organization = st.text_input("Organization Name*")
            date = st.date_input("Date*")
            tags_input = st.text_input("Tags (comma-separated, e.g., environment, cleanup)*")
            spots = st.number_input("Number of Spots*", min_value=1, step=1)

            submitted = st.form_submit_button("Submit Event")

            if submitted:
                if not all([title, organization, date, tags_input, spots]):
                    st.error("Please fill out all required fields marked with *")
                else:
                    all_events = event_manager.load_events()
                    new_id = max([e['id'] for e in all_events] + [0]) + 1
                    
                    new_event = {
                        "id": new_id,
                        "title": title,
                        "organization": organization,
                        "date": date.strftime("%Y-%m-%d"),
                        "spots": spots,
                        "tags": [tag.strip() for tag in tags_input.split(",")]
                    }
                    
                    all_events.append(new_event)
                    event_manager.save_events(all_events)
                    st.success("Event added successfully!")
    elif password:
        st.error("Incorrect password.")