import streamlit as st
import sqlite3
import random
import requests
from PyDictionary import PyDictionary  # PDF REQUIREMENT ADDED

# Initialize PyDictionary
dictionary = PyDictionary()

# -----------------------------------------------------------------
# DATABASE SETUP (SQLite3)
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
# WORD VALIDATION & PYDICTIONARY HINT SYSTEM
# -----------------------------------------------------------------
@st.cache_data
def load_mit_wordlist():
    url = "https://www.mit.edu/mecprice/wordlist.10000"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return set(w.strip().lower() for w in response.text.split('\n') if w.strip())
    except:
        pass
    return {"apple", "banana", "computer", "elephant", "game", "python", "streamlit", "zebra", "tiger", "orange"}

def get_word_hint(word):
    # Fetching Meanings and Synonyms using PyDictionary as per PDF
    try:
        meanings = dictionary.meaning(word)
        synonyms = dictionary.synonym(word)
        
        hint_text = ""
        if meanings:
            # Get the first part of speech (e.g., Noun, Verb) and its first definition
            first_key = list(meanings.keys())[0]
            hint_text += f"**Meaning ({first_key}):** {meanings[first_key][0]}\n\n"
        
        if synonyms:
            # Take top 3 synonyms
            hint_text += f"**Synonyms:** {', '.join(synonyms[:3])}"
            
        if hint_text:
            return hint_text
    except:
        pass
    
    # Fallback agar PyDictionary kisi word ka data na nikal paaye
    return f"The word starts with '{word[0].upper()}' and has {len(word)} letters."

# -----------------------------------------------------------------
# GAME INITIALIZATION
# -----------------------------------------------------------------
init_db()
mit_words = load_mit_wordlist()
db_words = get_all_db_words()
all_valid_words = mit_words.union(set(db_words))

st.set_page_config(page_title="Spelly Word Game", page_icon="🎮", layout="centered")
st.title("🎮 Spelly Word Game")

if 'score' not in st.session_state:
    st.session_state.score = 0
if 'used_words' not in st.session_state:
    st.session_state.used_words = []
if 'current_word' not in st.session_state:
    st.session_state.current_word = ""
if 'shuffled_word' not in st.session_state:
    st.session_state.shuffled_word = ""
if 'hint_text' not in st.session_state:
    st.session_state.hint_text = ""
if 'game_msg' not in st.session_state:
    st.session_state.game_msg = ("Welcome! Enter any valid word to start the game.", "info")

# -----------------------------------------------------------------
# GAME LOGIC FUNCTIONS
# -----------------------------------------------------------------
def shuffle_word(word):
    word_chars = list(word)
    random.shuffle(word_chars)
    return "".join(word_chars)

def computer_turn(last_letter):
    possible_words = [w for w in all_valid_words if w.startswith(last_letter) and w not in st.session_state.used_words]
    if possible_words:
        chosen_word = random.choice(possible_words)
        st.session_state.current_word = chosen_word
        st.session_state.shuffled_word = shuffle_word(chosen_word)
        st.session_state.used_words.append(chosen_word)
        st.session_state.hint_text = "" 
        return True
    return False

def handle_player_guess(user_input):
    user_input = user_input.strip().lower()
    if not user_input:
        st.session_state.game_msg = ("Please enter a word!", "warning")
        return

    if not st.session_state.current_word:
        if user_input in all_valid_words:
            st.session_state.used_words.append(user_input)
            st.session_state.score += len(user_input)
            last_char = user_input[-1]
            success = computer_turn(last_char)
            if success:
                st.session_state.game_msg = ("Good start! Computer played a word. Unscramble it!", "success")
            else:
                st.session_state.game_msg = (f"You won! Computer couldn't find a word starting with '{last_char.upper()}'.", "success")
        else:
            st.session_state.game_msg = ("Invalid word! Please enter a real dictionary word.", "error")
    else:
        if user_input == st.session_state.current_word:
            st.session_state.score += len(user_input)
            last_char = user_input[-1]
            success = computer_turn(last_char)
            if success:
                st.session_state.game_msg = (f"Correct! +{len(user_input)} Points. Computer played another word. Solve it!", "success")
            else:
                st.session_state.game_msg = ("Correct! But Computer is out of words. You Win!", "success")
        else:
            st.session_state.game_msg = ("Incorrect spelling! Try again or use a hint.", "error")

def reset_game():
    st.session_state.score = 0
    st.session_state.used_words = []
    st.session_state.current_word = ""
    st.session_state.shuffled_word = ""
    st.session_state.hint_text = ""
    st.session_state.game_msg = ("Game reset! Enter a new word to start.", "info")

# -----------------------------------------------------------------
# USER INTERFACE (UI)
# -----------------------------------------------------------------
tab1, tab2 = st.tabs(["🎮 Play Game", "⚙️ Word Management (CRUD)"])

with tab1:
    st.subheader("Spelly Arena")
    col1, col2 = st.columns(2)
    col1.metric(label="Your Score", value=st.session_state.score)
    col2.metric(label="Words Used", value=len(st.session_state.used_words))
    
    msg_text, msg_type = st.session_state.game_msg
    if msg_type == "success": st.success(msg_text)
    elif msg_type == "error": st.error(msg_text)
    elif msg_type == "warning": st.warning(msg_text)
    else: st.info(msg_text)

    if st.session_state.shuffled_word:
        st.markdown(f"### 🔀 Shuffled Word Challenge: `{st.session_state.shuffled_word.upper()}`")
        st.caption(f"Hint Rule: The word actually starts with the letter: **'{st.session_state.current_word[0].upper()}'**")

    with st.form(key="game_form", clear_on_submit=True):
        user_guess = st.text_input("Enter your word / guess here:")
        submit_btn = st.form_submit_button(label="Submit")
        if submit_btn:
            handle_player_guess(user_guess)
            st.rerun()

    c1, c2 = st.columns(2)
    if st.session_state.current_word:
        if c1.button("💡 Get Hint", use_container_width=True):
            st.session_state.hint_text = get_word_hint(st.session_state.current_word)
            st.rerun()
            
    if c2.button("🔄 Reset Game", use_container_width=True):
        reset_game()
        st.rerun()

    if st.session_state.hint_text:
        st.info(f"**Hint Details:**\n\n{st.session_state.hint_text}")

    if st.session_state.used_words:
        with st.expander("📜 History of Words Used"):
            st.write(", ".join(st.session_state.used_words))

with tab2:
    st.subheader("Local Database Management")
    new_word_input = st.text_input("Add New Word to Database:")
    if st.button("➕ Add Word"):
        if new_word_input.isalpha():
            if add_word_to_db(new_word_input):
                st.success(f"'{new_word_input}' successfully added!")
            else:
                st.warning("Word already exists in database.")
        else:
            st.error("Please enter a valid word without numbers or symbols.")

    st.markdown("---")
    current_db_words = get_all_db_words()
    if current_db_words:
        selected_word = st.selectbox("Select a word to Update or Delete:", current_db_words)
        col_edit, col_del = st.columns(2)
        
        with col_edit:
            updated_name = st.text_input("Edit Selected Word:", value=selected_word)
            if st.button("📝 Update Word"):
                if updated_name.isalpha() and update_word_in_db(selected_word, updated_name):
                    st.success("Word updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update word.")
                    
        with col_del:
            st.write("Danger Zone:")
            if st.button("🗑️ Delete Word", type="primary"):
                delete_word_from_db(selected_word)
                st.success("Word deleted successfully!")
                st.rerun()
    else:
        st.info("Database is currently empty.")
