import os
import random

# 📁 Zielordner
output_folder = "generated_dlls"
os.makedirs(output_folder, exist_ok=True)

# 🔤 Namensbestandteile für professionelle DLLs
prefixes = ["System", "Core", "Net", "Data", "UI", "Graphics", "Security", "Interop", "Runtime", "Service"]
suffixes = ["Helper", "Manager", "Engine", "Module", "Bridge", "Handler", "Provider", "Client", "Host", "Wrapper"]

# 🔄 DLLs generieren mit großem Inhalt
def generate_large_dlls(count=5):
    for _ in range(count):
        name = f"{random.choice(prefixes)}{random.choice(suffixes)}.dll"
        path = os.path.join(output_folder, name)

        # 📏 Zufällige Größe zwischen 2 MB und 10 MB
        size_mb = random.randint(2, 10)
        size_bytes = size_mb * 1024 * 1024

        # 🧵 Inhalt: Wiederholter Dummy-String
        filler = ("/* Dummy DLL content */\n" * 100).encode("utf-8")
        repetitions = size_bytes // len(filler)

        with open(path, "wb") as f:
            for _ in range(repetitions):
                f.write(filler)

        print(f"📦 DLL erstellt: {name} ({size_mb} MB)")

# ▶️ Ausführen
if __name__ == "__main__":
    generate_large_dlls()