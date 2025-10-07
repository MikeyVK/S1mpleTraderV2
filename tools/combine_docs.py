import os

def merge_markdown_files(input_folder, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(input_folder):
            if filename.endswith(".md"):
                file_path = os.path.join(input_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(f"# {filename}\n\n")  # optioneel: titel toevoegen
                    outfile.write(infile.read())
                    outfile.write("\n\n---\n\n")  # scheiding tussen bestanden

if __name__ == "__main__":
    input_folder = "./docs/system"       # vervang door jouw map
    output_file = "docs123.md" # naam van het resultaat
    merge_markdown_files(input_folder, output_file)
    print(f"Alle bestanden samengevoegd in: {output_file}")