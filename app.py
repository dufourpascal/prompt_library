import re
import streamlit as st
# from st_copy_to_clipboard import st_copy_to_clipboard as clipboard

from db import get_engine, Prompt, Category, PromptCategoryLink
from sqlmodel import Session, select

from localization import init_localization


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
        if st.session_state.language == "de":
            categories_formatted = {category.name_de: category.id for category in categories}
        else:
            categories_formatted = {category.name_en: category.id for category in categories}
        return categories_formatted

# @st.cache_data()
def get_prompts(category_id: int, filter: str = "") -> list[(str, str, str)]:
    engine = create_enginge()
    with Session(engine) as session:
        if category_id == 0:
            statement = select(Prompt).limit(200)
        else:
            statement = select(PromptCategoryLink, Prompt).join(Prompt).where(PromptCategoryLink.category_id == category_id).limit(200)

        prompts = session.exec(statement).fetchall()
        if len(prompts) and hasattr(prompts[0], "Prompt"):  # With join, the result has a Prompt attribute
            prompts = [prompt.Prompt for prompt in prompts]

        if st.session_state.language == "de":
            prompts_formatted = [(prompt.name_de, prompt.description_de, prompt.text_de) for prompt in prompts]
        else:
            prompts_formatted = [(prompt.name_en, prompt.description_en, prompt.text_en) for prompt in prompts]

        if filter:
            filter_lc = filter.lower()
            prompts_formatted = [prompt for prompt in prompts_formatted
                                 if filter_lc in prompt[0].lower()
                                 if filter_lc in prompt[0].lower()
                                 if filter_lc in prompt[0].lower()]
        return prompts_formatted


def get_variables(prompt):
    variables = {}

    matches = re.findall(r"\{(\w+)(?::\s*([^}]+))?\}", prompt)
    for match in matches:
        variable = match[0]
        values = match[1].split("|") if match[1] else []
        variables[variable] = values
    return variables

def has_variables(prompts):
    return len(get_variables(prompts)) > 0

def replace_variables(prompt_text, variables):
    pattern = r"\{(\w+)(?::\s*([^}]+))?\}"
    
    def replacer(match):
        variable = match.group(1)
        if variable in variables:
            variable_value = st.session_state.get(variable, "")
            if variable_value == "Other" or variable_value == "Andere":
                variable_value = st.session_state.get(variable+"_other", "")
            return variable_value
        else:
            return match.group(0)  # If no replacement is found, return the original match

    def replacer_formatted(match):
        variable = match.group(1)
        if variable in variables:
            variable_value = st.session_state.get(variable, "")
            if variable_value == "Other" or variable_value == "Andere":
                variable_value = st.session_state.get(variable+"_other", "")
            
            variable_value = f":orange-background[{variable_value}]"
            return variable_value
        else:
            return match.group(0)  # If no replacement is found, return the original match
    
    result = re.sub(pattern, replacer, prompt_text)
    result_formatted = re.sub(pattern, replacer_formatted, prompt_text)
    result_formatted = result_formatted.replace("\n", "  \n")
    return result, result_formatted


def show_variable_options(variables):
    for variable, values in variables.items():
        if len(values) > 0:
            label = variable.replace("_", " ").capitalize()
            other_value = "Other"
            value_selected = st.selectbox(label, [*values, other_value], key=variable)
            if value_selected == other_value:
                st.text_input(label, key=variable+"_other")
        else:
            st.text_input(variable, key=variable)

@st.dialog("Prompt", width="large", )
def show_prompt(prompt_name, prompt_description, prompt_text):
    st.subheader(prompt_name)
    st.write(prompt_description)

    if has_variables(prompt_text):
        variables = get_variables(prompt_text)
        show_variable_options(variables)
    else:
        variables = {}

    prompt_replaced, prompt_replaced_formatted = replace_variables(prompt_text, variables.keys())
    with st.container(border=True):
        st.markdown(prompt_replaced_formatted)

    # clipboard(prompt_replaced, before_copy_label=_t("Copy to clipboard"), after_copy_label=_t("Copied!"))

def init_session_state():
    if "prompt_name" not in st.session_state:
        st.session_state.prompt_name = None
    if "prompt_text" not in st.session_state:
        st.session_state.prompt_text = None
    if "category_id" not in st.session_state:
        st.session_state.category_id = 0
    if "filter" not in st.session_state:
        st.session_state.filter = ""

def select_category(category_id: int):
    st.session_state.category_id = category_id

st.set_page_config(page_title="Prompt Library", layout="wide")

engine = create_enginge()

init_session_state()
_t = init_localization()

def main():
    # language = st.selectbox("Language", ["English", "German"])
    # st.session_state.language = st.radio("Language", ["English", "German"])
    st.write(_t("Categories"))
    categories = get_categories()

    columns = st.columns(8)
    
    all_category_id = 0
    button_type = "primary" if all_category_id == st.session_state.category_id else "secondary"
    columns[0].button(_t("All"), type=button_type, on_click=select_category, args=(all_category_id,))

    col_idx = 1
    for category_name, category_id in categories.items():
        button_type = "primary" if category_id == st.session_state.category_id else "secondary"
        columns[col_idx].button(category_name, type=button_type, on_click=select_category, args=(category_id,))
        col_idx = (col_idx + 1) % len(columns)

    st.session_state.filter = st.text_input("Filter")

    with st.container():
        st.write(_t("Select a prompt"))
        prompts = get_prompts(st.session_state.category_id, st.session_state.filter)

        idx_tmp = 0
        for prompt_name, prompt_description, prompt_text in prompts:
            if st.button(f"**{prompt_name}**: {prompt_description}", key=prompt_name+str(idx_tmp)):
                show_prompt(prompt_name, prompt_description, prompt_text)
            idx_tmp += 1

if __name__ == "__main__":
    main()
