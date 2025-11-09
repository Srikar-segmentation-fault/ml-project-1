import streamlit as st
import pickle
import requests
import os
from dotenv import load_dotenv
from functools import lru_cache

# -------------------- LOAD ENV VARIABLES --------------------
load_dotenv()
TMDB_TOKEN = os.getenv("TMDB_TOKEN")

if not TMDB_TOKEN:
    st.warning("⚠️ TMDB_TOKEN not found in environment variables.")

# -------------------- LOAD MODEL AND DATA --------------------
new = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


# -------------------- HELPER FUNCTIONS --------------------
def get_movie_from_dataset(user_input: str):
    """Find a close match from dataset for given user input."""
    matches = new[new["title"].str.lower().str.contains(user_input.lower())]
    if matches.empty:
        return None
    return matches.iloc[0]["title"]  # best match


@lru_cache(maxsize=200)
def get_poster_url(movie_name: str):
    """Fetch poster image URL for given movie name using TMDB API."""
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}"}
    search_url = f"https://api.themoviedb.org/3/search/movie"
    params = {"query": movie_name}

    try:
        response = requests.get(search_url, headers=headers, params=params)
        data = response.json()

        # No results found
        if "results" not in data or len(data["results"]) == 0:
            print(f"[DEBUG] No TMDB results for: {movie_name}")
            return "https://via.placeholder.com/300x450?text=No+Image"

        movie_data = data["results"][0]

        # Direct poster path
        if movie_data.get("poster_path"):
            return f"https://image.tmdb.org/t/p/w500{movie_data['poster_path']}"

        # Try alternative image fetch by movie ID
        movie_id = movie_data.get("id")
        if movie_id:
            img_url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"
            img_data = requests.get(img_url, headers=headers).json()
            posters = img_data.get("posters", [])
            if posters:
                poster_path = posters[0].get("file_path")
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

        # If no image found at all
        return "https://via.placeholder.com/300x450?text=No+Image"

    except Exception as e:
        print(f"[ERROR fetching poster for {movie_name}] {e}")
        return "https://via.placeholder.com/300x450?text=No+Image"


def recommend(movie_input: str):
    """Generate top 5 similar movies and their posters."""
    movie = get_movie_from_dataset(movie_input)
    if not movie:
        return []

    movie_index = new[new["title"] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    for i in movies_list:
        title = new.iloc[i[0]].title
        poster_url = get_poster_url(title)
        recommended_movies.append((title, poster_url))
    return recommended_movies


# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎥 Movie Recommendation System")

st.write("Enter a movie name below to get top 5 similar movie recommendations with posters.")

movie_name = st.text_input("🎞️ Enter a movie name:")

if st.button("Get Recommendations"):
    if movie_name.strip():
        recommendations = recommend(movie_name.strip())

        if recommendations:
            st.success("✅ Here are your recommended movies:")
            cols = st.columns(5)
            for idx, (title, poster) in enumerate(recommendations):
                with cols[idx % 5]:
                    st.image(poster, use_container_width=True)
                    st.markdown(f"**{title}**", unsafe_allow_html=True)
        else:
            st.error("❌ Movie not found in dataset. Please check spelling or try another movie.")
    else:
        st.warning("⚠️ Please enter a movie name before clicking the button.")
