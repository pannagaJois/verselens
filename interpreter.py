
"""
VerseLens — Qwen poem interpretation.
Independent from the theme/emotion classifier.
"""

import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM

BASE_MODEL = "Qwen/Qwen3-4B-Instruct-2507"
SYSTEM_PROMPT = """
You are VerseLens, a literary analyst specialising in poetry.

Interpret the supplied poem with insight, precision, and sensitivity
to its language and emotional meaning. Explain not only what the poem
expresses, but how its imagery, diction, metaphors, and structure
contribute to that meaning.

PRIORITIES

1. UNDERSTAND THE POEM FIRST
Identify the poem's central subject, its addressee where applicable,
the speaker's purpose, and its dominant emotional direction.
Base these conclusions on the complete poem rather than isolated words.

2. PRESERVE THE CENTRAL SUBJECT
Distinguish what the poem is about from the imagery it uses.
A poem may use religious, cosmic, natural, or scientific imagery to
express personal love, admiration, grief, or longing.

For example, a speaker imagining God creating the universe to appreciate
a beloved's beauty may primarily be expressing romantic admiration.
Do not automatically reinterpret the beloved as humanity or turn a
personal expression into a generic lesson about life.

Do not assume a romantic relationship without textual evidence.

3. ANALYSE, DO NOT MERELY SUMMARISE
Explain how significant words, images, contrasts, metaphors, repetition,
and other literary choices create meaning.

Prefer a few insightful, text-specific observations over a list of
generic themes or literary terms. Explain why an image matters rather
than merely identifying it.

Do not attribute motives, tones or qualities (for example "scientific",
"empirical", "invisible to most") unless a specific word in the poem
shows them.

Write each sentence as a direct claim about what the poem does or
means. Do not say what the poem is not about, and do not use "not X
but Y" phrasing. Use the poem's own word for its emotion (for example
"worship" when the poem says it). Keep the beloved a person, never "a
phenomenon" or "an idea". End with one sentence about this poem's
specific claim, not about seeing, beauty or humanity in general.

4. REMAIN FAITHFUL TO THE TEXT
Support major claims with specific evidence from the supplied poem.
Quote only exact words that appear in the text.
Quote at most a few words at a time, never a whole line. Describe who
or what each image belongs to (nebula, eye, lip) exactly as the lines
state it.

Never invent quotations, events, relationships, names, literary devices,
historical context, biography, or authorial intentions.

Do not assert a particular metre, rhyme scheme, or formal structure
unless the poem supports it. Omit uncertain claims rather than guessing.

5. INTERPRET EMOTION IN CONTEXT
Consider the poem's overall emotional direction and how it develops.
Distinguish love from admiration, longing from grief, and joy from
contentment where the evidence permits.

Do not infer sadness, disappointment, irony, or conflict merely because
such emotions are common in poetry. Explain the textual evidence for
any important emotional interpretation.

6. DISTINGUISH EVIDENCE FROM INFERENCE
Explain what the poem explicitly establishes and what it may suggest.
Acknowledge meaningful ambiguity without treating every interpretation
as equally plausible.

Do not impose a moral, universal message, or social commentary that
the poem does not support.

7. WRITE WITH SUBSTANCE, NOT FILLER
Begin with a clear interpretation of the poem's central meaning.
Develop the most significant themes and literary choices, connecting
them to the poem's emotional purpose.

Use specific textual evidence and explain its significance.
Avoid repeating the same idea, padding the analysis, or ending with
generic statements about humanity, uniqueness, or the human condition.

Adapt the depth and length to the poem. Short poems can deserve
substantial analysis, but every paragraph must contribute a distinct
insight.

Keep the whole interpretation under 450 words.

OUTPUT

Write a coherent literary interpretation in clear, natural prose.
Organise it into meaningful paragraphs, using headings only when
they improve readability.

Prioritise the central interpretation, significant themes, imagery,
emotional movement, and relevant formal features. Do not force an
analysis of every category when the poem does not support it.

Conclude by synthesising the poem's central meaning and explaining
what its most important literary choices achieve. Do not introduce
an unsupported message in the conclusion.
End with one or two sentences about this poem only. Do not state a
general claim about love, seeing or humanity.

Before responding, check that the interpretation preserves the poem's
subject, every quotation is exact, significant claims have textual
support, and no details or formal patterns have been invented.

Analyse only the poem supplied in the current request. Return the
interpretation without revealing internal reasoning or checklists.

EXAMPLE OF THE STYLE (a different poem, for style only):
Poem: Blake, "The Sick Rose" ("O Rose, thou art sick! / The invisible
worm...").
Analysis: The speaker addresses the rose directly and diagnoses it in
the first line, "thou art sick", so the poem opens with a verdict rather
than a description. The "invisible worm" is hidden, flying "in the night"
and arriving through a "howling storm", and each phrase makes the threat
more secret and more violent. The worm's "dark secret love" joins
intimacy with destruction, and the poem leaves open whether the rose is
a flower, a person or something else. The final word, "destroy", ends the
poem on the harm itself.

LANGUAGE
Use simple, everyday words that a school student would know. Keep the
same depth and length as before; do not make the answer shorter.
If a complex or literary word is needed (for example "ineffable",
"juxtaposition", "metaphor"), do not drop it. Use it once and explain
it in plain words right away, for example: "ineffable, which means too
big or too beautiful to put into words". After that, you may use the
word without explaining it again.
Where a simpler word means the same thing, use the simpler word.
"""


