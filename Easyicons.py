import os
import re

ROOT = r"C:\Users\ArntV\OneDrive - De Lage Landen International B.V\Desktop\GDS\Interface Essentials\test"  # <<< ALTERE AQUI

def clean_svg_whitespace(svg_content):
    """
    Removes unnecessary new lines and spaces between SVG tags,
    without changing spaces inside d="..." path data.
    """
    svg_content = re.sub(r">\s+<", "><", svg_content)
    svg_content = re.sub(r"\s{2,}", " ", svg_content)
    return svg_content.strip()

def merge_path_d_values(svg_content):
    """
    Merge all <path d="..."/> elements inside each <g> into one single <path>.
    Keeps the attributes from the first path, replacing only its d value.
    """

    group_pattern = re.compile(r"(<g\b[^>]*>)(.*?)(</g>)", flags=re.DOTALL)
    path_pattern = re.compile(r"<path\b(?P<attrs>[^>]*)\s*/>", flags=re.DOTALL)

    def merge_group(match):
        group_open = match.group(1)
        group_content = match.group(2)
        group_close = match.group(3)

        paths = list(path_pattern.finditer(group_content))

        # Nothing to merge
        if len(paths) <= 1:
            return match.group(0)

        d_values = []

        for path_match in paths:
            attrs = path_match.group("attrs")
            d_match = re.search(r'\sd=(["\'])(.*?)\1', attrs, flags=re.DOTALL)

            if d_match:
                d_values.append(d_match.group(2).strip())

        # If no d values were found, do nothing
        if not d_values:
            return match.group(0)

        combined_d = " ".join(d_values)

        # Use attributes from the first path
        first_attrs = paths[0].group("attrs")

        # Remove the original d attribute from first path attrs
        attrs_without_d = re.sub(
            r'\sd=(["\']).*?\1',
            "",
            first_attrs,
            count=1,
            flags=re.DOTALL
        ).strip()

        # Create the new merged path
        if attrs_without_d:
            merged_path = f'<path d="{combined_d}" {attrs_without_d}/>'
        else:
            merged_path = f'<path d="{combined_d}"/>'

        # Rebuild group content:
        # keep everything except the old path tags, inserting only the merged path
        new_group_content = []
        last_end = 0
        inserted = False

        for path_match in paths:
            new_group_content.append(group_content[last_end:path_match.start()])

            if not inserted:
                new_group_content.append(merged_path)
                inserted = True

            last_end = path_match.end()

        new_group_content.append(group_content[last_end:])

        return group_open + "".join(new_group_content) + group_close

    return group_pattern.sub(merge_group, svg_content)


def process_svg(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # --- PRIMEIRO BLOCO: substituições no arquivo original ---
    content_mod = content.replace(
        "Streamline Icon: https://streamlinehq.com", "").replace("--Streamline-Core", "").replace("black","#006BB2").replace('width="14" height="14"',"").replace('<rect width="14" height="14" fill="white"/>', '')
    # último comando: remover bloco <defs>...</defs>
    content_mod = re.sub(r"<defs>.*?</defs>", "", content_mod, flags=re.DOTALL)

    match_svg = re.search(r"<svg[^>]*>", content_mod)
    # Encontrar a tag <svg ...>

    if match_svg:
    # Conteúdo logo após <svg>
        after_svg = content_mod[match_svg.end():].lstrip()

        # Se NÃO começar com <g>, inserir <g> e </g>
        if not after_svg.startswith("<g"):
            # Inserir <g> após <svg>
            content_mod = (
                content_mod[:match_svg.end()] +
                "\n<g>" +
                content_mod[match_svg.end():]
            )

            # Inserir </g> antes de </svg>
            content_mod = re.sub(r"</svg>", "</g>\n</svg>", content_mod, count=1)


    # Salva alterações no arquivo original
    with open(path, "w", encoding="utf-8") as f:
        f.write(content_mod)

    
    # gerar novo arquivo transformado ---
    filename = os.path.basename(path)
    name_no_ext = os.path.splitext(filename)[0]

    new_content = content_mod

    # Substituir viewBox 14x14 → 16x16
    new_content = new_content.replace(
        'viewBox="0 0 14 14"',
        'viewBox="0 0 16 16"'
    )

    # Substituir <g por <g transform="translate(1 1)"
    new_content = new_content.replace(
        "<g",
        '<g transform="translate(1 1)"'
    )
    

    # Substituir conteúdo do <desc>
    desc_pattern = r"<desc>.*?</desc>"
    new_desc = f"<desc>Flattern, Size= 16px Weight: Regular • {name_no_ext} • Icons • Visual Assets • GDS</desc>"
    new_content = re.sub(desc_pattern, new_desc, new_content, flags=re.DOTALL)
        # Juntar todos os valores d="..." dos paths em um único <path>
    new_content = merge_path_d_values(new_content)
    # Remover quebras de linha e espaços desnecessários
    new_content = clean_svg_whitespace(new_content)

    new_content = new_content.replace('<rect fill="white"/>','')

    # Nome do novo arquivo
    new_filename = f"{name_no_ext}.Size=16,Weight=Regular.svg"
    new_path = os.path.join(os.path.dirname(path), new_filename)

    # Salvar novo arquivo
    with open(new_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    #Exclui arquivo original
    os.remove(path)

def walk_and_process(root):
    for folder, _, files in os.walk(root):
        for file in files:
            if file.lower().endswith(".svg"):
                full_path = os.path.join(folder, file)
                print(f"Processando: {full_path}")
                process_svg(full_path)
              

walk_and_process(ROOT)
