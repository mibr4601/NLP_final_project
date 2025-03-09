## Project Description


## DJ-Search Folder

This code build infrastructure around the DJ-Search algorithm. DJ-Search is used to evaluate the creativity of LLMs by quantifying their originality. Using a combination of a custom reference corpus and a memory-mapped similarity table, the algorithm assesses the novelty of text outputs from different LLMs. This allows for the comparison of creativity scores across various models and prompts. The approach is model-agnostic, providing a robust and deterministic assessment of linguistic creativity based on unique n-grams and their occurrence across a large reference corpus.

## Setup Instructions

To run this code, follow the steps below:

- Clone the DJ-Search repository: First, clone the repository and setup it at [GXimingLu/creativity_index.](https://github.com/GXimingLu/creativity_index/blob/main/README.md).

- Replace necessary files:
    - Replace `DJ_search_earth_mover.py` and `retrieve_documents.py` with the corresponding files provided in the zip.
    The `DJ_search_earth_mover.py` file has been modified to use a memory-mapped lookup table, which is loaded during initialization. You will need to specify the path to the similarity table in the code.
    The `retrieve_documents.py` file has been fully reworked to accommodate the new index structure, but the interface and usage remain consistent for compatibility.

- Elastic Cloud Access:
    - To run the algorithm from scratch, please contact me (Illia Voloshyn) with the desired input. The free tier of Elastic Cloud has some limits on public API keys, so I am unable to provide public access.
    Precomputed similarity tables are not included due to their large size (30 GB), which could cause issues with Gradescope. However, if necessary, the Elastic Cloud can be populated with the `put_data_to_es.ipynb` and similarity table can be generated from scratch using the `generate_lookup_table.ipynb script`.

- Install ollama

- Add environmental variables for huggingface and elastic cloud tokens

## Example Usage

Some example files are included in data folder as a reference for inputs and outputs. Please feel free to disregard them if not needed
Specifically,
- `Llama3_2_3B_no_instruct.json` aggregates interesting prompts and responses of Llama3.2 3B.
- `Llama3_2_3B_no_instruct_for_es.json` has extracted "text" field for running elastic search
- `Llama3_2_3B_no_instruct_for_es_result.json` contains the result of getting files from elastic cloud
- `Llama3_2_3B_no_instruct_filtered.json` has processed text
- `Llama3_2_3B_no_instruct_final.json` has final DJ-Search result
- `data/prompt/...` has results of running DJ-Search on engineered prompts specified in our Wiki page
- `llama.xslx` contains a part of our analysis on results

### Step 1: Put Your Dataset into Elastic Cloud

Use the `put_data_to_es.ipynb` interactive notebook to upload your dataset (or RedPajama by default) into your own Elastic Cloud instance.

### Step 2: Download and Prepare Model Weights

Select the desired model to test and obtain its weights (if the model is in a gated repository). Download the embedding layer for the model and use the `generate_lookup_table.ipynb` script to generate the similarity lookup table. Warning: This is a storage-costly operation, for example, models like Llama 3.2 3B will require around 30 GB of storage.

### Step 3: Create Prompts Dataset

Aggregate interesting prompts, including any relevant metadata, into a JSON file (`example.json`) with a "prompt" key and other desirable information.

### Step 4: Execute Prompts

Activate the virtual environment with `conda activate vllm` as specified in the original GitHub instructions, then run:
```
python execute_prompts.py path/to/example.json path/to/example_filled_with_response.json --n_words n_to_trim_model_responses
```
This command will generate a JSON file with the same structure as the input file, but with model responses trimmed to n_words. The script also removes the prompt from the model response if it appears at the beginning of the text. You will need ollama installed and the Llama 3.2 model available.

### Step 5: Sanitize Model Responses

Run the following script to extract the "text" fields from the model responses and format them for document retrieval:
```
python sanitize_input.py path/to/example_filled_with_response.json path/to/example_filled_with_response_for_es.json
```
### Step 6: Retrieve Relevant Documents

Now, use the retrieve_documents.py script to search for and retrieve  relevant documents from Elastic Cloud:
```
python retrieve_documents.py --output_dir outputs/example --input_file path/to/example_filled_with_response_for_es.json --nb_documents n_documents_to_retrieve_for_each_text --index_name sampled_redpajama --subset n_to_stop_retrieving_after_n_texts
```
### Step 7: Process Retrieved Documents

Activate the infini-gram environment with `conda activate infini-gram`, then process the retrieved documents:
```
python process_documents.py --task task_name --retrieved_data_path path/to/example_filled_with_response_for_es_result.json --data_output_dir outputs/filtered
```

### Step 8: Run DJ-Search Algorithm

Finally, run the DJ-Search algorithm to evaluate the creativity of the retrieved documents:
```
python DJ_search_earth_mover.py --task task_name --data_dir outputs/filtered --output_dir outputs/example
```
Note: Due to time constraints, the implementation does not support loading the similarity table from an arbitrary location. However, this is an easy enhancement for the future.

After the DJ-Search algorithm completes, convert the results into a CSV file for analysis:
```
python json_score_to_csv.py path/to/task_name.json path/to/output.csv
```
To generate csv file that can be loaded into excel and analyzed

## LLM-Based Evaluation Folder

### Code Files

#### pre_process_data.ipynb

This file generates in the gpt_writing_prompts dataset and regenerates the stories based on the prompts to take in an appropriate amount of stories. It then saves this dataset into a csv file. This is the first file to run and the only requirement is to include a Together_API_key as mentioned, otherwise it does not require any files to be in the same directory

#### metric.ipynb

This file takes in the previous file that has been saved, so ensure that those names are the same. Then, it takes that dataset and runs the questions on the dataset to get results with Reasoning, yes/no answers, the index of the text and the author of the text. Similar to above, it requires the Together_API_key, but it now additionally requires the file from the previous notebook file.

#### analysis.ipynb

This file takes in the dataset from the previous one and runs basic analysis on the individual dataset. In the future, this will also include statistical comparisons between multiple runs.
