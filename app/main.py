import os
import argparse
from .outline_extractor import extract_outline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input PDF file or folder")
    parser.add_argument("--output", type=str, required=True, help="Output JSON file or folder")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    if os.path.isdir(input_path):
        os.makedirs(output_path, exist_ok=True)
        for filename in os.listdir(input_path):
            if filename.lower().endswith(".pdf"):
                in_pdf = os.path.join(input_path, filename)
                out_json = os.path.join(output_path, os.path.splitext(filename)[0] + ".json")
                result = extract_outline(in_pdf, filename)
                with open(out_json, "w", encoding="utf-8") as f:
                    import json
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Saved: {out_json}")
    else:
        filename = os.path.basename(input_path)
        result = extract_outline(input_path, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            import json
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved: {output_path}")
