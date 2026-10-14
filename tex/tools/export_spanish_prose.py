#!/usr/bin/env python3
"""Export the Spanish pilot as UTF-8 text locally, without compiling a PDF."""
import json
from pathlib import Path
import re
import subprocess

TEX = Path(__file__).resolve().parents[1]


def pandoc(text, source, target):
    return subprocess.check_output(
        ["pandoc", "--from=" + source, "--to=" + target, "--wrap=none"],
        input=text, text=True)


def compact(text):
    return re.sub(r"\s+", "", text)


# Explicit text equivalents for the pilot's two display equations.
# Exact matching prevents later mathematical edits from silently using stale text.
DISPLAY_MATH = {
    compact(r"""\begin{pmatrix}
\text{intensidad de la} \\
\text{fuerza de la gravedad}
\end{pmatrix}
= \frac{(\text{masa del objeto 1})\times(\text{masa del objeto 2})}
{(\text{distancia entre los objetos 1 y 2})^{2}}"""):
        "Intensidad de la fuerza de la gravedad = (masa del objeto 1) × (masa del objeto 2) / (distancia entre los objetos 1 y 2)²",
    compact(r"""\begin{equation}\label{eq:02-01}
{\overrightarrow{F}}_{grav} = \  - \ G\frac{M_{1}M_{2}}{r^{2}}\left( \frac{\overrightarrow{r}}{r} \right)
\end{equation}"""):
        "F⃗_grav = −G (M₁ M₂ / r²) (r⃗ / r)    (2.1)",
}

CHAPTER03_MATH = {
    compact(r'\begin{pmatrix}\text{la gravedad es la manifestación} \\ \text{de la curvatura del espaciotiempo}\end{pmatrix}'):
        'La gravedad es la manifestación de la curvatura del espaciotiempo',
    compact(r'E = m\textcolor{gray}{c^{2}}'): 'E = mc²',
    compact(r'G_{\mu\upsilon} = \textcolor{gray}{\left( \frac{8\pi G}{c^{4}} \right)}T_{\mu\upsilon\ \ }'):
        'Gμυ = (8πG / c⁴) Tμυ',
    compact(r'(\text{tensor de Einstein}) = (\text{tensor de energía-momento})'):
        '(tensor de Einstein) = (tensor de energía-momento)',
    compact(r'(\text{geometría-curvatura}) = (\text{masa-energía})'):
        '(geometría-curvatura) = (masa-energía)',
}

CHAPTER04_MATH = {
    compact(r'''\begin{gathered}
\begin{pmatrix}\text{intensidad relativa de la} \\ \text{curvatura del espaciotiempo}\end{pmatrix}
\sim \left(\textcolor{gray}{\frac{G}{c^{2}}}\frac{M}{R}\right) \\
= \frac{(\text{masa de un objeto})}{(\text{tamaño de un objeto})}
\end{gathered}'''):
        'Intensidad relativa de la curvatura del espaciotiempo ∼ (G/c²)(M/R) = (masa de un objeto)/(tamaño de un objeto)',
    compact(r'''\begin{gathered}
\left(\textcolor{gray}{\frac{G}{c^{2}}}\frac{M_{\oplus}}{R_{\oplus}}\right)
\approx \left(\textcolor{gray}{\frac{G}{c^{2}}}\right)\frac{5{,}97\times 10^{24}\ \mathrm{kg}}{6372\ \mathrm{km}} \\
\approx 7\times 10^{-10}=0{,}0000000007
\end{gathered}'''):
        '(G/c²)(M⊕/R⊕) ≈ (G/c²)(5,97 × 10²⁴ kg / 6372 km) ≈ 7 × 10⁻¹⁰ = 0,0000000007',
    compact(r'''\begin{gathered}
\left(\textcolor{gray}{\frac{G}{c^{2}}}\frac{M_{\odot}}{R_{\odot}}\right)
\approx \left(\textcolor{gray}{\frac{G}{c^{2}}}\right)\frac{1{,}98\times 10^{30}\ \mathrm{kg}}{695\,000\ \mathrm{km}} \\
\approx 2\times 10^{-6}=0{,}000002
\end{gathered}'''):
        '(G/c²)(M☉/R☉) ≈ (G/c²)(1,98 × 10³⁰ kg / 695 000 km) ≈ 2 × 10⁻⁶ = 0,000002',
    compact(r'\begin{array}{@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}} R_{\odot}\cong15\ \mathrm{km} & R_{\odot}\cong7.5\ \mathrm{km} & R_{\odot}\cong5\ \mathrm{km}\end{array}'):
        'R☉ ≅ 15 km; R☉ ≅ 7.5 km; R☉ ≅ 5 km',
    compact(r'\begin{array}{@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}} M/R\cong0.1 & M/R\cong0.2 & M/R\cong0.3\end{array}'):
        'M/R ≅ 0.1; M/R ≅ 0.2; M/R ≅ 0.3',
}


