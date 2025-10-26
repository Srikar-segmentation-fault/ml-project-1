import streamlit as st
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# Load data
new = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Recommend function
def recommend(movie):
    movie_index = new[new['title'] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = [new.iloc[i[0]].title for i in movies_list]
    return recommended_movies

# Streamlit UI
st.title("Movie Recommendation System")
user_input = st.text_input("Enter a movie name:")

if st.button("Get Recommendation"):
    if user_input:
        try:
            recommendations = recommend(user_input)
            st.success("Recommended Movies:")
            for m in recommendations:
                st.write(m)
        except IndexError:
            st.error("Movie not found! Please check spelling.")
    else:
        st.warning("Please enter a movie name!")
