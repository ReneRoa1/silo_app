import os

def convert_to_utf8(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="latin-1") as f:
                        content = f.read()
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Convertido: {path}")
                except Exception as e:
                    print(f"Erro em {path}: {e}")

convert_to_utf8(".")
