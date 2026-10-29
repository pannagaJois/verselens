# VerseLens

VerseLens is a notebook-first poetry analysis project with three complementary
capabilities:

- **Theme classification** with a fine-tuned `microsoft/deberta-v3-base`
  multi-label classifier.
- **Emotion classification** with a second classification head in the exported
  checkpoint.
- **Literary interpretation** with the `Qwen/Qwen3-4B-Instruct-2507` model.

The classifier also supports Integrated Gradients token attribution, so
predictions can be inspected at the token level. The project is intended for
educational and research use, not for authoritative literary criticism.

## Contents

- [Repository layout](#repository-layout)
- [Requirements](#requirements)
- [Run the complete analysis](#run-the-complete-analysis)
- [Run the web frontend](#run-the-web-frontend)
- [Use the classifier from Python](#use-the-classifier-from-python)
- [Use the literary interpreter from Python](#use-the-literary-interpreter-from-python)
- [Train or export the classifier](#train-or-export-the-classifier)
- [Datasets](#datasets)
- [Model details](#model-details)
- [Limitations](#limitations)
- [License](#license)

## Repository layout

```text
verselens/
├── datasets/                         # Cleaned CSV datasets used by notebooks
├── api.py                            # FastAPI backend and static frontend server
├── frontend/                         # Single-page VerseLens web interface
│   ├── index.html                    # Stitch layout with inline API wiring
│   └── reference.png                 # Frontend design reference
├── inference.py                      # Prediction and Integrated Gradients helpers
├── interpreter.py                    # Qwen literary interpretation
├── model.py                          # DeBERTa architecture and checkpoint loader
├── run.ipynb                         # End-to-end classifier + interpretation demo
├── verselens_roberta.ipynb           # Classifier training and export notebook
├── verselens_export/                 # Local classifier export (downloaded/generated)
└── README.md
```

The two model directories are ignored by Git because they contain large model
artifacts. They must be present locally before running the corresponding
inference code.

The web frontend is served by `api.py` from the same origin as the `/analyze`
endpoint. It keeps the Stitch-designed layout and provides poem input, example
loading, analysis progress, sanitized Markdown interpretation, theme/emotion
score bars, generation timing, and word count.

## Requirements

Use Python 3.10 or newer and create an isolated environment:

```bash
git clone https://github.com/pannagaJois/verselens.git
cd verselens

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
```

For classifier inference and the `run.ipynb` notebook:

```bash
pip install torch transformers sentencepiece numpy huggingface_hub \
    jupyter ipykernel
```

For the local web frontend, also install FastAPI and Uvicorn:

```bash
pip install fastapi uvicorn
```

For the faster quantized Apple Silicon interpreter:

```bash
pip install mlx-lm
```

Training additionally uses the packages imported by
`verselens_roberta.ipynb`:

```bash
pip install pandas scikit-learn tqdm
```

The DeBERTa checkpoint is loaded on CPU by default. The interpreter uses Apple
Metal (`mps`) when available and otherwise falls back to CPU.

## Run the complete analysis

### 1. Prepare the DeBERTa classifier export

Download the classifier archive from the
[VerseLens Hugging Face repository](https://huggingface.co/pranav-326/verselens-v1):

```bash
hf download pranav-326/verselens-v1 verselens_export.zip --local-dir .
mkdir -p verselens_export
unzip -o verselens_export.zip -d verselens_export
```

If the repository requires authentication, run `hf auth login` first. The
extracted directory must contain at least:

```text
verselens_export/
├── verselens_state_dict.pt
├── verselens_meta.json
└── tokenizer files
```

### 2. Prepare the Qwen interpreter

No local adapter is required for inference. The base model
`Qwen/Qwen3-4B-Instruct-2507` and its tokenizer are downloaded by
Transformers on first use. Ensure the machine has enough memory for a 4B
parameter model.

### 3. Run the notebook

Start Jupyter from the repository root:

```bash
jupyter notebook
```

Open `run.ipynb`, select the virtual-environment kernel, and run all cells.
The notebook:

1. classifies the supplied poem for themes and emotions;
2. displays labels whose probability meets the configured threshold; and
3. generates a text-grounded literary interpretation with Qwen.

You can change the poem, title, and poet in the second notebook cell.

## Run the web frontend

First prepare the classifier export and Qwen/MLX model as described above.
Then start the FastAPI server from the repository root:

```bash
source .venv/bin/activate
uvicorn api:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser. Enter a poem
and optionally provide its title and poet, then select **Analyze poem**. The
backend runs classification first and generates the literary interpretation
second. The first request may take longer while the MLX model loads.

The frontend calls:

```text
POST /analyze
{
  "poem": "Your poem text",
  "title": "Optional title",
  "poet": "Optional poet"
}
```

The response contains `predictions`, `interpretation`,
`duration_seconds`, and `word_count`. The interpretation is rendered as
sanitized Markdown in the browser. The frontend loads `marked` and
`DOMPurify` from public CDNs; an internet connection is therefore needed for
those browser assets unless they are later vendored locally.

## Use the classifier from Python

`inference.py` loads the classifier export once when imported:

```python
from inference import analyze, evidence

poem = """A poem to analyse."""

predictions = analyze(poem, k=5, threshold=0.3)
print(predictions)
# {'theme': [('nature', 0.81), ...], 'emotion': [('admiration', 0.67), ...]}
```

To inspect token-level evidence for one label:

```python
from inference import TASK_VOCAB, evidence

task = "theme"
label_idx = TASK_VOCAB[task].index("nature")

for token, attribution in evidence(poem, task, label_idx, steps=16)[:12]:
    print(f"{token:15} {attribution:+.4f}")
```

`analyze` returns the top `k` labels per task after applying the threshold.
`evidence` returns tokens sorted by attribution; positive values indicate
movement toward the selected label. Increasing `steps` generally makes the
Integrated Gradients approximation slower but more accurate.

## Use the literary interpreter from Python

`interpreter.py` lazily loads Qwen on the first request:

```python
from interpreter import interpret_poem

interpretation = interpret_poem(
    poem,
    title="Optional title",
    poet="Optional poet",
    max_new_tokens=800,
)
print(interpretation)
```

The interpreter validates that the poem is non-empty and instructs the model
to ground its analysis in the supplied text. Generation is deterministic by
default and capped at 800 new tokens; the prompt also asks for an
interpretation under 450 words.

On Apple Silicon, `interpret_poem_mlx` uses the 4-bit MLX version of the same
model and is substantially faster than the PyTorch/MPS path:

```python
from interpreter import interpret_poem_mlx

interpretation = interpret_poem_mlx(
    poem,
    title="Optional title",
    poet="Optional poet",
    max_tokens=800,
)
print(interpretation)
```

The first MLX call downloads the quantized model (about 2.5 GB) and caches it
locally. The MLX runtime is intended for macOS/Apple Silicon; use
`interpret_poem` for other platforms.

## Train or export the classifier

Open `verselens_roberta.ipynb` in a GPU-enabled notebook environment for the
training workflow. The notebook:

1. discovers and inspects CSV files under `datasets/`;
2. parses list-like and scalar labels;
3. builds a shared DeBERTa encoder with one MLP head per task;
4. trains with weighted binary cross-entropy;
5. evaluates multi-label predictions; and
6. writes `verselens_export/verselens_state_dict.pt`,
   `verselens_export/verselens_meta.json`, tokenizer files, and a zip archive.

The export metadata currently describes the following classifier labels:

- **Theme:** living, social commentaries, relationships, nature, arts &
  sciences, activities, love, history & politics, religion, time & brevity,
  mythology & folklore.
- **Emotion:** joy, amusement, sadness, admiration, contentment, love,
  disappointment, pleasure, disgust, pride, compassion, relief, shame, regret,
  guilt, contempt, hate, interest, anger, fear.

Training settings such as the backbone, text column, label columns, maximum
sequence length, threshold, and learning rates are configured in the notebook.
Change `CONFIG["csv_file"]` and `CONFIG["label_cols"]` when training on a
different compatible dataset.

## Datasets

The repository includes cleaned CSVs for several poetry tasks:

- `POCAAffectClassification_cleaned.csv` — poem-level theme/emotion labels.
- `poetry_train_cleaned.csv`, `poetry_validation_cleaned.csv`,
  `poetry_test_cleaned.csv`, and `poetry_eval_cleaned.csv` — poetry
  classification splits.
- `poemo.english.emotion_cleaned.csv` — English poetry emotion data.
- `poemsum_train.csv`, `poemsum_valid.csv`, and `poemsum_test.csv` —
  poem/summarization data used by the Qwen adapter workflow.

Dataset schemas and label formats vary. Inspect the notebook's dataset
discovery and inspection cells before changing the training configuration.

## Model details

### Classifier

```text
microsoft/deberta-v3-base
└── Shared transformer encoder
    ├── Theme MLP head: Linear → GELU → Dropout(0.1) → Linear
    └── Emotion MLP head: Linear → GELU → Dropout(0.1) → Linear
```

The heads emit logits for multiple labels. `inference.py` applies sigmoid
probabilities and filters them using the configured threshold. The current
export uses a maximum sequence length of 512 and a default threshold of 0.5;
the notebook demo overrides the threshold to 0.3.

### Interpreter

The interpreter uses `Qwen/Qwen3-4B-Instruct-2507` directly. Earlier local
Qwen adapter artifacts may still exist for training or experimentation, but
the current inference path does not load them.

## Limitations

- Predictions reflect the training data and checkpoint; they are not facts
  about a poem or its author.
- Multi-label probabilities are not calibrated confidence estimates.
- Integrated Gradients is an explanatory approximation, not proof of causal
  reasoning.
- The interpreter can produce inaccurate or unsupported literary claims despite
  its grounding instructions. Verify quotations and interpretations against the
  poem.
- Long poems are truncated by the classifier at 512 tokens and by the
  interpreter input limit.
- The code currently loads the classifier on CPU. Qwen generation on MPS or
  CPU can require substantial memory and time.

## License

This repository does not currently include a license file. Treat it as
all-rights-reserved unless the project owner provides separate permission.
Review the licenses for DeBERTa, Qwen, Transformers, and each dataset
before redistributing code, weights, or derived artifacts.
