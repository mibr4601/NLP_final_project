import json
import csv
import argparse

def process_json_to_csv(input_file, output_file):
    """
    Parses JSON from an input file, extracts the first 5 words from the "text" field
    and the "coverage" score, and writes them to a CSV file.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['First 5 Words', 'Coverage Score'])  # Write header

            for item in data:
                if isinstance(item, dict) and "text" in item and "coverage" in item:
                    text = item["text"]
                    coverage = item["coverage"]
                    words = text.split()[:5]  # Get the first 5 words
                    first_5_words = ' '.join(words)
                    writer.writerow([first_5_words, coverage])

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in input file '{input_file}'.")
    except KeyError as e:
        print(f"Error: missing key in json file. Key: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse JSON and create CSV.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    args = parser.parse_args()

    process_json_to_csv(args.input_file, args.output_file)