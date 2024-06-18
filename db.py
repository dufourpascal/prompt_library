from sqlmodel import Field, SQLModel, create_engine, Relationship

from datetime import datetime

print("IMPORTING db.py")

class PromptCategoryLink(SQLModel, table=True):
    prompt_id: int | None = Field(default=None, foreign_key="prompt.id", primary_key=True)
    category_id: int | None = Field(default=None, foreign_key="category.id", primary_key=True)


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name_en: str
    name_de: str

    prompts: list["Prompt"] = Relationship(back_populates="categories", link_model=PromptCategoryLink)


class Prompt(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name_en: str
    name_de: str
    text_en: str
    text_de: str
    description_en: str
    description_de: str
    date_added: datetime = Field(default=datetime.now())

    categories: list["Category"] = Relationship(back_populates="prompts", link_model=PromptCategoryLink)





def get_engine():
    return create_engine("sqlite:///prompts.db", echo=False)
