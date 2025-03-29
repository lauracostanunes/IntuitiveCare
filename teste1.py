import os
import shutil

import requests


def download_pdf(url, filename):
    folder = "downloads"
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Download concluído: {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o PDF: {e}")


pdf_url_1 = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos/Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"  # Substitua pela URL desejada
pdf_filename_1 = "anexo 1.pdf"
download_pdf(pdf_url_1, pdf_filename_1)

pdf_url_2 = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos/Anexo_II_DUT_2021_RN_465.2021_RN628.2025_RN629.2025.pdf"  # Segunda URL do PDF
pdf_filename_2 = "anexo 2.pdf"
download_pdf(pdf_url_2, pdf_filename_2)

zip_filename = "downloads.zip"
shutil.make_archive("downloads", 'zip', "downloads")
print(f"Arquivo ZIP criado: {zip_filename}")
