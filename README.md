# NLP Project: Yelp Positional Bias Pipeline

This project builds a filtered Yelp dataset, creates positional variants of review concatenations, and runs summarization experiments with LLM APIs (Groq, OpenAI, Together.ai, Hugging Face, and Mock).

## Prerequisites

- Python 3.10+
- Install dependencies:

    pip install openai pandas numpy matplotlib python-dotenv groq requests nltk

- Configure environment variables (based on provider):

    # For Groq (free tier available)
    set GROQ_API_KEY=gsk_your_key_here

    # For OpenAI (paid)
    set OPENAI_API_KEY=sk-proj-your_key_here

    # For Together.ai (free credits available)
    set TOGETHER_API_KEY=your_key_here

    # For Hugging Face (free tier with limitations)
    set HF_TOKEN=hf_your_token_here

## Executable Files and Commands

Run all commands from the project root folder (the folder containing these scripts).

### 1) Analyze businesses and review counts

File: analyze_yelp_reviews.py

Purpose:
- Reads yelp_academic_dataset_business.json and yelp_academic_dataset_review.json from data/ folder
- Computes per-business counts (positive: 4-5⭐, negative: 1-2⭐, neutral: 3⭐)
- Reports how many businesses meet this requirement:
  - at least 10 positive reviews (4-5 stars)
  - at least 1 negative review (1-2 stars)
- Writes business_review_stats.csv

Command:

    python analyze_yelp_reviews.py --business-file data/yelp_academic_dataset_business.json --review-file data/yelp_academic_dataset_review.json

Optional arguments:

    python analyze_yelp_reviews.py --business-file data/business.json --review-file data/review.json --output-csv business_review_stats.csv

### 2) Create positional-bias base dataset (configurable positive/negative counts)

File: create_positional_bias_dataset.py

Purpose:
- Reads business_review_stats.csv
- Filters businesses by the requested number of positive and negative reviews
- Randomly selects the requested number of businesses
- For each business: samples positive reviews + 1 negative review
- Creates positional_bias_dataset.csv with sampled review counts

Command (default 50 businesses, 10 positive + 1 negative):

    python create_positional_bias_dataset.py --business-file data/yelp_academic_dataset_business.json --review-file data/yelp_academic_dataset_review.json --business-limit 50

Small test run:

    python create_positional_bias_dataset.py --business-limit 10

Optional arguments:

    python create_positional_bias_dataset.py --business-limit 100 --positive-count 10 --negative-count 1 --seed 42 --stats-file business_review_stats.csv --output-csv positional_bias_dataset.csv

### 3) Create concatenated datasets with negative review at top/middle/end

File: create_positioned_concatenations.py

Purpose:
- Reads positional_bias_dataset.csv
- Produces three versions where the single negative review is placed at:
  - Top (position 1)
  - Middle (position 6 out of 11)
  - End (position 11)
- Concatenates all reviews into one text block per business
- Output files:
  - positional_bias_concatenated_top.csv
  - positional_bias_concatenated_middle.csv
  - positional_bias_concatenated_end.csv

Command:

    python create_positioned_concatenations.py

Optional arguments:

    python create_positioned_concatenations.py --input-csv positional_bias_dataset.csv --output-prefix positional_bias_concatenated

### 4) Run summarization experiments

File: run_experiments.py

Purpose:
- Loads the three positioned concatenation CSV files
- For each sample, runs three prompting strategies:
  - Baseline (standard prompt)
  - CoT (Chain-of-Thought: "think step by step")
  - Prompt Repetition (repeats the entire prompt twice)
- Calculates for each generated summary:
  - Minority Opinion Recall (does the summary mention the negative review?)
  - Output Length (number of words)
  - Latency (API response time in seconds)
  - Position Sensitivity (max recall difference across positions)
- Saves logs and metrics to experiment_outputs

Supported providers:

    Provider     | Model Example                              | Cost
    ------------|--------------------------------------------|------------------
    mock        | N/A                                        | Free (fake responses)
    groq        | llama-3.1-8b-instant, llama-3.3-70b-versatile | Free tier: 100K-500K tokens/day
    openai      | gpt-4o-mini, gpt-4.1-mini                  | Paid (pay-per-token)
    together    | meta-llama/Llama-3.3-70B-Instruct-Turbo    | Free credits available
    huggingface | google/flan-t5-large                       | Free tier (limited)

