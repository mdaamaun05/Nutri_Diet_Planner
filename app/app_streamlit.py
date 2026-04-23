import streamlit as st
from rag import answer_question
import asyncio  

st.set_page_config(page_title="NutriChef AI: Smart Recipe & Nutrition Assistant ⭐", layout="centered")
st.title("🍳 Smart Recipe Explorer: Ingredient-to-Table Cooking Assistant ⭐")

# Sample ingredient inputs
sample_ingredients = [
    "Egg, Onion",
    "Chicken, Garlic, Tomato",
    "Potato, Onion",
    "Paneer, Butter, Tomato",
    "Rice, Vegetables",
    "Egg, Cheese",
    "Tomato, Basil, Pasta",
    "Milk, Sugar, Rice",
    "Banana, Milk",
    "Bread, Egg, Milk"
]

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# Selectbox for sample ingredient queries
selected_input = st.selectbox(
    "Choose sample ingredients or type your own:",
    ["--Type your own--"] + sample_ingredients
)

# Show text input if user wants custom ingredients
if selected_input == "--Type your own--":
    user_input = st.text_input("Enter ingredients (comma separated):")
else:
    user_input = selected_input


# Ask button
if st.button("Suggest Recipe"):
    if not user_input.strip():
        st.warning("Please enter ingredients!")
    else:
        with st.spinner("Finding best recipe for you..."):
            # Slight prompt enhancement for better retrieval
            query = f"Suggest a recipe using these ingredients: {user_input}"
            answer = run_async(answer_question(query))

        st.success("🍽️ Recipe Suggestion:")
        st.write(answer)
