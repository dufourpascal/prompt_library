import streamlit as st
# from streamlit_card import card
from st_copy_to_clipboard import st_copy_to_clipboard as clipboard
from streamlit_card import card

from db import get_engine, Prompt, Category, PromptCategoryLink
from sqlmodel import Session, select


# @st.cache_resource()
def create_enginge():
    return get_engine()

# @st.cache_data()
def get_session():
    engine = create_enginge()
    return Session(engine)

# @st.cache_data()
def get_categories() -> dict[str, int]:
    engine = create_enginge()
    with Session(engine) as session:
        statement = select(Category)
        categories = session.exec(statement).fetchall()
        categories_formatted = {category.name_en: category.id for category in categories}
        return categories_formatted


# @st.cache_data()
def get_prompts(category_id: int) -> list[(str, str, str)]:
    engine = create_enginge()
    with Session(engine) as session:
        statement = select(PromptCategoryLink, Prompt).join(Prompt).where(PromptCategoryLink.category_id == category_id)
        prompts = session.exec(statement).fetchall()
        prompts_formatted = [(prompt.Prompt.name_en, prompt.Prompt.description_en, prompt.Prompt.text_en) for prompt in prompts]
        return prompts_formatted


# @st.experimental_dialog("Copy your prompt", width="large")
def show_prompt(prompt_name, prompt_description, prompt_text):
    print("clicked", prompt_name)
    # st.subheader(prompt_name)
    # st.text(prompt_description)

    # with st.container(border=True):
    #     st.write(prompt_text)
    # clipboard(prompt_text, before_copy_label="Copy to clipboard", after_copy_label="Copied!")


def prompt_selected(prompt_name: str, prompt_description: str, prompt_text: str):
    # st.session_state.prompt_name = prompt_name
    # st.session_state.prompt_text = prompt_text
    show_prompt(prompt_name, prompt_description, prompt_text)


def init_session_state():
    if "prompt_name" not in st.session_state:
        st.session_state.prompt_name = None
    if "prompt_text" not in st.session_state:
        st.session_state.prompt_text = None

st.set_page_config(page_title="Prompt Library", layout="wide")

engine = create_enginge()

init_session_state()


# st.title("Prompt Library")

st.selectbox("Language", ["English", "German"])

st.write("Select the category")
categories = get_categories()

print(categories)
category_name = st.selectbox("Categories", categories.keys())
category_id = categories[category_name]

with st.container():
    st.write("Select a prompt")
    prompts = get_prompts(category_id)

    columns =  st.columns(3)
    col_idx = 0

    for prompt_name, prompt_description, prompt_text in prompts:
        with columns[col_idx]:
            col_idx = (col_idx + 1) % len(columns)

            card(
                prompt_name,
                prompt_description,
                on_click=lambda: show_prompt(prompt_name, prompt_description, prompt_text),
                key=prompt_name,
                styles={
                    "card": {
                        "width": "300px", 
                        "height": "200px", 
                        "border-radius": "10px",
                        "padding": "10px",
                        "margin": "10px",
                        "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                        "background-image": "linear-gradient(45deg, #fd7014, #fd8f47)",
                        ":hover": {
                            "background-image": "linear-gradient(45deg, #dc5802, #fd7014)",
                        },
                        "div": {
                            "background-color": "rgba(0,0,0,0)",

                        },
                    },
                    "text": {
                        "font-family": "sans-serif",
                        "font-size": "1.25em",
                    },
                    "title": {
                        "font-family": "sans-serif",
                        "font-size": "2em",
                    },
                }
                )

            # card_clicked = st.button(prompt_name)
                
            # print(card_clicked)
            # if card_clicked:
            #     print("card clicked", prompt_name)
            #     try:
            #         # show_prompt(prompt_name, prompt_description, prompt_text)
            #         print("CLICKED", prompt_name)
            #         st.rerun()
            #     except StreamlitAPIException as e:
            #         print("Ignoring exception from streamlit (cards causes dialog to reopen)")
