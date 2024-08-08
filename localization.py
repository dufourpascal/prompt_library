import json
import warnings
import streamlit as st


class Localization:
    language = "en"
    default_language = "en"
    translations = ["de"]

    def __init__(self, language: str):
        self.language = language
        self.data = self._load_data()

    def get_languages(self):
        return self.default_language, *self.translations

    def _load_data(self):
        with open("localization.json") as f:
            return json.load(f)

    def _write_data(self):
        with open("localization.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def _add_text(self, text):
        self.data[text] = {self.default_language: text}
        for lang in self.translations:
            if lang not in self.data[text]:
                self.data[text][lang] = ""

    def translate(self, text: str):
        if text in self.data:
            translation = self.data[text][self.language]
            if len(translation) > 0:
                return translation
            else:
                return "NOT LOCALIZED" + text
        else:
            warnings.warn(f"No locaization for '{text}'")
            self._add_text(text)
            self._write_data()
            return text

def init_localization():
    if "language" not in st.session_state:
        st.session_state.language = "de"

    localization = Localization(st.session_state.language)
    _ = Localization(st.session_state.language).translate

    index = localization.get_languages().index(st.session_state.language)
    st.sidebar.selectbox(_("Language"), options=localization.get_languages(), index=index, key="language")
    return _