CHAPTER06_MATH = {
    compact(r'r_{S}=2M\textcolor{gray}{\frac{G}{c^{2}}}'): 'rₛ = 2MG/c²',
    compact(r'v_{f}=\sqrt{2\frac{M}{R}\textcolor{gray}{G}}'): 'v_f = √(2MG/R)',
    compact(r'\textcolor{gray}{\frac{G}{c^{2}}}\frac{M_{\star}}{R_{\star}}\leq\frac{4}{9}'): '(G/c²)(M★/R★) ≤ 4/9',
    compact(r'\begin{array}{@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}}\text{Sol} & \text{estrella ultracompacta} & \text{agujero negro}\end{array}'): 'Sol; estrella ultracompacta; agujero negro',
    compact(r'\begin{array}{@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}w{c}{0.2933\linewidth}@{}}M/R\cong0{,}000002 & M/R\cong0{,}444 & M/R=0{,}5\end{array}'): 'M/R ≅ 0,000002; M/R ≅ 0,444; M/R = 0,5',
}


CHAPTER07_MATH = {
    compact(r'\begin{equation}\label{eq:07-01}\begin{pmatrix}\text{resolución angular de la} \\ \text{imagen astronómica}\end{pmatrix}=\left(\frac{\text{longitud de onda de las observaciones}}{\text{tamaño del telescopio}}\right)\end{equation}'):
        'Resolución angular de la imagen astronómica = longitud de onda de las observaciones / tamaño del telescopio    (7.1)',
}
DISPLAY_MATH.update(CHAPTER07_MATH)



CHAPTER08_MATH = {
    compact(r'\square'): '□',
    compact(r'\simeq \ '): '≃',
    compact(r'\phi'): 'φ',
    compact(r'\ \square\ \phi\  = \ 0'): '□φ = 0',
    compact(r'\square\  = \partial_{t}^{2} - v^{2}(\partial_{x}^{2} + \partial_{y}^{2} + \partial_{z}^{2})'): '□ = ∂ₜ² − v²(∂ₓ² + ∂ᵧ² + ∂_z²)',
    compact(r'v'): 'v',
    compact(r'\begin{equation}\label{eq:08-01}L_{GW} \simeq \textcolor{gray}{Gc}\left( \frac{M}{R} \right)^{2}\left( \frac{v}{v} \right)^{6} \simeq \textcolor{gray}{\frac{c^{5}}{G}}\left( \frac{r_{s}}{R} \right)^{2}\left( \frac{v}{v} \right)^{6}\end{equation}'):
        'L_GW ≃ Gc(M/R)²(v/v)⁶ ≃ (c⁵/G)(rₛ/R)²(v/v)⁶    (8.1)',
    compact(r'\begin{equation}\tag{8.1}\label{eq:08-01-repeat}L_{GW} \simeq \frac{c^{5}}{G}\textcolor{gray}{\left( \frac{r_{s}}{R} \right)^{2}\left( \frac{v}{v} \right)^{6}\ }\end{equation}'):
        'L_GW ≃ (c⁵/G)(rₛ/R)²(v/v)⁶    (8.1)',
    compact(r'\begin{equation}\label{eq:08-02}L_{GW}\sim\frac{c^{5}}{G}\sim 3{,}6 \times 10^{48}\ \mathrm{vatios}\end{equation}'):
        'L_GW ∼ c⁵/G ∼ 3,6 × 10⁴⁸ vatios    (8.2)',
}
DISPLAY_MATH.update(CHAPTER08_MATH)


def figure_math(node):
    """Preserve Word's external formula labels around figure 4.2."""
    if isinstance(node, list):
        return [item for child in node for item in figure_math(child)]
    if isinstance(node, dict):
        if node.get('t') == 'Math':
            return [{'t': 'Para', 'c': [clean(node)]}]
        return figure_math(node.get('c', []))
    return []


