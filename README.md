# VerseLens

VerseLens is a notebook-first poetry analysis project with three complementary
capabilities:

- **Theme classification** with a fine-tuned `microsoft/deberta-v3-base`
  multi-label classifier.
- **Emotion classification** with a second classification head in the exported
  checkpoint.
- **Literary interpretation** with a Qwen2.5-1.5B-Instruct model and a local
  PEFT/LoRA adapter.

The classifier also supports Integrated Gradients token attribution, so
predictions can be inspected at the token level. The project is intended for
educational and research use, not for authoritative literary criticism.

## Contents

- [Repository layout](#repository-layout)
- [Requirements](#requirements)
- [Run the complete analysis](#run-the-complete-analysis)
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
├── inference.py                      # Prediction and Integrated Gradients helpers
├── interpreter.py                    # Qwen + PEFT literary interpretation
├── model.py                          # DeBERTa architecture and checkpoint loader
├── run.ipynb                         # End-to-end classifier + interpretation demo
├── verselens_roberta.ipynb           # Classifier training and export notebook
├── verselens_export/                 # Local classifier export (downloaded/generated)
├── verselens_qwen2_5_1_5b_interpreter_adapter/
│                                     # Local Qwen LoRA adapter (downloaded/generated)
└── README.md
```

The two model directories are ignored by Git because they contain large model
artifacts. They must be present locally before running the corresponding
inference code.

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

For the Qwen interpreter, also install PEFT:

```bash
pip install peft accelerate
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

### 2. Prepare the Qwen interpreter adapter

Place the trained adapter at the repository root with this exact name:

```text
verselens_qwen2_5_1_5b_interpreter_adapter/
```

It must contain the PEFT adapter weights and tokenizer files, including
`adapter_config.json` and `adapter_model.safetensors`. The base model
`Qwen/Qwen2.5-1.5B-Instruct` is downloaded by Transformers on first use.

### 3. Run the notebook

Start Jupyter from the repository root:

```bash
jupyter notebook
```

Open `run.ipynb`, select the virtual-environment kernel, and run all cells.
The notebook:

1. classifies the supplied poem for themes and emotions;
2. displays labels whose probability meets the configured threshold; and
3. generates a text-grounded literary interpretation with the Qwen adapter.

You can change the poem, title, and poet in the second notebook cell.

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

`interpreter.py` lazily loads Qwen and the adapter on the first request:

```python
from interpreter import interpret_poem

interpretation = interpret_poem(
    poem,
    title="Optional title",
    poet="Optional poet",
    max_new_tokens=900,
)
print(interpretation)
```

The interpreter validates that the poem is non-empty and instructs the model
to ground its analysis in the supplied text. Model generation is stochastic,
so repeated runs may differ.

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

The interpreter uses `Qwen/Qwen2.5-1.5B-Instruct` with a PEFT LoRA adapter.
The adapter metadata records QLoRA training with 4-bit NF4 quantization on
302 filtered examples from `poemsum_test.csv` (240 train, 31 validation, and
31 test rows).

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
- The code currently loads the classifier on CPU. Large-model interpreter
  generation can require substantial memory.

## License

This repository does not currently include a license file. Treat it as
all-rights-reserved unless the project owner provides separate permission.
Review the licenses for DeBERTa, Qwen, Transformers, PEFT, and each dataset
before redistributing code, weights, or derived artifacts.
