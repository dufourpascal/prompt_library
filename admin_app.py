import streamlit as st
from time import sleep

from db import get_engine, Prompt, Category, PromptCategoryLink
from sqlmodel import Session, select, or_

def get_session():
    engine = get_engine()
    return Session(engine)


def get_prompts(filter: str):
    with get_session() as session:
        statement = (
            select(Prompt)
            .where(or_(
                Prompt.name_en.contains(filter),
                Prompt.name_de.contains(filter),
                Prompt.description_en.contains(filter),
                Prompt.description_de.contains(filter),
                Prompt.text_en.contains(filter),
                Prompt.text_de.contains(filter),
            )
        ))
        prompts = session.exec(statement).fetchall()

    return prompts


def get_prompt_by_id(prompt_id):
    with get_session() as session:
        statement = select(Prompt).where(Prompt.id == prompt_id)
        prompt = session.exec(statement).first()

    return prompt

def add_prompt():
    with get_session() as session:
        new_prompt = Prompt(
            name_en="New Prompt", name_de="Neuer Prompt",
            description_en="Description of the prompt", description_de="Beschreibung des Prompts",
            text_en="Enter English text here", text_de="Geben Sie hier den deutschen Text ein"
        )
        session.add(new_prompt)
        session.commit()

    toast = st.toast("Prompt added")
    sleep(1)
    toast.empty()
    st.rerun()

def delete_prompt(prompt_id):
    with get_session() as session:
        prompt = get_prompt_by_id(prompt_id)
        session.delete(prompt)
        session.commit()

    toast = st.toast("Prompt deleted")
    sleep(1)
    toast.empty()
    st.rerun()

def change_prompt_field(prompt_id, field):
    new_value = st.session_state[f"prompt_{prompt_id}_{field}"]
    prompt = get_prompt_by_id(prompt_id)
    setattr(prompt, field, new_value)
    with get_session() as session:
        session.add(prompt)
        session.commit()

    toast = st.toast(f"Prompt field {field} updated to {new_value}")
    sleep(1)
    toast.empty()

def change_prompt_categories(prompt_id):
    selected_categories = st.session_state[f"prompt_{prompt_id}_categories"]

    with get_session() as session:
        statement = select(Prompt).where(Prompt.id == prompt_id)
        prompt = session.exec(statement).one()

        categories = session.exec(select(Category)).fetchall()

        chosen_categories = []
        for category in categories:
            if category.name_en in selected_categories:
                chosen_categories.append(category)
        
        prompt.categories = chosen_categories

        session.add(prompt)
        session.commit()

    toast = st.toast("Prompt categories updated")
    sleep(1)
    toast.empty()

def get_categories():
    with get_session() as session:
        statement = select(Category)
        categories = session.exec(statement).fetchall()

    return categories

def get_category_by_id(category_id):
    with get_session() as session:
        statement = select(Category).where(Category.id == category_id)
        category = session.exec(statement).first()

    return category

def change_category_name(category_id, field):
    print(category_id, field, st.session_state[f"category_{category_id}_{field}"])
    new_value = st.session_state[f"category_{category_id}_{field}"]
    category = get_category_by_id(category_id)
    setattr(category, field, new_value)
    with get_session() as session:
        session.add(category)
        session.commit()

    toast = st.toast("Category name updated to " + new_value)
    sleep(1)
    toast.empty()

def delete_category(category_id):
    with get_session() as session:
        category = get_category_by_id(category_id)
        session.delete(category)
        session.commit()

    toast = st.toast("Category deleted")
    sleep(1)
    toast.empty()

def add_category():
    with get_session() as session:
        new_category = Category(name_en="New Category", name_de="Neue Kategorie")
        session.add(new_category)
        session.commit()
    toast = st.toast("Category added")
    sleep(1)
    toast.empty()
    st.rerun()


def show_categories():
    categories = get_categories()

    expander = st.expander("Categories", expanded=False)
    for category in categories:
        container = expander.container(border=True)
        col1, col2, col3 = container.columns(3)
        col1.text_input("name_en", category.name_en, key=f"category_{category.id}_name_en", on_change=change_category_name, args=(category.id, "name_en"))
        col2.text_input("name_de", category.name_de, key=f"category_{category.id}_name_de", on_change=change_category_name, args=(category.id, "name_de"))
        col3.button("Delete", key=f"button_delete_{category.id}", on_click=delete_category, args=(category.id,), type="primary")

    if st.button("Add Category", type="primary"):
        add_category()


def show_prompts():

    categories = get_categories()

    st.subheader("Prompts")
    if st.button("Add Prompt", type="primary"):
        add_prompt()

    filter = st.text_input("Filter")
    prompts = get_prompts(filter)

    for prompt in prompts:
        with st.popover(f"{prompt.name_en} - {prompt.description_en}", use_container_width=True):
            col1, col2 = st.columns(2)

            col1.text_input("name_en", prompt.name_en, key=f"prompt_{prompt.id}_name_en", on_change=change_prompt_field, args=(prompt.id, "name_en"))
            col2.text_input("name_de", prompt.name_de, key=f"prompt_{prompt.id}_name_de", on_change=change_prompt_field, args=(prompt.id, "name_de"))

            col1.text_input("description_en", prompt.description_en, key=f"prompt_{prompt.id}_description_en", on_change=change_prompt_field, args=(prompt.id, "description_en"))
            col2.text_input("description_de", prompt.description_de, key=f"prompt_{prompt.id}_description_de", on_change=change_prompt_field, args=(prompt.id, "description_de"))

            col1.text_area("text_en", prompt.text_en, height=300, key=f"prompt_{prompt.id}_text_en", on_change=change_prompt_field, args=(prompt.id, "text_en"))
            col2.text_area("text_de", prompt.text_de, height=300, key=f"prompt_{prompt.id}_text_de", on_change=change_prompt_field, args=(prompt.id, "text_de"))

            with get_session() as session:
                categories_prompt = session.exec(
                    select(Category)
                    .join(PromptCategoryLink)
                    .where(PromptCategoryLink.prompt_id == prompt.id)
                ).fetchall()
                # print(prompt.name_en, categories_prompt)
            st.multiselect(
                "Categories",
                options=[category.name_en for category in categories],
                default=[category.name_en for category in categories_prompt],
                key=f"prompt_{prompt.id}_categories",
                on_change=change_prompt_categories,
                args=(prompt.id,)
            )

            if st.button("Delete Prompt", key=f"delete_prompt_{prompt.id}", type="primary"):
                delete_prompt(prompt.id)


def main():
    st.set_page_config(page_title="Admin DB Interface", layout="wide")
    st.header("Admin DB Interface")

    show_categories()

    show_prompts()

if __name__ == "__main__":
    main()
