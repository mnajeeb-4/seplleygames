import streamlit as st
import sqlite3
import random
import requests
from PyDictionary import PyDictionary
import time

# --- 1. DATABASE MANAGEMENT (SQLite3) ---
def init_db():
    conn = sqlite3.connect('spelly.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS words (word TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

def add_word_db(word):
    conn = sqlite3.connect('spelly.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO words (word) VALUES (?)", (word.lower(),))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Word already exists
    conn.close()

def get_all_words_db():
    conn = sqlite3.connect('spelly.db')
    c = conn.cursor()
    c.execute("SELECT word FROM words")
    words = [row[0] for row in c.fetchall()]
    conn.close()
    return words

def delete_word_db(word):
    conn = sqlite3.connect('spelly.db')
    c = conn.cursor()
    c.execute("DELETE FROM words WHERE word=?", (word.lower(),))
    conn.commit()
    conn.close()

# --- 2. WORD VALIDATION & API ---
@st.cache_data
def load_word_list():
    # Fetches the required MIT word list
    try:
        response = requests.get("https://www.mit.edu/mecprice/wordlist.10000")
        words = response.text.splitlines()
        return [w.lower() for w in words]
    except:
        return ["apple", "elephant", "tiger", "rabbit", "turtle"] # Fallback

def get_hint(word):
    dictionary = PyDictionary()
    meaning = dictionary.meaning(word)
    if meaning:
        # Return the first meaning found
        for pos, meanings in meaning.items():
            return f"({pos}) {meanings[0]}"
    return "No hint available for this word."

# --- 3. GAME LOGIC & STATE INITIALIZATION ---
def init_session_state():
    if 'used_words' not in st.session_state:
        st.session_state.used_words = []
    if 'player_score' not in st.session_state:
        st.session_state.player_score = 0
    if 'ai_score' not in st.session_state:
        st.session_state.ai_score = 0
    if 'current_turn' not in st.session_state:
        st.session_state.current_turn = 'Player'
    if 'last_letter' not in st.session_state:
        st.session_state.last_letter = ''
    if 'target_word' not in st.session_state:
        st.session_state.target_word = ''
    if 'shuffled_word' not in st.session_state:
        st.session_state.shuffled_word = ''

# --- 4. MAIN APP UI ---
def main():
    st.set_page_config(page_title="Spelly Word Game", layout="wide")
    init_db()
    init_session_state()
    valid_words = load_word_list()

    st.title("🎮 Spelly Word Game")
    
    # Sidebar for CRUD Operations
    with st.sidebar:
        st.header("Word Management (CRUD)")
        new_word = st.text_input("Add a custom word to DB:")
        if st.button("Add Word"):
            if new_word:
                add_word_db(new_word)
                st.success(f"'{new_word}' added!")
                
        st.subheader("Database Words")
        db_words = get_all_words_db()
        st.write(db_words)
        
        del_word = st.text_input("Delete a word:")
        if st.button("Delete"):
            delete_word_db(del_word)
            st.warning(f"'{del_word}' deleted!")

    # Main Game Area
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"🗣️ Player Score: {st.session_state.player_score}")
    with col2:
        st.subheader(f"🤖 AI Score: {st.session_state.ai_score}")

    st.divider()

    # Determine Valid Starting Letter
    if st.session_state.last_letter:
        st.info(f"The next word MUST start with the letter: **{st.session_state.last_letter.upper()}**")

    # --- PLAYER TURN ---
    if st.session_state.current_turn == 'Player':
        st.write("### Your Turn!")
        
        # Shuffled Word Challenge
        if not st.session_state.target_word:
            # Pick a word for the player to guess that starts with the right letter
            available_words = [w for w in valid_words if w not in st.session_state.used_words]
            if st.session_state.last_letter:
                available_words = [w for w in available_words if w.startswith(st.session_state.last_letter)]
            
            if available_words:
                st.session_state.target_word = random.choice(available_words)
                letters = list(st.session_state.target_word)
                random.shuffle(letters)
                st.session_state.shuffled_word = "".join(letters)
            else:
                st.error("No more words available! Game Over.")
                st.stop()

        st.warning(f"🔀 Unscramble this word: **{st.session_state.shuffled_word.upper()}**")
        
        # Hint Feature
        if st.button("💡 Get Hint"):
            hint_text = get_hint(st.session_state.target_word)
            st.info(f"Hint: {hint_text}")

        player_input = st.text_input("Enter your guessed word:").strip().lower()
        
        if st.button("Submit Word"):
            if player_input == st.session_state.target_word:
                st.success("Correct!")
                st.session_state.player_score += len(player_input)
                st.session_state.used_words.append(player_input)
                st.session_state.last_letter = player_input[-1] # Get last letter
                st.session_state.current_turn = 'AI'
                st.session_state.target_word = '' # Reset for next round
                st.rerun()
            else:
                st.error("Incorrect spelling. Try again!")

    # --- AI TURN ---
    elif st.session_state.current_turn == 'AI':
        st.write("### 🤖 Computer's Turn...")
        with st.spinner("AI is thinking..."):
            time.sleep(1.5) # Simulate thinking time
            
            available_words = [w for w in valid_words if w not in st.session_state.used_words]
            if st.session_state.last_letter:
                available_words = [w for w in available_words if w.startswith(st.session_state.last_letter)]
            
            if available_words:
                ai_word = random.choice(available_words)
                st.session_state.ai_score += len(ai_word)
                st.session_state.used_words.append(ai_word)
                st.session_state.last_letter = ai_word[-1]
                st.session_state.current_turn = 'Player'
                
                st.success(f"The AI played: **{ai_word.upper()}**")
                time.sleep(2)
                st.rerun()
            else:
                st.error("AI couldn't find a word. You win!")

    st.divider()
    st.write("### 📜 Used Words List")
    st.write(", ".join(st.session_state.used_words))

if __name__ == "__main__":
    main()
