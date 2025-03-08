import json
import subprocess
import argparse
from tqdm import tqdm

def trim_to_n_words(text, n):
    """Trims a string to the first n words."""
    words = text.split()
    if len(words) > n:
        return " ".join(words[:n])
    else:
        return text

def remove_prompt_prefix(output, prompt):
    """Removes the prompt from the beginning of the output if it exists."""
    detect_txt_prompt = prompt
    common_instruction = "Please write a few paragraphs for a novel starting with the following prompt: "
    if detect_txt_prompt.startswith(common_instruction):
        detect_txt_prompt = prompt[len(common_instruction):]

    if output.startswith(detect_txt_prompt):
        return output[len(detect_txt_prompt):].strip() #remove the prompt
    else:
        return output #return original output
    
def preprocess_prompt(prompt):
    """Preprocesses the prompt for Ollama."""
    instruction = f"You are a creative writer who likes unconventional novels"
    # if prompt.startswith(instruction):
    #     prompt = prompt[len(instruction):]

    return f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>{instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>{prompt}<|eot_id|> <|start_header_id|>assistant<|end_header_id|>"


def process_json_with_ollama(input_file, output_file, n_words):
    """
    Reads a JSON file, extracts prompts, calls Ollama, and adds outputs to a new JSON.

    Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to the output JSON file.
        n_words (int): Number of words to trim the Ollama output to.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        output_data = []
        for item in tqdm(data, desc="Processing items"):
            if isinstance(item, dict) and "prompt" in item:
                prompt = item["prompt"]
                preprocessed_prompt = preprocess_prompt(prompt)
                try:
                    # Call Ollama using subprocess
                    result = subprocess.run(
                        ["ollama", "run", "llama3.2", preprocessed_prompt],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    ollama_output = result.stdout.strip()
                    ollama_output = remove_prompt_prefix(ollama_output, prompt)
                    trimmed_output = trim_to_n_words(ollama_output, n_words)
                    new_item = item.copy()
                    new_item["text"] = trimmed_output
                    output_data.append(new_item)

                except subprocess.CalledProcessError as e:
                    print(f"Error calling Ollama: {e}")
                    new_item = item.copy()
                    new_item["text"] = f"Ollama Error: {e.stderr.strip()}"
                    output_data.append(new_item)

                except FileNotFoundError:
                    print("Error: Ollama not found. Ensure it is installed and in your PATH.")
                    new_item = item.copy()
                    new_item["text"] = "Ollama Error: Ollama not found"
                    output_data.append(new_item)

                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    new_item = item.copy()
                    new_item["text"] = f"Error: {str(e)}"
                    output_data.append(new_item)
            else:
                print("Warning: Item missing 'prompt' field or is not a dictionary.")
                output_data.append(item)

            # Dump JSON after each prompt
            with open(output_file, 'w', encoding='utf-8') as outfile:
                json.dump(output_data, outfile, indent=4)

        print(f"Processed JSON and saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in input file '{input_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON with Ollama.")
    parser.add_argument("input_file", help="Path to the input JSON file.")
    parser.add_argument("output_file", help="Path to the output JSON file.")
    parser.add_argument("--n_words", type=int, default=100, help="Number of words to trim the Ollama output to.")
    args = parser.parse_args()

    process_json_with_ollama(args.input_file, args.output_file, args.n_words)