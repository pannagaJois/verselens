"""
VerseLens — Model definition & weight loading utility.

Usage:
    from model import load_model, DEVICE, CONFIG, TASK_VOCAB, tokenizer

    model = load_model()
    # model is on DEVICE, in eval mode, ready for inference.
"""

import json
import torch
import torch.nn as nn
from typing import Dict
from transformers import AutoModel, AutoTokenizer

# ── Paths ────────────────────────────────────────────────────────────────────
EXPORT_DIR = "verselens_export"


# ── Device (temporary stability test) ────────────────────────────────────────
DEVICE = torch.device("cpu")
print(f"Using device: {DEVICE}")


# ── Metadata & Tokenizer ────────────────────────────────────────────────────
with open(f"{EXPORT_DIR}/verselens_meta.json") as _f:
    _meta = json.load(_f)

CONFIG = _meta["config"]
TASK_COLS = _meta["task_cols"]
TASK_VOCAB = _meta["task_vocab"]

tokenizer = AutoTokenizer.from_pretrained(EXPORT_DIR)


# ── Architecture ─────────────────────────────────────────────────────────────
class VerseLens(nn.Module):
    """Shared DeBERTa-v3 encoder + one MLP head per task
    (Linear → GELU → Dropout → Linear)."""

    def __init__(
        self,
        backbone: str,
        task_dims: Dict[str, int],
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(backbone)
        h = self.encoder.config.hidden_size
        self.heads = nn.ModuleDict(
            {
                t: nn.Sequential(
                    nn.Linear(h, h),
                    nn.GELU(),
                    nn.Dropout(dropout),
                    nn.Linear(h, d),
                )
                for t, d in task_dims.items()
            }
        )

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        inputs_embeds=None,
    ) -> Dict[str, torch.Tensor]:
        out = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            inputs_embeds=inputs_embeds,
        )
        cls = out.last_hidden_state[:, 0]  # [CLS] pooling
        return {t: head(cls) for t, head in self.heads.items()}


# ── Loader ───────────────────────────────────────────────────────────────────

def load_model() -> VerseLens:
    """Load trained weights and use consistent float32 precision."""
    task_dims = {t: len(v) for t, v in TASK_VOCAB.items()}

    model = VerseLens(CONFIG["backbone"], task_dims)

    state = torch.load(
        f"{EXPORT_DIR}/verselens_state_dict.pt",
        map_location="cpu",
        weights_only=True,
    )
    model.load_state_dict(state)

    # Keep the entire model in float32 for CPU inference.
    model = model.float()
    model.to(DEVICE)
    model.eval()

    print(
        f"✓ VerseLens loaded on {DEVICE} "
        f"({sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params)"
    )
    return model