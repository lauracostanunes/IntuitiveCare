import os
import pandas as pd
import pdfplumber
import zipfile
from datetime import datetime

LEGENDA_ABREVIACOES = {
    'OD': 'Odontológico',
    'AMB': 'Ambulatorial',
}


def encontrar_arquivo_pdf():
    locais_busca = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Documents"),
    ]

    for local in locais_busca:
        caminho = os.path.join(local, "anexo 1.pdf")
        if os.path.exists(caminho):
            return caminho

    print("Não encontrei 'anexo 1.pdf' nestes locais:")
    for local in locais_busca:
        print(f"- {local}")

    return input("\nCole o caminho completo do arquivo ou arraste o PDF aqui: ").strip('"')


def extrair_tabela(pdf_path):
    dados = []
    colunas = None

    with pdfplumber.open(pdf_path) as pdf:
        inicio, fim = 2, 180
        total_paginas = len(pdf.pages)

        if total_paginas < fim + 1:
            print(f"Aviso: O PDF tem apenas {total_paginas} páginas. Ajustando extração.")
            fim = total_paginas - 1

        print(f"\nExtraindo dados das páginas {inicio + 1} a {fim + 1}...")

        for pagina_num in range(inicio, fim + 1):
            pagina = pdf.pages[pagina_num]
            tabelas = pagina.extract_tables()

            if tabelas:
                for tabela in tabelas:
                    tabela_limpa = [
                        [str(celula).strip() if celula is not None else ""
                         for celula in linha
                         if any(str(celula).strip())
                         ] for linha in tabela if any(linha)]

                    if pagina_num == inicio and not colunas:
                        for i, linha in enumerate(tabela_limpa):
                            if any("Código" in item or "Procedimento" in item for item in linha):
                                colunas = linha
                                dados.extend(tabela_limpa[i + 1:])
                                break
                        else:
                            dados.extend(tabela_limpa)
                    else:
                        dados.extend(tabela_limpa)

            if (pagina_num - inicio + 1) % 10 == 0:
                print(f"Progresso: {pagina_num - inicio + 1}/{fim - inicio + 1} páginas")

    if colunas and dados:
        df = pd.DataFrame(dados, columns=colunas)
    else:
        df = pd.DataFrame(dados)

    df = df.dropna(how='all').drop_duplicates().reset_index(drop=True)

    if not df.empty and len(df.columns) > 0:
        df = df[df[df.columns[0]].str.contains(r'^\d', na=False)]

    return df


def substituir_abreviacoes(df):
    colunas_para_verificar = [col for col in df.columns if isinstance(col, str)]

    for coluna in colunas_para_verificar:
        if df[coluna].dtype == object:
            for abreviacao, descricao in LEGENDA_ABREVIACOES.items():
                df[coluna] = df[coluna].str.replace(
                    rf'\b{abreviacao}\b',
                    descricao,
                    case=True,
                    regex=True
                )

    return df


def salvar_e_compactar(df):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_csv = f"procedimentos_saude_{timestamp}.csv"
    nome_zip = "Teste_Laura.zip"

    df.to_csv(nome_csv, index=False, encoding='utf-8-sig')
    print(f"\nArquivo CSV criado: {nome_csv}")

    with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(nome_csv)
        print(f"Arquivo ZIP criado: {nome_zip}")

    return nome_csv, nome_zip


def main():
    print("=== Extração e Tratamento de Dados de Saúde ===")

    caminho_pdf = encontrar_arquivo_pdf()

    if not os.path.exists(caminho_pdf):
        print(f"\nErro: Arquivo não encontrado - {caminho_pdf}")
        return

    print(f"\nArquivo encontrado: {caminho_pdf}")

    try:
        df = extrair_tabela(caminho_pdf)
    except Exception as e:
        print(f"\nErro na extração: {str(e)}")
        return

    if df.empty:
        print("\nNenhum dado foi extraído. Verifique:")
        print("- Se o PDF contém a tabela nas páginas 3-181")
        print("- Se o PDF não está protegido ou corrompido")
        return

    print("\nSubstituindo abreviações pelas descrições completas...")
    df = substituir_abreviacoes(df)

    arquivo_csv, arquivo_zip = salvar_e_compactar(df)

    print("\n" + "=" * 50)
    print("✅ Processo concluído com sucesso!")
    print(f"📄 Arquivo PDF processado: {os.path.basename(caminho_pdf)}")
    print(f"📊 Total de registros extraídos: {len(df):,}")
    print(f"🔄 Abreviações substituídas: {', '.join(LEGENDA_ABREVIACOES.keys())}")
    print(f"📁 Arquivo CSV gerado: {arquivo_csv}")
    print(f"🗜 Arquivo ZIP criado: {arquivo_zip}")

    print("\nAmostra dos dados com as substituições (3 primeiras linhas):")
    print(df.head(3).to_string(index=False))

    print("\nLegenda aplicada:")
    for abreviacao, descricao in LEGENDA_ABREVIACOES.items():
        print(f"- {abreviacao} = {descricao}")

    print(f"- Envie o arquivo '{arquivo_zip}' para Laura")
    print("- O CSV dentro do ZIP já está pronto para análise")


if __name__ == "__main__":
    try:
        import pdfplumber
        import pandas as pd
        import zipfile
    except ImportError:
        print("Instalando dependências necessárias...")
        import subprocess

        subprocess.run(["pip", "install", "pdfplumber", "pandas"], check=True)

    main()