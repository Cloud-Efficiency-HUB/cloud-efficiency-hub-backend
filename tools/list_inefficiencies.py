from pathlib import Path

def list_inefficiencies():
    hub_dir = Path("hub")
    for metadata_file in hub_dir.rglob("metadata.yaml"):
        print(f"Found inefficiency: {metadata_file.parent}")

if __name__ == "__main__":
    list_inefficiencies()