def clean(node):
    if isinstance(node, list):
        return [clean(item) for item in node]
    if not isinstance(node, dict):
        return node
    if node.get("t") == "Figure":
        attr, caption, body = node["c"]
        chapter, number = re.fullmatch(r"fig:(\d+)-(\d+)", attr[0]).groups()
        title = {"t": "Para", "c": [{"t": "Str", "c": f"Figura {int(chapter)}.{int(number)}."}]}
        external = [{"t": "Para", "c": [{"t": "Str", "c": "sin rotación"}]}] if attr[0] == "fig:07-03" else []
        return {"t": "Div", "c": [["", [], []], [title] + external + figure_math(body) + clean(caption[1])]}
    if node.get("t") == "Math" and node["c"][0]["t"] == "InlineMath":
        reviewed = {**CHAPTER08_MATH, compact(r'\sqrt{27}'): '√27', compact(r'\sqrt{27} \simeq 5{,}2'): '√27 ≃ 5,2'}
        expression = compact(node["c"][1])
        if expression in reviewed:
            return {"t": "Str", "c": reviewed[expression]}
    if node.get("t") == "Math" and node["c"][0]["t"] == "DisplayMath":
        expression = compact(node["c"][1])
        label06 = re.search(r'\\label\{eq:06-(\d+)\}', expression)
        body06 = re.sub(r'\\(?:begin|end)\{equation\}|\\label\{eq:06-\d+\}', '', expression)
        if body06 in CHAPTER06_MATH:
            suffix = f'    (6.{int(label06[1])})' if label06 else ''
            return {"t": "Str", "c": CHAPTER06_MATH[body06] + suffix}
        label04 = re.search(r'\\label\{eq:04-(\d+)\}', expression)
        body04 = re.sub(r'\\(?:begin|end)\{equation\}|\\label\{eq:04-\d+\}', '', expression)
        if body04 in CHAPTER04_MATH:
            suffix = f'    (4.{int(label04[1])})' if label04 else ''
            return {"t": "Str", "c": CHAPTER04_MATH[body04] + suffix}
        label = re.search(r'\\label\{eq:03-(\d+)\}', expression)
        body = re.sub(r'\\(?:begin|end)\{equation\}|\\label\{eq:03-\d+\}', '', expression)
        if body in CHAPTER03_MATH:
            suffix = f'    (3.{int(label[1])})' if label else ''
            return {"t": "Str", "c": CHAPTER03_MATH[body] + suffix}
        if expression not in DISPLAY_MATH:
            raise ValueError("Add a reviewed plain-text equivalent for this display equation: " + node["c"][1])
        return {"t": "Str", "c": DISPLAY_MATH[expression]}
    if node.get("t") == "Div" and re.fullmatch(r"note:\d+-\d+", node["c"][0][0]):
        number = int(node["c"][0][0].rsplit("-", 1)[1])
        title = {"t": "Para", "c": [{"t": "Str", "c": f"{number}."}]}
        return {"t": "Div", "c": [["", [], []], [title] + clean(node["c"][1])]}
    return {key: clean(value) for key, value in node.items()}


def main():
    output = TEX / "build/prose/spanish"
    output.mkdir(parents=True, exist_ok=True)
    chapters = []
    sources = sorted((TEX / 'spanish').glob('ch[0-9][0-9].tex'))
    for source in sources:
        chapter = source.stem[2:]
        text = (TEX / f"spanish/ch{chapter}.tex").read_text()
        text += "\n\\section*{Notas}\n" + (TEX / f"spanish/notes/ch{chapter}.tex").read_text()
        # Preserve book numbering independently of Pandoc's standalone counters.
        text = re.sub(r"\\(eqref|ref)\{(?:eq|fig):(\d+)-(\d+)\}",
                      lambda m: ("(" if m[1] == "eqref" else "") +
                      f"{int(m[2])}.{int(m[3])}" + ( ")" if m[1] == "eqref" else ""), text)
        # Resolve the comparison table relative to tex/, regardless of caller cwd.
        text = re.sub(r"\\input\{(spanish/tables/[^}]+)\}",
                      lambda m: (TEX / (m[1] + ".tex")).read_text(), text)
        document = clean(json.loads(pandoc(text, "latex", "json")))
        plain = pandoc(json.dumps(document), "json", "plain")
        if "\\" in plain or "DOCX paragraph" in plain or re.search(r"\[(?:eq|fig|note):", plain):
            raise ValueError("Unrendered source markup remains in chapter " + chapter)
        path = output / f"ch{chapter}.txt"
        path.write_text(plain, encoding="utf-8")
        chapters.append(plain)
        print(f"{path.relative_to(TEX)}: {len(plain.split())} words, {path.stat().st_size} bytes")
    (output / "chapters01-02.txt").write_text("\n\n".join(chapters[:2]), encoding="utf-8")
    (output / "all-chapters.txt").write_text("\n\n".join(chapters), encoding="utf-8")
    supporting = []
    for name in ('introduction', 'conclusion', 'acknowledgements'):
        source = TEX / 'spanish' / (name + '.tex')
        if not source.exists():
            continue
        document = clean(json.loads(pandoc(source.read_text(), 'latex', 'json')))
        plain = pandoc(json.dumps(document), 'json', 'plain')
        if "\\" in plain or 'DOCX paragraph' in plain:
            raise ValueError('Unrendered source markup remains in ' + name)
        (output / (name + '.txt')).write_text(plain, encoding='utf-8')
        supporting.append(plain)
        print(f'build/prose/spanish/{name}.txt: {len(plain.split())} words')
    (output / 'supporting.txt').write_text('\n\n'.join(supporting), encoding='utf-8')
    frontmatter = TEX / 'spanish/frontmatter.tex'
    if frontmatter.exists():
        document = clean(json.loads(pandoc(frontmatter.read_text(), 'latex', 'json')))
        plain = pandoc(json.dumps(document), 'json', 'plain')
        (output / 'frontmatter.txt').write_text(plain, encoding='utf-8')



if __name__ == "__main__":
    main()
