import streamlit as st
import sqlite3
import random
import requests
from PyDictionary import PyDictionary
import time

# --- 1. DATABASE SETUP (CRUD Operations) ---
# Connecting to local SQLite database (Creates 'spelly.db' automatically)
conn = sqlite3.connect('spelly.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS words (word TEXT PRIMARY KEY)")
conn.commit()

# --- 2. WORD VALIDATION (Clean MIT List Download) ---
# Fetching the official 10,000 MIT word list and cleaning it up
@st.cache_data  # Keeps data cached so it doesn't re-download on every click
def load_words():
    try:
        response = requests.get("https://www.mit.edu/mecprice/wordlist.10000")
        raw_words = response.text.splitlines()
        
        clean_words = []
        for w in raw_words:
            word_clean = w.strip().lower()
            # GLITCH FIX: Only allow real words (no symbols, no spaces) between 3 and 10 characters
            if word_clean.isalpha() and 3 <= len(word_clean) <= 10:
                clean_words.append(word_clean)
                
        return clean_words
    except:
        # Fallback backup words in case of internet connection issues
        return ["apple", "elephant", "tiger", "rabbit", "turtle"]

valid_words = load_words()

# --- 3. SESSION STATE (Game Memory) ---
# Keeps track of scores and turns across page reloads
if 'used_words' not in st.session_state:
    st.session_state.used_words = []
if 'player_score' not in st.session_state:
    st.session_state.player_score = 0
if 'ai_score' not in st.session_state:
    st.session_state.ai_score = 0
if 'last_letter' not in st.session_state:
    st.session_state.last_letter = ""
if 'target_word' not in st.session_state:
    st.session_state.target_word = ""
if 'shuffled_word' not in st.session_state:
    st.session_state.shuffled_word = ""
if 'turn' not in st.session_state:
    st.session_state.turn = "Player"

# --- 4. MAIN GAME INTERFACE ---
st.title("🎮 Spelly Word Game")

# --- SIDEBAR: WORD MANAGEMENT (CRUD) ---
st.sidebar.header("Word Management (CRUD)")

# C - CREATE (Add Word)
new_word = st.sidebar.text_input("1. Add word to Database:")
if st.sidebar.button("Add Word"):
    if new_word:
        try:
            cursor.execute("INSERT INTO words (word) VALUES (?)", (new_word.lower(),))
            conn.commit()
            st.sidebar.success(f"'{new_word}' added successfully!")
        except:
            st.sidebar.warning("This word already exists in the database.")

# R - READ (View Words)
cursor.execute("SELECT word FROM words")
all_db_words = [row[0] for row in cursor.fetchall()]
st.sidebar.write("2. View Saved Words:", all_db_words)

# U - UPDATE (Modify Word)
st.sidebar.write("3. Modify/Update a Word:")
if all_db_words:
    word_to_edit = st.sidebar.selectbox("Select word to change:", all_db_words)
    updated_spelling = st.sidebar.text_input("Enter new spelling:")
    if st.sidebar.button("Update Word"):
        if updated_spelling:
            cursor.execute("UPDATE words SET word=? WHERE word=?", (updated_spelling.lower(), word_to_edit))
            conn.commit()
            st.sidebar.success(f"Word updated to '{updated_spelling}'!")
            st.rerun()

# D - DELETE (Remove Word)
delete_word = st.sidebar.text_input("4. Delete word from Database:")
if st.sidebar.button("Delete Word"):
    if delete_word:
        cursor.execute("DELETE FROM words WHERE word=?", (delete_word.lower(),))
        conn.commit()
        st.sidebar.error(f"'{delete_word}' deleted successfully!")
        st.rerun()


# --- MAIN SCREEN: SCORE & RULES ---
col1, col2 = st.columns(2)
col1.metric("Player Score", st.session_state.player_score)
col2.metric("AI Score", st.session_state.ai_score)

# Antakshari Rule Display
if st.session_state.last_letter:
    st.info(f"Rule: Next word MUST start with the letter **'{st.session_state.last_letter.upper()}'**")

# --- 5. GAME PLAY LOGIC ---

# A) PLAYER'S TURN
if st.session_state.turn == "Player":
    st.subheader("👨‍💼 Your Turn!")
    
    # Select a new word if there isn't an active target word
    if not st.session_state.target_word:
        available = [w for w in valid_words if w not in st.session_state.used_words]
        if st.session_state.last_letter:
            available = [w for w in available if w.startswith(st.session_state.last_letter)]
        
        if available:
            st.session_state.target_word = random.choice(available)
            # Shuffle the selected word's letters
            letters = list(st.session_state.target_word)
            random.shuffle(letters)
            st.session_state.shuffled_word = "".join(letters)
        else:
            st.error("Game Over! No words available matching the criteria.")
            st.stop()

    st.write(f"Unscramble and guess the correct spelling: **{st.session_state.shuffled_word.upper()}**")
    
    # Hint Button (Fetches meaning using PyDictionary)
    if st.button("💡 Get Hint"):
        dictionary = PyDictionary()
        meaning = dictionary.meaning(st.session_state.target_word)
        if meaning:
            for key in meaning:
                st.info(f"Hint (Meaning): {meaning[key][0]}")
                break
        else:
            st.info("No hint available for this word.")

    # Player Guess Input
    player_guess = st.text_input("Type your answer here:").strip().lower()
    if st.button("Submit Answer"):
        if player_guess == st.session_state.target_word:
            st.success("Correct Answer!")
            st.session_state.player_score += len(player_guess) # Score based on word length
            st.session_state.used_words.append(player_guess)   # Add to used list
            st.session_state.last_letter = player_guess[-1]   # Save the last letter
            st.session_state.target_word = ""                 # Clear target for next round
            st.session_state.turn = "AI"                      # Pass turn to AI
            time.sleep(1)
            st.rerun()
        else:
            st.error("Incorrect spelling! Please try again.")

# B) AI'S TURN (Computer Opponent)
else:
    st.subheader("🤖 Computer (AI) is thinking...")
    time.sleep(1.5)  # Simulated thinking delay
    
    available = [w for w in valid_words if w not in st.session_state.used_words]
    if st.session_state.last_letter:
        available = [w for w in available if w.startswith(st.session_state.last_letter)]
        
    if available:
        ai_word = random.choice(available)
        st.session_state.ai_score += len(ai_word)
        st.session_state.used_words.append(ai_word)
        st.session_state.last_letter = ai_word[-1]
        st.write(f"AI played the word: **{ai_word.upper()}**")
        st.session_state.turn = "Player"  # Pass turn back to player
        time.sleep(1.5)
        st.rerun()
    else:
        st.success("AI has no words left. You Win!")
        st.session_state.turn = "Player"

# Played Words History List
st.write("---")
st.write("**Played Words History:**", ", ".join(st.session_state.used_words))
