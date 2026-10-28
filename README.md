# VerseLens

Multi-task poetry analysis using **DeBERTa-v3-base**. VerseLens classifies poetry themes and emotions, with Integrated Gradients for token-level attribution and model interpretability.

[![Open Training Notebook in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pannagaJois/verselens/blob/main/verselens.ipynb)

[Hugging Face Model Repository](https://huggingface.co/pranav-326/verselens-v1)

## Table of Contents

- [Quick Start — Run Pretrained Model Locally](#quick-start--run-pretrained-model-locally)
- [Retrain with a Different Dataset](#retrain-with-a-different-dataset)
- [Project Structure](#project-structure)
- [Model Architecture](#model-architecture)
- [License](#license)

---

## Quick Start — Run Pretrained Model Locally

### 1. Clone the Repository and Install Dependencies

```bash
git clone https://github.com/pannagaJois/verselens.git
cd verselens

python -m venv .venv
source .venv/bin/activate

pip install torch transformers sentencepiece numpy huggingface_hub
```

### 2. Download the Pretrained Model from Hugging Face

Download the export model archive directly from the Hugging Face Hub repository:

```bash
hf download pranav-326/verselens-v1 verselens_export.zip --local-dir .
```

If the repository is private, authenticate first:

```bash
hf auth login
```

Extract the archive into the directory expected by `model.py`:

```bash
mkdir -p verselens_export
unzip -o verselens_export.zip -d verselens_export
```

The `verselens_export/` directory should contain the model checkpoint, metadata, and tokenizer files, including:

- `verselens_state_dict.pt`
- `verselens_meta.json`
- Tokenizer files

> **Note:** The archive must be uploaded to the Hugging Face repository under the filename `verselens_export.zip`. If you used a different filename, substitute it in the download and extraction commands.

### 3. Run Inference

Run the inference demonstration:

```bash
python inference.py
```
then start the ipynb kernel in `run.iynb`
and then run all cells

## Project Structure

```text
verselens/
├── datasets/                  # Training datasets
├── verselens_export/          # Downloaded model export
│   ├── verselens_state_dict.pt
│   ├── verselens_meta.json
│   └── tokenizer files
├── model.py                   # Architecture and weight loading
├── inference.py               # Prediction and Integrated Gradients
├── run.ipynb                  # Inference input/output notebook
├── verselens.ipynb            # Training notebook
├── .gitignore
└── README.md
```

The export model files are downloaded from the [VerseLens Hugging Face repository](https://huggingface.co/pranav-326/verselens-v1), rather than stored in the Git repository.

## Model Architecture

```text
VerseLens
├── Shared Encoder: microsoft/deberta-v3-base
│   └── Transformer encoder
└── Task Heads
    ├── Theme classification head
    └── Emotion classification head
```

Each task head uses the following architecture:

```text
Linear(hidden_size → hidden_size)
    → GELU
    → Dropout(0.1)
    → Linear(hidden_size → number_of_labels)
```

### Key Features

- **Multi-task classification:** Shared encoder with independent task heads.
- **Multi-label predictions:** Sigmoid probabilities allow multiple labels per poem.
- **Interpretability:** Integrated Gradients provides token-level attribution scores.
- **Configurable inference:** Choose the number of labels and the minimum prediction threshold.
- **Local inference:** Run predictions locally after downloading the model export.

Prediction quality depends on the training data, evaluation methodology, and checkpoint used. Attribution scores are explanatory estimates and should not be treated as definitive evidence of a model's reasoning.

## License

This project is intended for educational and research purposes. Check the repository's license and the pretrained backbone's license before redistributing the code, weights, or derived artifacts.
