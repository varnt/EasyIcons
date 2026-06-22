import os
import re

ROOT = r"C:\caminho\da\pasta"  # <<< ALTERE AQUI

def process_svg(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # --- PRIMEIRO BLOCO: substituições no arquivo original ---
    content_mod = content.replace(
        "Streamline Icon: https://streamlinehq.com", ""
    ).replace(
        "--Streamline-Core", ""
    )

    # Salva alterações no arquivo original
    with open(path, "w", encoding="utf-8") as f:
        f.write(content_mod)

    # --- SEGUNDO BLOCO: gerar novo arquivo transformado ---
    filename = os.path.basename(path)
    name_no_ext = os.path.splitext(filename)[0]

    new_content = content_mod

    # Substituir viewBox 14x14 → 16x16
    new_content = new_content.replace(
        '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14"',
        '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 16"'
    )

    # Substituir <g por <g transform="translate(1 1)"
    new_content = new_content.replace(
        "<g",
        '<g transform="translate(1 1)"'
    )

    # Substituir conteúdo do <desc>
    desc_pattern = r"<desc>.*?</desc>"
    new_desc = f"<desc>Size= 16px Type: Regular • {name_no_ext} • Icons • Visual Assets • GDS</desc>"
    new_content = re.sub(desc_pattern, new_desc, new_content, flags=re.DOTALL)

    # Nome do novo arquivo
    new_filename = f"{name_no_ext}.Size=16,Type=Regular.svg"
    new_path = os.path.join(os.path.dirname(path), new_filename)

    # Salvar novo arquivo
    with open(new_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def walk_and_process(root):
    for folder, _, files in os.walk(root):
        for file in files:
            if file.lower().endswith(".svg"):
                full_path = os.path.join(folder, file)
                print(f"Processando: {full_path}")
                process_svg(full_path)


walk_and_process(ROOT)
