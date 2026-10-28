
"""
VerseLens — Qwen2.5 poem interpretation.
Independent from the theme/emotion classifier.
"""

import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
ADAPTER_PATH = Path(__file__).parent / (
    "verselens_qwen2_5_1_5b_interpreter_adapter"
)


SYSTEM_PROMPT = """
You are VerseLens, an expert literary analyst specialising in poetry.

Your task is to produce a substantial, nuanced, text-grounded literary
interpretation of the complete poem. Do not merely summarise its content
or paraphrase each stanza. Explore how the poem creates meaning.

Write approximately 700–1000 words when the poem supports that depth.
For shorter poems, remain proportionate but still analyse them carefully.
Never pad the response with repetition or unsupported claims.

Use the following structure:

1. CENTRAL INTERPRETATION
Explain the poem's central meaning, its deeper implications, and what
the poem appears to explore beyond its literal subject.

2. STANZA-BY-STANZA ANALYSIS
Discuss each stanza or meaningful section separately. Explain what
happens, what changes, and how each section contributes to the whole.
Refer to specific words, phrases, and images from the poem.

3. THEMES AND IDEAS
Explore the major themes and their relationships. Explain how the poem
develops these ideas rather than simply listing theme names.

4. IMAGERY, METAPHOR AND SYMBOLISM
Analyse important images, metaphors, symbols, contrasts, and other
literary devices. Explain their effects and support claims with textual
evidence. Do not invent devices that are not present.

5. TONE AND EMOTIONAL MOVEMENT
Discuss the speaker's tone, emotional tensions, shifts in mood, and
how the reader's understanding develops through the poem.

6. FORM AND LANGUAGE
When supported by the text, examine diction, repetition, rhythm, sound,
structure, and other stylistic choices. Explain how these choices
contribute to meaning.

7. OVERALL SIGNIFICANCE
Bring the analysis together. Explain what makes the poem meaningful,
what ambiguities remain, and which interpretations are most strongly
supported by the text.

IMPORTANT RULES:
- Ground interpretations in the supplied poem.
- Distinguish direct textual evidence from plausible inference.
- Acknowledge ambiguity and alternative readings where appropriate.
- Do not invent quotations, historical context, biography, or authorial
  intentions.
- Do not force every analytical category onto every poem.
- Prefer specific, insightful analysis over generic literary language.

EVIDENCE AND ACCURACY REQUIREMENTS:

1. Analyse only the poem supplied in the current request.
2. Never invent poem titles, names, quotations, lines, literary devices,
   metrical patterns, historical facts, or authorial intentions.
3. Before quoting a phrase, verify that the exact phrase occurs in the
   supplied poem. If it does not, paraphrase without quotation marks.
4. If you cannot confidently identify the meter or rhyme scheme,
   explicitly say that the formal pattern is uncertain or omit the claim.
5. Ground every major interpretive claim in a specific word, phrase,
   image, or structural feature from the poem.
6. Distinguish textual observation from interpretation.
7. Do not repeat the same point across multiple sections.
8. If a requested analytical feature is not clearly supported by the
   poem, say so rather than inventing an example.
9. Preserve the correct title and author supplied by the user.
10. Prioritise analytical depth, textual accuracy, and nuance over
    response length.

"""

_tokenizer = None
_model = None
_device = None


def load_interpreter():
    """Load Qwen once, on the first interpretation request."""
    global _tokenizer, _model, _device

    if _model is not None:
        return _model, _tokenizer

    if not ADAPTER_PATH.is_dir():
        raise FileNotFoundError(
            f"Adapter directory not found: {ADAPTER_PATH}\n"
            "Extract your trained Qwen adapter into this directory."
        )

    _device = (
        "mps" if torch.backends.mps.is_available()
        else "cpu"
    )
    dtype = torch.float16 if _device == "mps" else torch.float32

    print(f"Loading VerseLens interpreter on {_device}...")

    _tokenizer = AutoTokenizer.from_pretrained(
        str(ADAPTER_PATH)
    )

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )

    _model = PeftModel.from_pretrained(
        base_model,
        str(ADAPTER_PATH),
    )

    _model.to(_device)
    _model.eval()

    print("VerseLens interpreter loaded.")
    return _model, _tokenizer


def interpret_poem(
    poem: str,
    title: str = "",
    poet: str = "",
    max_new_tokens: int = 900,
) -> str:
    """Generate a literary interpretation of a complete poem."""

    if not poem or not poem.strip():
        raise ValueError("Please provide a non-empty poem.")

    model, tokenizer = load_interpreter()

    metadata = []
    if title.strip():
        metadata.append(f"Title: {title.strip()}")
    if poet.strip():
        metadata.append(f"Poet: {poet.strip()}")

    user_content = (
        ("\n".join(metadata) + "\n\n") if metadata else ""
    )
    user_content += (
        f"Poem:\n{poem.strip()}\n\n"
        "Provide a detailed literary interpretation supported by "
        "specific evidence from the poem."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1536,
    )
    inputs = {
        key: value.to(_device)
        for key, value in inputs.items()
    }

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.08,
            pad_token_id=tokenizer.pad_token_id
            if tokenizer.pad_token_id is not None
            else tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = output[0, inputs["input_ids"].shape[1]:]

    return tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    ).strip()


if __name__ == "__main__":
    poem = """
LORD of the lotus, lord of the harvest,
Bright and munificent lord of the morn!
Thine is the bounty that prospered our sowing,
Thine is the bounty that nurtured our corn.
We bring thee our songs and our garlands for tribute,
The gold of our fields and the gold of our fruit;
O giver of mellowing radiance, we hail thee,
We praise thee, O Surya, with cymbal and flute.

Lord of the rainbow, lord of the harvest,
Great and beneficent lord of the main!
Thine is the mercy that cherished our furrows,
Thine is the mercy that fostered our grain.
We bring thee our thanks and our garlands for tribute,
The wealth of our valleys, new-garnered and ripe;
O sender of rain and the dewfall, we hail thee,
We praise thee, Varuna, with cymbal and pipe.
    """

    # result = interpret_poem(
    #     poem,
    #     title="Harvest Hymn: Mens Voices:",
    #     poet="Sarojini Naidu",
    # )

    # print("\n" + "=" * 60)
    # print("VERSELENS — LITERARY INTERPRETATION")
    # print("=" * 60)
    # print(result)
