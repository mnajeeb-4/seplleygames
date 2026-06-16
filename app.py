import streamlit as st
import sqlite3
import random
import requests
from PyDictionary import PyDictionary

# Initialize PyDictionary for hints
dictionary = PyDictionary()

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
# WORD VALIDATION & MIT WORDLIST FETCHING
# -----------------------------------------------------------------
@st.cache_data
def load_mit_wordlist():
    # PDF Requirement: Validate words using the official MIT 10,000 wordlist link
    url = "https://www.mit.edu/mecprice/wordlist.10000"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return set(w.strip().lower() for w in response.text.split('\n') if w.strip())
    except:
        pass
    # Fallback words if internet is slow or connection fails
    return {"apple", "banana", "computer", "elephant", "game", "python", "streamlit", "zebra", "tiger", "orange"}

def get_word_hint(word):
    # PyDictionary implementation for meanings & synonyms as per PDF
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
st.title("🎮 Spelly Word Game")

# Tracking stats and scores according to PDF
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
    st.session_state.turn_step = "START"  # Statuses: START, PLAY_NEW_WORD, GUESS_SHUFFLED_WORD
if 'game_msg' not in st.session_state:
    st.session_state.game_msg = ("Welcome! Enter any valid word to start the Antakshari chain.", "info")

# -----------------------------------------------------------------
# GAME LOGIC FUNCTIONS (Turn-based AI & Shuffling)
# -----------------------------------------------------------------
def shuffle_word(word):
    word_chars = list(word)
    random.shuffle(word_chars)
    return "".join(word_chars)

def trigger_computer_turn(from_letter):
    # AI logic: Find word starting with last letter of player's word and not used before
    possible_words = [w for w in all_valid_words if w.startswith(from_letter) and w not in st.session_state.used_words]
    
    if possible_words:
        chosen_word = random.choice(possible_words)
        st.session_state.current_word = chosen_word
        st.session_state.shuffled_word = shuffle_word(chosen_word)
        st.session_state.used_words.append(chosen_word)
        st.session_state.computer_score += len(chosen_word)  # Score tracked by word length
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

    # STEP 1: Player is starting the game or continuing the chain with a new word
    if st.session_state.turn_step in ["START", "PLAY_NEW_WORD"]:
        # Enforce last letter rule if it's a running chain
        if st.session_state.last_letter and not user_input.startswith(st.session_state.last_letter):
            st.session_state.game_msg = (f"Rule Error! Your word must start with the letter '{st.session_state.last_letter.upper()}'.", "error")
            return
            
        if user_input in st.session_state.used_words:
            st.session_state.game_msg = ("This word has already been used! Try a different one.", "warning")
            return

        if user_input in all_valid_words:
            st.session_state.used_words.append(user_input)
            st.session_state.player_score += len(user_input)
            
            # Instantly switch to Computer's Turn
            next_letter = user_input[-1]
            ai_success = trigger_computer_turn(next_letter)
            if not ai_success:
                st.session_state.game_msg = (f"You Win! Computer couldn't find any word starting with '{next_letter.upper()}'.", "success")
                st.session_state.turn_step = "START"
                st.session_state.last_letter = ""
        else:
            st.session_state.game_msg = ("Invalid word! Word not found in MIT list or Local Database.", "error")

    # STEP 2: Player is guessing/unscrambling the Computer's Shuffled Word
    elif st.session_state.turn_step == "GUESS_SHUFFLED_WORD":
        if user_input == st.session_state.current_word:
            st.session_state.player_score += len(user_input)
            st.session_state.last_letter = user_input[-1]
            st.session_state.shuffled_word = ""
            st.session_state.current_word = ""
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
tab1, tab2 = st.tabs(["🎮 Spelly Arena", "⚙️ Word Management (Database)"])

with tab1:
    st.subheader("Game Board")
    
    # Dual Score and Information Display
    col_p, col_c, col_t = st.columns(3)
    col_p.metric(label="👤 Your Score", value=st.session_state.player_score)
    col_c.metric(label="🤖 AI Score", value=st.session_state.computer_score)
    
    # Custom Turn Status Indicator for clarity
    if st.session_state.turn_step == "START":
        col_t.markdown("**Current Phase:**\n\n🟢 Start Game")
    elif st.session_state.turn_step == "PLAY_NEW_WORD":
        col_t.markdown(f"**Current Phase:**\n\n📝 New Word (`{st.session_state.last_letter.upper()}`)")
    else:
        col_t.markdown("**Current Phase:**\n\n🧩 Guessing Word")

    # Game Alerts and Feedback
    msg_text, msg_type = st.session_state.game_msg
    if msg_type == "success": st.success(msg_text)
    elif msg_type == "error": st.error(msg_text)
    elif msg_type == "warning": st.warning(msg_text)
    else: st.info(msg_text)

    # Shuffled Word Challenge Display
    if st.session_state.turn_step == "GUESS_SHUFFLED_WORD" and st.session_state.shuffled_word:
        st.markdown(f"<div style='background-color:#f0f2f6; padding:15px; border-radius:10px; text-align:center; margin-bottom:15px;'>"
                    f"<span style='font-size:1.2rem; color:#31333F;'>🔀 Shuffled Word Challenge:</span><br>"
                    f"<strong style='font-size:2.2rem; color:#ff4b4b; letter-spacing: 3px;'>{st.session_state.shuffled_word.upper()}</strong>"
                    f"</div>", unsafe_allow_html=True)
        st.caption(f"Hint Rule: The secret word starts with the letter: **'{st.session_state.current_word[0].upper()}'**")

    # Interactive Input Field
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
            st.rerun()

    # Hints and Reset Systems
    c1, c2 = st.columns(2)
    if st.session_state.turn_step == "GUESS_SHUFFLED_WORD":
        if c1.button("💡 Ask AI for Hint", use_container_width=True):
            st.session_state.hint_text = get_word_hint(st.session_state.current_word)
            st.rerun()
            
    if c2.button("🔄 Restart Match", use_container_width=True):
        reset_game()
        st.rerun()

    if st.session_state.hint_text:
        st.info(f"**AI Hint Details:**\n\n{st.session_state.hint_text}")

    if st.session_state.used_words:
        with st.expander("📜 Word History Chain"):
            st.write(" ➡️ ".join([w.upper() for w in st.session_state.used_words]))

with tab2:
    st.subheader("Local Database Control (CRUD)")
    
    new_word_input = st.text_input("Add Custom Word to Dictionary:")
    if st.button("➕ Create Word"):
        if new_word_input.isalpha():
            if add_word_to_db(new_word_input):
                st.success(f"'{new_word_input}' added to database successfully!")
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
                    st.rerun()
                else:
                    st.error("Failed to update.")
                    
        with col_del:
            st.write("Action:")
            if st.button("🗑️ Permanent Delete", type="primary"):
                delete_word_from_db(selected_word)
                st.success("Word removed!")
                st.rerun()
    else:
        st.info("Local SQLite database is currently empty.")