Run with Groq (Llama 3.1 8B - free tier, 500K tokens/day):

    python run_experiments.py --provider groq --model llama-3.1-8b-instant --sample-size 20

Run with Groq (Llama 3.3 70B - free tier limited to 100K tokens/day):

    python run_experiments.py --provider groq --model llama-3.3-70b-versatile --sample-size 5

Run with OpenAI (GPT-4o Mini - paid, most reliable):

    python run_experiments.py --provider openai --model gpt-4o-mini --sample-size 50

Run with Together.ai (free credits available):

    python run_experiments.py --provider together --model meta-llama/Llama-3.3-70B-Instruct-Turbo --sample-size 20

Run mock test (no API key needed, validates pipeline):

    python run_experiments.py --provider mock --sample-size 10

Optional arguments:

    python run_experiments.py --provider groq --model llama-3.1-8b-instant --sample-size 50 --temperature 0.2 --max-tokens 220 --output-dir experiment_outputs

### 5) Generate visualizations

File: visualize_results.py

Purpose:
- Reads experiment results from the summary CSV
- Generates publication-quality graphs:
  - Recall by position (bar chart)
  - Output length by position (bar chart)
  - Latency by position (bar chart)
  - Recall line comparison
  - Summary results table
- Saves all images to visualizations/{model_name}/ folder
- Also saves raw data as CSV and summary as TXT

Command:

    python visualize_results.py --model llama_3.1_8b --sample-size 5

Optional arguments:

    python visualize_results.py --model llama_3.3_70b --sample-size 10 --output-dir visualizations

## Recommended End-to-End Order

1. python analyze_yelp_reviews.py --business-file data/yelp_academic_dataset_business.json --review-file data/yelp_academic_dataset_review.json

2. python create_positional_bias_dataset.py --business-file data/yelp_academic_dataset_business.json --review-file data/yelp_academic_dataset_review.json --business-limit 50

3. python create_positioned_concatenations.py

4. python run_experiments.py --provider mock --sample-size 5

5. python run_experiments.py --provider groq --model llama-3.1-8b-instant --sample-size 5

6. python run_experiments.py --provider groq --model llama-3.1-8b-instant --sample-size 50

7. python visualize_results.py --model llama_3.1_8b --sample-size 50

## Outputs

- business_review_stats.csv
- positional_bias_dataset.csv
- positional_bias_concatenated_top.csv
- positional_bias_concatenated_middle.csv
- positional_bias_concatenated_end.csv
- experiment_outputs/experiment_logs_*.jsonl
- experiment_outputs/experiment_detailed_*.csv
- experiment_outputs/experiment_summary_*.csv
- visualizations/{model_name}/recall_by_position.png
- visualizations/{model_name}/output_words_by_position.png
- visualizations/{model_name}/latency_by_position.png
- visualizations/{model_name}/recall_line_comparison.png
- visualizations/{model_name}/results_summary_table.png
- visualizations/{model_name}/{model_name}_raw_data.csv
- visualizations/{model_name}/{model_name}_summary.txt

## Sample Results (Llama 3.1 8B, sample-size=5)

| Strategy   | Top Recall | Middle Recall | End Recall | Position Sensitivity | Avg Output Words |
|------------|------------|---------------|------------|---------------------|------------------|
| Baseline   | 1.0        | 1.0           | 1.0        | 0.0                 | 102.6            |
| CoT        | 1.0        | 1.0           | 1.0        | 0.0                 | 89.9             |
| Repetition | 1.0        | 1.0           | 1.0        | 0.0                 | 126.7            |

Key Finding: Llama 3.1 8B shows no positional bias (position sensitivity = 0.0) and perfect recall across all positions.

## Troubleshooting

Rate limit errors (Groq free tier):
- Llama 3.3 70B: 100K tokens/day → max --sample-size 10
- Llama 3.1 8B: 500K tokens/day → can run --sample-size 50
- Wait for limit reset or upgrade to Developer tier

Missing dataset files:
- Run steps 1-3 in order before running experiments

Check available Groq models:

    python -c "from groq import Groq; import os; client=Groq(api_key=os.getenv('GROQ_API_KEY')); print([m.id for m in client.models.list() if 'llama' in str(m).lower()])"

API key not set (Windows CMD):

    set GROQ_API_KEY=your_key_here
    echo %GROQ_API_KEY%