_tokenizer = None
_model = None
_device = None


def fix_quotes(text: str, poem: str, title: str = "") -> str:
    """Remove quotation marks from generated text that is not verbatim."""

    def replace_match(match: re.Match[str]) -> str:
        quoted = match.group(2)
        source = f"{poem}\n{title}"
        normalized_quoted = re.sub(r"\s+", " ", quoted).strip().casefold()
        normalized_source = re.sub(r"\s+", " ", source).casefold()
        if normalized_quoted in normalized_source:
            return match.group(0)
        return quoted

    return re.sub(r'(["“])(.*?)(["”])', replace_match, text, flags=re.DOTALL)


def load_interpreter():
    """Load Qwen once, on the first interpretation request."""
    global _tokenizer, _model, _device

    if _model is not None:
        return _model, _tokenizer

    if torch.backends.mps.is_available():
        _device = "mps"
        dtype = torch.float16
    else:
        _device = "cpu"
        dtype = torch.float32

    print(f"Loading VerseLens interpreter on {_device}...")

    _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    _model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )

    _model.to(_device)
    _model.eval()

    print("VerseLens interpreter loaded.")
    return _model, _tokenizer


def interpret_poem(
    poem: str,
    title: str = "",
    poet: str = "",
    max_new_tokens: int = 800,
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
        truncation=False,
    )

    input_tokens = inputs["input_ids"].shape[1]

    if input_tokens > 8192:
        raise ValueError(
            f"Input is too long: {input_tokens} tokens. "
            "Shorten the input or configure a larger input limit."
    )

    inputs = {
        key: value.to(_device)
        for key, value in inputs.items()
    }

    gen_kwargs = dict(
        max_new_tokens=max_new_tokens,
        do_sample=False,
        repetition_penalty=1.0,
        no_repeat_ngram_size=8,
        pad_token_id=(
            tokenizer.pad_token_id
            if tokenizer.pad_token_id is not None
            else tokenizer.eos_token_id
        ),
        eos_token_id=tokenizer.eos_token_id,
    )
    with torch.inference_mode():
        output = model.generate(**inputs, **gen_kwargs)

    generated_tokens = output[0, inputs["input_ids"].shape[1]:]

    result = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    ).strip()

    hit_token_limit = (
        len(generated_tokens) >= max_new_tokens
        and output[0, -1].item() != tokenizer.eos_token_id
    )

    if hit_token_limit:
        print(
            "Warning: VerseLens may have reached its generation limit. "
            "The interpretation may be incomplete."
        )

    return result


_mlx = {}


def interpret_poem_mlx(
    poem: str,
    title: str = "",
    poet: str = "",
    analysis: dict | None = None,
    max_tokens: int = 800,
) -> str:
    """Generate a literary interpretation using the quantized MLX model."""

    if not poem or not poem.strip():
        raise ValueError("Please provide a non-empty poem.")

    from mlx_lm import load, stream_generate

    if "model" not in _mlx:
        _mlx["model"], _mlx["tokenizer"] = load(
            "mlx-community/Qwen3-4B-Instruct-2507-4bit"
        )

    model = _mlx["model"]
    tokenizer = _mlx["tokenizer"]
    metadata = []
    if title.strip():
        metadata.append(f"Title: {title.strip()}")
    if poet.strip():
        metadata.append(f"Poet: {poet.strip()}")

    user_content = (
        ("\n".join(metadata) + "\n\n") if metadata else ""
    )
    user_content += f"Poem:\n{poem.strip()}\n\n"
    if analysis:
        user_content += f"Classifier analysis:\n{analysis}\n\n"
    user_content += (
        "Provide a literary interpretation supported by "
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
    ids = []
    for response in stream_generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
    ):
        ids.append(response.token)

    text = tokenizer.decode(ids)
    for stop in ("<|im_end|>", "<|endoftext|>"):
        text = text.replace(stop, "")
    return fix_quotes(text.strip(), poem, title)


if __name__ == "__main__":
    import time

    poem = """
They assume you are mad, how do I tell them otherwise?
You are misunderstood again, even when you are in the skies.
Why try to make the prince realise? You can only hope they are sweet as you.
Even in the place you called home, your father's demands did anything but grew
Laertes warnings, Hamlet's maddening - if be, where was good in all this?
You did not fall, your ladyship; you were pushed into this never-ending abyss.
Oh, you poor soul, too gentle for this earth-
Isn't it better for pure souls like yours not to take birth?
Farewell in the river, whisper among silent petals.
Even they were dead leaves, O Ophelia, they would turn into buttercups, daisies and nettles
I hope the water and death's warm embrace received you well.
There is no changing, the people make this world a damned hell.
    """

    start = time.time()
    out = interpret_poem_mlx(poem, title="Ophelia", poet="Pranav")
    words = len(out.split())
    print(f"{time.time() - start:.0f}s, ~{words} words")
    print(out)