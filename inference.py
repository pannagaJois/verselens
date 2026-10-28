"""
VerseLens — Inference helpers: prediction, analysis, and Integrated Gradients
token-level attribution.

Usage:
    from inference import analyze, predict_probs, evidence

    results = analyze("Some poem text here...", k=5, threshold=0.3)
    print(results)
"""

import re
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

from model import load_model, DEVICE, CONFIG, TASK_COLS, TASK_VOCAB, tokenizer

# ── Load model once on import ────────────────────────────────────────────────
model = load_model()


# ── Helpers ──────────────────────────────────────────────────────────────────
def _encode(poem_text: str) -> dict:
    """Tokenize a single poem and move tensors to DEVICE."""
    enc = tokenizer(
        poem_text,
        truncation=True,
        max_length=CONFIG["max_len"],
        return_tensors="pt",
    )
    return {
        k: v.to(DEVICE)
        for k, v in enc.items()
        if k in ("input_ids", "attention_mask")
    }


# ── Prediction ───────────────────────────────────────────────────────────────
@torch.no_grad()
def predict_probs(poem_text: str) -> Dict[str, np.ndarray]:
    """Return sigmoid probabilities for every label of every task."""
    model.eval()
    enc = _encode(poem_text)
    logits = model(enc["input_ids"], enc["attention_mask"])
    return {
        t: torch.sigmoid(l.float())[0].cpu().numpy()
        for t, l in logits.items()
    }


def analyze(
    poem_text: str,
    k: int = 5,
    threshold: Optional[float] = None,
) -> Dict[str, List[Tuple[str, float]]]:
    """Top-k labels per task whose probability ≥ threshold.

    Parameters
    ----------
    poem_text : str
        The poem to classify.
    k : int
        Number of top labels to return per task.
    threshold : float or None
        Minimum probability to include a label (default: CONFIG threshold).

    Returns
    -------
    dict mapping task name → list of (label, probability) tuples.
    """
    thr = CONFIG["threshold"] if threshold is None else threshold
    result = {}
    for t, p in predict_probs(poem_text).items():
        order = np.argsort(-p)[:k]
        result[t] = [
            (TASK_VOCAB[t][i], round(float(p[i]), 4))
            for i in order
            if p[i] >= thr
        ]
    return result


# ── Integrated Gradients Attribution ─────────────────────────────────────────
def evidence(
    poem_text: str,
    task: str,
    label_idx: int,
    steps: int = 8,
    verbose: bool = False,
) -> List[Tuple[str, float]]:
    """Integrated Gradients of the target logit w.r.t. input embeddings.

    Baseline = PAD embedding for ordinary tokens (special tokens kept).
    Returns (token, attribution) sorted descending; positive values push the
    model TOWARD the label.

    Parameters
    ----------
    poem_text : str
        Input poem.
    task : str
        Task name (e.g. "theme").
    label_idx : int
        Index into TASK_VOCAB[task] for the label to explain.
    steps : int
        Number of interpolation steps for the Riemann sum (more = more accurate
        but slower).
    verbose : bool
        If True, print the IG completeness check.
    """
    assert task in TASK_COLS, (
        f"Unknown task {task!r}. Available: {list(TASK_COLS)}"
    )
    assert 0 <= label_idx < len(TASK_VOCAB[task]), (
        f"label_idx out of range for {task} (0..{len(TASK_VOCAB[task]) - 1})"
    )

    model.eval()
    enc = _encode(poem_text)
    ids, am = enc["input_ids"], enc["attention_mask"]
    emb_layer = model.encoder.embeddings.word_embeddings

    with torch.no_grad():
        emb = emb_layer(ids)  # [1, T, H]
        pad_emb = emb_layer(
            torch.tensor([[tokenizer.pad_token_id]], device=DEVICE)
        )
        special = torch.tensor(
            tokenizer.get_special_tokens_mask(
                ids[0].tolist(), already_has_special_tokens=True
            ),
            dtype=torch.bool,
            device=DEVICE,
        )
        baseline = torch.where(
            special[None, :, None], emb, pad_emb.expand_as(emb)
        )

    grad_sum = torch.zeros_like(emb)
    for s in range(1, steps + 1):
        x = (
            baseline + (s / steps) * (emb - baseline)
        ).detach().requires_grad_(True)
        logit = model(inputs_embeds=x, attention_mask=am)[task][0, label_idx]
        grad_sum += torch.autograd.grad(logit, x)[0]

    attr = (
        ((emb - baseline) * grad_sum / steps)
        .sum(-1)[0]
        .detach()
        .cpu()
        .numpy()
    )  # [T]

    if verbose:
        with torch.no_grad():
            fx = model(inputs_embeds=emb, attention_mask=am)[task][
                0, label_idx
            ].item()
            fb = model(inputs_embeds=baseline, attention_mask=am)[task][
                0, label_idx
            ].item()
        print(
            f"   IG completeness: sum(attr)={attr.sum():.3f} vs "
            f"f(x)-f(base)={fx - fb:.3f} (gap shrinks with more steps)"
        )

    toks = tokenizer.convert_ids_to_tokens(ids[0].tolist())
    pairs = [
        (t.replace("\u2581", "").strip() or t, float(a))
        for t, a, sp in zip(toks, attr, special.cpu().numpy())
        if not sp
    ]
    return sorted(pairs, key=lambda z: -z[1])


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json

    # Robert Frost — "Stopping by Woods on a Snowy Evening" (1923, public domain)
    DEMO_POEM = """\
It won't be a tire to look at you all day
Face between the valley of cheekbones, showing the way.
Trail of jasmine spread across your jet black hair
Arm of milky way amongst space, is that you there?
Coral like eyebrows, pearl like eyes
Melody of water in the breath your voice lies
Skin so supple like dessert sand at dawn
Did god, in wonder, create one of her own?"""

    print("=" * 60)
    print("analyze() — Top predicted themes")
    print("=" * 60)
    preds = analyze(DEMO_POEM, k=5, threshold=0.3)
    print(json.dumps(preds, indent=2))

    probs = predict_probs(DEMO_POEM)
    for task, p in probs.items():
        top = int(np.argmax(p))
        label = TASK_VOCAB[task][top]
        top3 = ", ".join(
            f"{TASK_VOCAB[task][i]}={p[i]:.3f}" for i in np.argsort(-p)[:3]
        )
        print(f"\n[{task}] top-3 scores: {top3}")
        print(
            f"[{task}] evidence for '{label}' "
            f"(Integrated Gradients, top-12 tokens):"
        )
        for tok, a in evidence(DEMO_POEM, task, top, steps=8, verbose=True)[
            :12
        ]:
            print(f"   {tok:15s} {a:+.4f}")
