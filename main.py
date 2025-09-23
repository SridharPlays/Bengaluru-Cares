import streamlit as st
import datetime
import event_manager
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# Page Configuration
st.set_page_config(
    page_title="Bengaluru Cares",
    page_icon="🤝",
    layout="wide"
)

# Initialize Session State
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'enrolled_events' not in st.session_state:
    st.session_state.enrolled_events = []
if 'page' not in st.session_state:
    st.session_state.page = "All Events"

def send_confirmation_email(user_name, user_email, event):
    """Sends a confirmation email to the user after they sign up for an event."""
    try:
        sender_email = st.secrets["email"]
        password = st.secrets["password"]

        sender_name = "Bengaluru Cares"

        # Create the email body
        subject = f"Confirmation: You're signed up for {event['title']}!"
        body = f"""
        Hi {user_name},

        This is a confirmation that you have successfully enrolled in the following event:

        Event: {event['title']}
        Organization: {event['organization']}
        Date: {event['date']}

        Thank you for volunteering with Bengaluru Cares! We look forward to seeing you there.

        Best,
        The Bengaluru Cares Team
        """

        # Create the email message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = formataddr((sender_name, sender_email))
        msg['To'] = user_email

        # Connect to Gmail SMTP server and send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, [user_email], msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email. Error: {e}")
        return False

def display_event_card(event, col):
    with col:
        with st.container(border=True):
            st.subheader(event['title'])
            st.write(f"🏢 **Organization:** {event['organization']}")
            st.write(f"📅 **Date:** {event['date']}")
            
            tags_html = "".join([f"<span style='background-color:#E0F2F1; color:#00796B; border-radius:5px; padding: 2px 8px; margin:2px;'>{tag.capitalize()}</span>" for tag in event.get('tags', [])])
            st.markdown(tags_html, unsafe_allow_html=True)
            
            st.write("")
            
            if st.session_state.user_name:
                if event['id'] in st.session_state.enrolled_events:
                    st.success("✅ You are enrolled!")
                else:
                    if st.button("Sign Up", key=f"signup_{event['id']}", type="primary"):
                        st.session_state.enrolled_events.append(event['id'])
                        
                        # Send confirmation email
                        email_sent = send_confirmation_email(
                            user_name=st.session_state.user_name,
                            user_email=st.session_state.user_email,
                            event=event
                        )
                        
                        if email_sent:
                            st.toast(f"🎉 Enrolled! A confirmation email has been sent.", icon="✅")
                        else:
                            st.toast(f"Enrolled, but we couldn't send a confirmation email.", icon="⚠️")
                        
                        st.rerun()
            else:
                st.warning("Please log in to sign up.")

st.sidebar.title("Welcome! 👋")
st.sidebar.header("Login")
user_name_input = st.sidebar.text_input("Enter your name", key="name_input")
user_email_input = st.sidebar.text_input("Enter your email", key="email_input")

if st.sidebar.button("Log In"):
    if user_name_input and user_email_input:
        st.session_state.user_name = user_name_input
        st.session_state.user_email = user_email_input
        st.toast(f"Welcome, {st.session_state.user_name}!")
        st.rerun()
    else:
        st.sidebar.warning("Please enter both your name and email.")

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
        my_events.sort(key=lambda x: x['date'])

        cols = st.columns(2)
        for i, event in enumerate(my_events):
            display_event_card(event, cols[i % 2])

# Page: Add an Event
elif st.session_state.page == "Add an Event":
    st.title("✍️ Add a New Volunteer Event")
    
    password = st.text_input("Enter Admin Password", type="password")
    if password == "admin123":
        with st.form(key="event_form", clear_on_submit=True):
            st.write("Fill out the details below to add a new event.")
            
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