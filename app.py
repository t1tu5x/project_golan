import streamlit as st
import pandas as pd
import os

DATA_DIR = "data"

# Порядок групп с эмодзи
GROUP_KEYS_ORDER = [
    "grains_and_pasta", "baked_vegetables", "potato_dishes", "fish_dishes",
    "chicken_dishes", "meat_dishes", "fried_snacks", "stuffed_vegetables",
    "fish_dishes", "baked_vegetables", "fish_dishes", "soups", "soups",
    "grains_and_pasta", "grains_and_pasta",
    "meat_dishes", "meat_special", "meat_special"
]

GROUP_LABELS_HE = {
    "grains_and_pasta": "🍝 דגנים ופסטה",
    "baked_vegetables": "🍠 ירקות אפויים",
    "potato_dishes": "🥔 מנות מתפוחי אדמה",
    "fish_dishes": "🐟 מנות דגים",
    "chicken_dishes": "🍗 מנות עוף",
    "meat_dishes": "🥩 מנות בשר",
    "fried_snacks": "🍟 נשנושים מטוגנים",
    "stuffed_vegetables": "🍆 ירקות ממולאים",
    "soups": "🍲 מרקים",
    "meat_special": "🧤 מיוחד בשר"
}

REQUIRED_COLUMNS = [
    "id", "dish_name_hebrew", "ingredients",
    "gross_yield_per_person", "gross_yield_per_gn1_1",
    "preparation_method", "notes"
]

@st.cache_data
def load_group_csv(group_key):
    path = os.path.join(DATA_DIR, f"{group_key}.csv")
    if not os.path.exists(path):
        st.warning(f"Файл не найден: {path}")
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"В файле {path} отсутствуют колонки: {missing}")
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    return df

def main():
    st.set_page_config(page_title="🏨 מלון גולן | Планировщик меню", layout="wide")
    st.title("🏨 מלון גולן | Планировщик меню")

    st.markdown("Выберите блюда из каждой категории (оставьте прочерк, если не хотите выбирать).")

    # Загружаем данные
    group_data = {}
    for key in set(GROUP_KEYS_ORDER):
        group_data[key] = load_group_csv(key)

    selected_dishes = {}

    break_lines_after = {4, 8, 15}
    for idx, group_key in enumerate(GROUP_KEYS_ORDER, start=1):
        df = group_data.get(group_key, pd.DataFrame(columns=REQUIRED_COLUMNS))
        options = ["-"] + df["dish_name_hebrew"].dropna().tolist()
        label = f"{idx:02d}. {GROUP_LABELS_HE.get(group_key, group_key)}"
        selected = st.selectbox(label, options, key=f"group_{idx}", index=0)
        selected_dishes[group_key + f"_{idx}"] = selected

        if idx in break_lines_after:
            st.markdown("---")

    if st.button("🧾 Сформировать меню"):
        chosen = []
        for key, dish in selected_dishes.items():
            if dish == "-" or dish == "":
                continue
            group_key = "_".join(key.split("_")[:-1])
            df = group_data.get(group_key, pd.DataFrame(columns=REQUIRED_COLUMNS))
            row = df.loc[df["dish_name_hebrew"] == dish]
            note = ""
            if not row.empty and "notes" in row.columns:
                note = row.iloc[0]["notes"] if pd.notna(row.iloc[0]["notes"]) else ""
            chosen.append({"№": len(chosen) + 1, "Блюдо": dish, "Примечание": note})

        if len(chosen) == 0:
            st.info("Ничего не выбрано.")
        else:
            st.table(pd.DataFrame(chosen))

if __name__ == "__main__":
    main()
