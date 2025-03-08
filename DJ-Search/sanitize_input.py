import json
import argparse

def extract_custom_fields(input_data):
    """
    Extracts custom fields ("text" for now) from each object in a JSON array.
    """
    output_data = [{"text": item.get("text")} for item in input_data if isinstance(item, dict) and "text" in item]
    return output_data

def main():
    parser = argparse.ArgumentParser(description="Extract 'text' fields from a JSON file.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("output_file", help="Path to the output JSON file.")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as infile:
            input_data = json.load(infile)

        output_data = extract_custom_fields(input_data)

        with open(args.output_file, "w") as outfile:
            json.dump(output_data, outfile, indent=4)

        print(f"Extracted 'text' fields and saved to {args.output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in input file '{args.input_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()