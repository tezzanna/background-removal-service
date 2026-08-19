import io
import os

import requests
import streamlit as st
from PIL import Image

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Удаление фона", page_icon="✂️", layout="wide")
st.title("✂️ Удаление фона с фото")


def show_image(image, caption: str | None = None) -> None:
    st.image(image, caption=caption, width=420)


uploaded_file = st.file_uploader(
    "Загрузите изображение (JPG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Исходное")
        show_image(uploaded_file)

    if st.button("Удалить фон", type="primary"):
        with st.spinner("Обрабатываю изображение..."):
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
            }
            try:
                response = requests.post(f"{API_URL}/remove-bg", files=files, timeout=60)
                response.raise_for_status()
            except requests.exceptions.ConnectionError:
                st.error(
                    "Не удалось подключиться к API. Убедитесь, что backend запущен "
                    f"и доступен по адресу {API_URL}."
                )
            except requests.exceptions.HTTPError:
                detail = response.json().get("detail", response.text)
                st.error(f"Ошибка API ({response.status_code}): {detail}")
            except requests.exceptions.Timeout:
                st.error("Сервер не ответил вовремя. Попробуйте изображение меньшего размера.")
            else:
                result_image = Image.open(io.BytesIO(response.content))
                with col2:
                    st.subheader("Результат")
                    show_image(result_image)

                st.download_button(
                    label="Скачать PNG",
                    data=response.content,
                    file_name=f"no_bg_{uploaded_file.name.rsplit('.', 1)[0]}.png",
                    mime="image/png",
                )
