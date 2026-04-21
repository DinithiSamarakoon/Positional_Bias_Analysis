# NLP Project: Yelp Positional Bias Pipeline

This project builds a filtered Yelp dataset, creates positional variants of review concatenations, and runs summarization experiments using multiple LLM providers (Groq, OpenAI, Together.ai, Hugging Face, and Mock).

---

## Prerequisites

- Python 3.10+

Install dependencies:
```bash
pip install openai pandas numpy matplotlib python-dotenv groq requests nltk

Configure environment variables (optional based on provider):

# Groq
set GROQ_API_KEY=your_key_here

# OpenAI
set OPENAI_API_KEY=your_key_here

# Together.ai
set TOGETHER_API_KEY=your_key_here

# Hugging Face
set HF_TOKEN=your_token_here
Project Structure
PositionalBiasSummarization/
├── data/                         # (ignored - large files)
├── experiments/
│   ├── __init__.py
│   ├── evaluation.py
│   ├── model_client.py
│   ├── prompting.py
│   └── runner.py
├── analyze_yelp_reviews.py
├── create_positional_bias_dataset.py
├── create_positioned_concatenations.py
├── run_experiments.py
├── visualize_results.py
├── visualizations/
└── experiment_outputs/          # (ignored)
Executable Files and Commands

Run all commands from the project root folder.

1) Analyze businesses and review counts

File: analyze_yelp_reviews.py

Purpose:

Reads Yelp dataset JSON files
Computes review counts per business
Filters businesses with:
≥10 positive reviews (4–5★)
≥1 negative review (1–2★)
Outputs business_review_stats.csv

Command:

python analyze_yelp_reviews.py --business-file data/yelp_academic_dataset_business.json --review-file data/yelp_academic_dataset_review.json
2) Create positional-bias dataset

File: create_positional_bias_dataset.py

Purpose:

Filters eligible businesses
Samples reviews (default: 10 positive + 1 negative)
Creates positional_bias_dataset.csv

Command:

python create_positional_bias_dataset.py --business-limit 50

Optional:

python create_positional_bias_dataset.py --business-limit 100 --seed 42
3) Create positioned concatenations

File: create_positioned_concatenations.py

Purpose:
Creates 3 datasets with the negative review placed at:

Top
Middle
End

Outputs:

positional_bias_concatenated_top.csv
positional_bias_concatenated_middle.csv
positional_bias_concatenated_end.csv

Command:

python create_positioned_concatenations.py
4) Run summarization experiments

File: run_experiments.py

Purpose:

Runs summarization with different prompting strategies:
Baseline
Chain-of-Thought (CoT)
Prompt Repetition
Computes:
Minority Opinion Recall
Output Length
Latency
Position Sensitivity
Supported Providers
Provider	Example Model
mock	(no API needed)
groq	llama-3.1-8b-instant
openai	gpt-4o-mini
together	meta-llama models
huggingface	flan-t5
Commands

Test run (no API):

python run_experiments.py --provider mock --sample-size 10

Groq (recommended free option):

python run_experiments.py --provider groq --model llama-3.1-8b-instant --sample-size 20

OpenAI:

python run_experiments.py --provider openai --model gpt-4o-mini --sample-size 50
5) Generate visualizations

File: visualize_results.py

Purpose:
Generates graphs:

Recall by position
Output length
Latency
Summary tables

Command:

python visualize_results.py --model llama_3.1_8b --sample-size 5
Recommended End-to-End Workflow
# Step 1
python analyze_yelp_reviews.py

# Step 2
python create_positional_bias_dataset.py

# Step 3
python create_positioned_concatenations.py

# Step 4
python run_experiments.py --provider mock --sample-size 5

# Step 5
python run_experiments.py --provider groq --model llama-3.1-8b-instant --sample-size 20

# Step 6
python visualize_results.py --model llama_3.1_8b --sample-size 20
Outputs
business_review_stats.csv
positional_bias_dataset.csv
positional_bias_concatenated_top.csv
positional_bias_concatenated_middle.csv
positional_bias_concatenated_end.csv
experiment_outputs/experiment_logs_*.jsonl
experiment_outputs/experiment_detailed_*.csv
experiment_outputs/experiment_summary_*.csv
visualizations/{model_name}/*.png
Important Notes
Large dataset files (data/*.json) are not included due to size limits.
Download Yelp dataset separately and place inside data/ folder.
