import os
import zipfile
import xml.etree.ElementTree as ET


def extract_text(pptx_path: str) -> list[str]:
    ns = {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    }
    texts: list[str] = []
    with zipfile.ZipFile(pptx_path) as zf:
        slide_files = sorted(
            [
                f
                for f in zf.namelist()
                if f.startswith("ppt/slides/slide") and f.endswith(".xml")
            ]
        )
        for slide in slide_files:
            xml_data = zf.read(slide)
            try:
                root = ET.fromstring(xml_data)
            except ET.ParseError:
                continue
            for node in root.findall(".//a:t", ns):
                if node.text:
                    texts.append(node.text.strip())
    return texts


def main() -> None:
    base = r"C:\Users\patthamawadi.t\Desktop\Basic Technical Drawing"
    files = [
        "เขียนแบบเทคนิค-06.pptx",
        "เขียนแบบเทคนิค-07.pptx",
        "เขียนแบบเทคนิค-08.pptx",
        "เขียนแบบเทคนิค-09.pptx",
        "เขียนแบบเทคนิค-10.pptx",
    ]

    for name in files:
        path = os.path.join(base, name)
        if not os.path.exists(path):
            print(f"Missing: {path}")
            continue
        out_path = os.path.join(base, name + ".txt")
        texts = extract_text(path)
        with open(out_path, "w", encoding="utf-8") as f:
            for line in texts:
                f.write(line + "\n")
        print(f"Extracted PPTX ({len(texts)} lines)")


if __name__ == "__main__":
    main()
