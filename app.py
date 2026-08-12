import streamlit as st
import sqlite3
import random
import requests
from PyDictionary import PyDictionary

# Initialize PyDictionary safely
try:
    dictionary = PyDictionary()
except:
    dictionary = None

# Helper function to handle streamlit rerun compatibility across versions
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# -----------------------------------------------------------------
# PLAYFUL GEOMETRIC DESIGN SYSTEM - CSS INJECTION
# -----------------------------------------------------------------
st.markdown("""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;800&family=Plus+Jakarta+Sans:wght@400;500;700&display=swap');

    /* Global Resets & Background */
    .stApp {
        background-color: #FFFDF5 !important;
        background-image: url("data:image/svg+xml,%3Csvg width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='3' cy='3' r='2' fill='%23E2E8F0' /%3E%3C/svg%3E") !important;
        background-size: 48px 48px !important;
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
        color: #1E293B !important;
    }

    /* Container max-width */
    .stMain {
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding: 2rem 1rem !important;
    }

    /* Headings - Outfit, Bold, Clean */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        color: #1E293B !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.5rem !important;
    }

    /* Buttons - The "Candy Button" */
    div.stButton > button {
        background-color: #8B5CF6 !important; /* Accent Violet */
        color: #FFFFFF !important;
        border: 2px solid #1E293B !important;
        border-radius: 9999px !important; /* Pill */
        box-shadow: 4px 4px 0px #1E293B !important; /* Hard Pop Shadow */
        font-weight: 700 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        min-height: 48px !important;
    }

    div.stButton > button:hover {
        transform: translate(-2px, -2px) !important;
        box-shadow: 6px 6px 0px #1E293B !important;
    }

    div.stButton > button:active {
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0px #1E293B !important;
    }

    /* Secondary buttons (like "Restart") - using transparent style */
    div.stButton > button[kind="secondary"], 
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: transparent !important;
        color: #1E293B !important;
        border: 2px solid #1E293B !important;
        box-shadow: none !important;
    }
    
    div.stButton > button[kind="secondary"]:hover,
    div.stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: #FBBF24 !important; /* Tertiary Yellow */
        color: #1E293B !important;
    }

    /* Text Inputs */
    div.stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 16px !important; /* Radius-lg */
        color: #1E293B !important;
        padding: 12px 16px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        transition: all 0.2s ease !important;
        box-shadow: 4px 4px 0px transparent !important;
    }

    div.stTextInput > div > div > input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 4px 4px 0px #8B5CF6 !important; /* Hard shadow on focus */
    }

    /* Metrics (Scores) */
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        color: #8B5CF6 !important;
        font-size: 2.5rem !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }

    /* Alerts (Messages) */
    .stAlert {
        border-radius: 16px !important;
        border: 2px solid #1E293B !important;
        box-shadow: 4px 4px 0px #1E293B !important;
        background-color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stAlert > div {
        color: #1E293B !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        border-radius: 9999px !important;
        background-color: transparent !important;
        border: 2px solid #1E293B !important;
        margin-right: 8px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        padding: 0.5rem 1rem !important;
        color: #1E293B !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #8B5CF6 !important;
        color: #FFFFFF !important;
        border-color: #8B5CF6 !important;
    }

    /* Expanders - Sticker Card style */
    details.stExpander {
        border: 2px solid #1E293B !important;
        border-radius: 16px !important;
        background-color: #FFFFFF !important;
        box-shadow: 8px 8px 0px #E2E8F0 !important;
        padding: 0.5rem 1rem !important;
    }
    
    details.stExpander > summary {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Shuffled Word Challenge Box */
    .shuffled-box {
        background-color: #FFFFFF !important;
        border: 2px solid #1E293B !important;
        border-radius: 24px !important;
        box-shadow: 8px 8px 0px #F472B6 !important; /* Pink shadow */
        padding: 1.5rem !important;
        text-align: center !important;
        margin: 1rem 0 !important;
    }

    /* Respect reduced motion */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------
# DATABASE SETUP (SQLite3 for CRUD Operations)
# -----------------------------------------------------------------
def init_db():
    conn = sqlite3.connect('spelly_words.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_word_to_db(word):
    word = word.strip().lower()
    try:
        conn = sqlite3.connect('spelly_words.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO custom_words (word) VALUES (?)", (word,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_db_words():
    conn = sqlite3.connect('spelly_words.db')
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM custom_words")
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return words

def update_word_in_db(old_word, new_word):
    old_word = old_word.strip().lower()
    new_word = new_word.strip().lower()
    try:
        conn = sqlite3.connect('spelly_words.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE custom_words SET word = ? WHERE word = ?", (new_word, old_word))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def delete_word_from_db(word):
    word = word.strip().lower()
    conn = sqlite3.connect('spelly_words.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_words WHERE word = ?", (word,))
    conn.commit()
    conn.close()

# -----------------------------------------------------------------
# WORD VALIDATION & MIT LINK FETCHING (AS PER PDF)
# -----------------------------------------------------------------
@st.cache_data
def load_mit_wordlist():
    # PDF mein diya gaya exact link
    url = "https://www.mit.edu/mecprice/wordlist.10000"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Wordlist ko process kar rahe hain aur clean words nikal rahe hain
            words = set(w.strip().lower() for w in response.text.split('\n') if w.strip() and w.strip().isalpha() and len(w.strip()) > 1)
            if words:
                return words
    except Exception as e:
        pass
    
    # Sirf tab chalega agar internet bilkul kaam na kare ya MIT server down ho
    return {
        "apple", "apricot", "ant", "airplane", "actor", "animal", "arrow",
        "banana", "berry", "book", "beautiful", "balloon", "butter", "bridge",
        "computer", "cat", "car", "challenge", "candle", "coffee", "camera",
        "dog", "door", "doctor", "dance", "diamond", "dolphin", "dragon",
        "elephant", "egg", "eagle", "earth", "engine", "energy", "elbow",
        "fox", "fish", "forest", "friend", "flower", "father", "feather",
        "game", "garden", "gold", "guitar", "grapes", "galaxy", "garlic",
        "house", "horse", "happy", "history", "hammer", "honey", "helmet",
        "island", "ice", "ink", "internet", "image", "iron", "insect",
        "jacket", "juice", "join", "joke", "journal", "jungle", "jewel",
        "kangaroo", "king", "key", "kitchen", "kite", "keyboard", "kidney",
        "lion", "lamp", "leaf", "lemon", "lizard", "laptop", "leather",
        "monkey", "mouse", "moon", "music", "market", "mirror", "melon",
        "nest", "night", "nature", "notebook", "needle", "necklace", "nurse",
        "orange", "owl", "ocean", "office", "onion", "olive", "ostrich",
        "python", "pen", "planet", "paper", "pencil", "pumpkin", "palace",
        "queen", "quiet", "quick", "question", "quilt", "quail", "quartz",
        "rabbit", "river", "rain", "rose", "rocket", "ring", "robot",
        "streamlit", "sun", "star", "school", "shadow", "silver", "spider",
        "tiger", "tree", "train", "time", "tomato", "turtle", "ticket",
        "umbrella", "uncle", "universe", "under", "unicorn", "unite", "urgent",
        "violin", "valley", "voice", "view", "vessel", "village", "velvet",
        "water", "window", "wolf", "world", "wallet", "weapon", "whisper",
        "xylophone", "xray", "yacht", "yellow", "year", "young", "yoga", "yolk",
        "zebra", "zoo", "zone", "zero", "zipper", "zigzag", "zenith"
    }

def get_word_hint(word):
    if not word:
        return "No word to guess right now."
    if dictionary is None:
        return f"The word starts with '{word[0].upper()}' and has {len(word)} letters."
    try:
        meanings = dictionary.meaning(word)
        synonyms = dictionary.synonym(word)
        
        hint_text = ""
        if meanings:
            first_key = list(meanings.keys())[0]
            hint_text += f"**Meaning ({first_key}):** {meanings[first_key][0]}\n\n"
        if synonyms:
            hint_text += f"**Synonyms:** {', '.join(synonyms[:3])}"
        if hint_text:
            return hint_text
    except:
        pass
    return f"The word starts with '{word[0].upper()}' and has {len(word)} letters."

# -----------------------------------------------------------------
# GAME INITIALIZATION & SESSION STATES
# -----------------------------------------------------------------
init_db()
mit_words = load_mit_wordlist()
db_words = get_all_db_words()
all_valid_words = mit_words.union(set(db_words))

st.set_page_config(page_title="Spelly Word Game", page_icon="🎮", layout="centered")
st.title("Spelly Word Game")

if 'player_score' not in st.session_state:
    st.session_state.player_score = 0
if 'computer_score' not in st.session_state:
    st.session_state.computer_score = 0
if 'used_words' not in st.session_state:
    st.session_state.used_words = []
if 'current_word' not in st.session_state:
    st.session_state.current_word = ""
if 'shuffled_word' not in st.session_state:
    st.session_state.shuffled_word = ""
if 'hint_text' not in st.session_state:
    st.session_state.hint_text = ""
if 'last_letter' not in st.session_state:
    st.session_state.last_letter = ""
if 'turn_step' not in st.session_state:
    st.session_state.turn_step = "START"
if 'game_msg' not in st.session_state:
    st.session_state.game_msg = ("Welcome! Enter any valid word to start the Antakshari chain.", "info")

# -----------------------------------------------------------------
# GAME LOGIC FUNCTIONS (Turn-based AI & Shuffling)
# -----------------------------------------------------------------
def shuffle_word(word):
    word_chars = list(word)
    # Loop se bachne ke liye shuffle tab tak karein jab tak word badal na jaye
    attempts = 0
    while "".join(word_chars) == word and attempts < 10:
        random.shuffle(word_chars)
        attempts += 1
    return "".join(word_chars)

def trigger_computer_turn(from_letter):
    possible_words = [w for w in all_valid_words if w.startswith(from_letter) and w not in st.session_state.used_words]
    
    if possible_words:
        chosen_word = random.choice(possible_words)
        st.session_state.current_word = chosen_word
        st.session_state.shuffled_word = shuffle_word(chosen_word)
        st.session_state.used_words.append(chosen_word)
        st.session_state.computer_score += len(chosen_word)
        st.session_state.turn_step = "GUESS_SHUFFLED_WORD"
        st.session_state.hint_text = ""
        st.session_state.game_msg = (f"AI Opponent played a word starting with '{from_letter.upper()}'. Unscramble it!", "success")
        return True
    return False

def process_game_turn(user_input):
    user_input = user_input.strip().lower()
    if not user_input:
        st.session_state.game_msg = ("Please enter a word!", "warning")
        return

    if st.session_state.turn_step in ["START", "PLAY_NEW_WORD"]:
        if st.session_state.last_letter and not user_input.startswith(st.session_state.last_letter):
            st.session_state.game_msg = (f"Rule Error! Your word must start with the letter '{st.session_state.last_letter.upper()}'.", "error")
            return
            
        if user_input in st.session_state.used_words:
            st.session_state.game_msg = ("This word has already been used! Try a different one.", "warning")
            return

        if user_input in all_valid_words:
            st.session_state.used_words.append(user_input)
            st.session_state.player_score += len(user_input)
            
            next_letter = user_input[-1]
            ai_success = trigger_computer_turn(next_letter)
            if not ai_success:
                st.session_state.game_msg = (f"You Win! Computer couldn't find any word starting with '{next_letter.upper()}'.", "success")
                st.session_state.turn_step = "START"
                st.session_state.last_letter = ""
        else:
            st.session_state.game_msg = ("Invalid word! Word not found in MIT list or Local Database.", "error")

    elif st.session_state.turn_step == "GUESS_SHUFFLED_WORD":
        if user_input == st.session_state.current_word:
            st.session_state.player_score += len(user_input)
            st.session_state.last_letter = user_input[-1]
            st.session_state.shuffled_word = ""
            # Clear current word AFTER getting hint if needed, but here turn changes
            st.session_state.turn_step = "PLAY_NEW_WORD"
            st.session_state.hint_text = ""
            st.session_state.game_msg = (f"Correct Guess! Now it's your turn to enter a NEW word starting with '{st.session_state.last_letter.upper()}'.", "success")
        else:
            st.session_state.game_msg = ("Incorrect spelling/guess! Try again or use a hint.", "error")

def reset_game():
    st.session_state.player_score = 0
    st.session_state.computer_score = 0
    st.session_state.used_words = []
    st.session_state.current_word = ""
    st.session_state.shuffled_word = ""
    st.session_state.hint_text = ""
    st.session_state.last_letter = ""
    st.session_state.turn_step = "START"
    st.session_state.game_msg = ("Game reset! Enter a new word to start.", "info")

# -----------------------------------------------------------------
# USER INTERFACE (UI WITH ACTION TABS)
# -----------------------------------------------------------------
tab1, tab2 = st.tabs(["Spelly Arena", "Word Management"])

with tab1:
    st.subheader("Game Board")
    
    # Score Cards (Sticker style)
    col_p, col_c, col_t = st.columns(3)
    with col_p:
        st.metric(label="Your Score", value=st.session_state.player_score)
    with col_c:
        st.metric(label="AI Score", value=st.session_state.computer_score)
    with col_t:
        if st.session_state.turn_step == "START":
            st.markdown("**Phase:** Start")
        elif st.session_state.turn_step == "PLAY_NEW_WORD":
            st.markdown(f"**Phase:** New Word (`{st.session_state.last_letter.upper()}`)")
        else:
            st.markdown("**Phase:** Guessing")

    # Game Messages
    msg_text, msg_type = st.session_state.game_msg
    if msg_type == "success": st.success(msg_text)
    elif msg_type == "error": st.error(msg_text)
    elif msg_type == "warning": st.warning(msg_text)
    else: st.info(msg_text)

    # Shuffled Word Challenge Display
    if st.session_state.turn_step == "GUESS_SHUFFLED_WORD" and st.session_state.shuffled_word:
        st.markdown(
            f"""
            <div class="shuffled-box">
                <div style="font-size:1rem; color:#64748B; font-weight:500;">🔀 Unscramble this word</div>
                <div style="font-size:2.8rem; font-weight:800; color:#1E293B; letter-spacing: 6px; font-family: 'Outfit', sans-serif;">
                    {st.session_state.shuffled_word.upper()}
                </div>
                <div style="font-size:0.9rem; color:#64748B; margin-top:8px;">
                    Hint: Starts with <strong>'{st.session_state.current_word[0].upper()}'</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Game Input Form
    with st.form(key="game_entry_form", clear_on_submit=True):
        if st.session_state.turn_step == "GUESS_SHUFFLED_WORD":
            prompt_lbl = "Unscramble and type the correct word:"
        elif st.session_state.turn_step == "PLAY_NEW_WORD":
            prompt_lbl = f"Type a new word starting with '{st.session_state.last_letter.upper()}':"
        else:
            prompt_lbl = "Type any valid English word to begin the game:"
            
        user_input_val = st.text_input(prompt_lbl)
        submit_action = st.form_submit_button(label="Submit Move")
        if submit_action:
            process_game_turn(user_input_val)
            safe_rerun()

    # Action Buttons
    c1, c2 = st.columns(2)
    if st.session_state.turn_step == "GUESS_SHUFFLED_WORD":
        if c1.button("💡 Ask AI for Hint", use_container_width=True):
            st.session_state.hint_text = get_word_hint(st.session_state.current_word)
            safe_rerun()
            
    if c2.button("🔄 Restart Match", use_container_width=True):
        reset_game()
        safe_rerun()

    # Hint display
    if st.session_state.hint_text:
        st.info(f"**Hint:**\n\n{st.session_state.hint_text}")

    # History expander
    if st.session_state.used_words:
        with st.expander("📜 Word History Chain"):
            st.write(" ➡️ ".join([w.upper() for w in st.session_state.used_words]))

with tab2:
    st.subheader("Database Control")
    
    new_word_input = st.text_input("Add Custom Word to Dictionary:")
    if st.button("➕ Create Word"):
        if new_word_input.isalpha():
            if add_word_to_db(new_word_input):
                st.success(f"'{new_word_input}' added to database successfully!")
                st.rerun()
            else:
                st.warning("Word already exists in your database.")
        else:
            st.error("Please enter alphabetical characters only.")

    st.markdown("---")
    current_db_words = get_all_db_words()
    if current_db_words:
        selected_word = st.selectbox("Select Word to Update/Delete:", current_db_words)
        col_edit, col_del = st.columns(2)
        
        with col_edit:
            updated_name = st.text_input("Modify Word Text:", value=selected_word)
            if st.button("📝 Save Update"):
                if updated_name.isalpha() and update_word_in_db(selected_word, updated_name):
                    st.success("Word modified successfully!")
                    safe_rerun()
                else:
                    st.error("Failed to update.")
                    
        with col_del:
            if st.button("🗑️ Permanent Delete", type="primary"):
                delete_word_from_db(selected_word)
                st.success("Word removed!")
                safe_rerun()
    else:
        st.info("Local SQLite database is currently empty.")
