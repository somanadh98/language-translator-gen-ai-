import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
HF_MODEL = os.getenv('HF_MODEL', 'facebook/nllb-200-distilled-600M')
DEVICE = os.getenv('DEVICE', 'auto')
MAX_NEW_TOKENS = int(os.getenv('MAX_NEW_TOKENS', '256'))

# Lazy imports / state
_model = None
_tokenizer = None
_device = None

def _get_device():
    global _device
    if _device is not None:
        return _device
    if DEVICE == 'auto':
        try:
            import torch
            _device = 'cuda' if torch.cuda.is_available() else 'cpu'
        except Exception:
            _device = 'cpu'
    else:
        _device = DEVICE
    return _device

def load_local_model(force_reload: bool=False):
    """Try multiple loading strategies for best-effort CPU-friendly or quantized loading.
    1) Try 8-bit load_in_8bit + device_map='auto' (requires bitsandbytes)
    2) Try device_map='auto' without 8-bit
    3) Fallback to CPU-only full precision
    """
    global _model, _tokenizer
    if _model is not None and _tokenizer is not None and not force_reload:
        return _model, _tokenizer
    try:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        device = _get_device()
        print(f"Attempting to load model {HF_MODEL} for device {device} ...")
        # Preferred: quantized 8-bit load (fast + memory efficient) if bitsandbytes available and device is cuda
        if device.startswith('cuda'):
            try:
                print('Trying 8-bit (bitsandbytes) quantized load...')
                _tokenizer = AutoTokenizer.from_pretrained(HF_MODEL, use_fast=False)
                _model = AutoModelForSeq2SeqLM.from_pretrained(HF_MODEL, device_map='auto', load_in_8bit=True, low_cpu_mem_usage=True)
                print('Loaded model in 8-bit.')
                return _model, _tokenizer
            except Exception as e:
                print('8-bit load failed, will try auto device_map without 8-bit:', e)
        # Try device_map auto (may still place on cuda if available)
        try:
            _tokenizer = AutoTokenizer.from_pretrained(HF_MODEL, use_fast=False)
            _model = AutoModelForSeq2SeqLM.from_pretrained(HF_MODEL, device_map='auto', low_cpu_mem_usage=True)
            print('Loaded model with device_map=auto.')
            return _model, _tokenizer
        except Exception as e:
            print('device_map auto failed, falling back to CPU load:', e)
        # CPU-only fallback
        _tokenizer = AutoTokenizer.from_pretrained(HF_MODEL, use_fast=False)
        _model = AutoModelForSeq2SeqLM.from_pretrained(HF_MODEL)
        print('Loaded model on CPU (full precision).')
        return _model, _tokenizer
    except Exception as e:
        _model = None
        _tokenizer = None
        raise RuntimeError(f'Failed to load local model: {e}')

def translate_with_local(text: str, tgt_lang: str, src_lang: Optional[str]=None) -> str:
    """Translate using the loaded HF model (NLLB). Expects NLLB style language codes like eng_Latn, fra_Latn."""
    model, tokenizer = load_local_model()
    device = _get_device()
    import torch
    # Tokenize
    inputs = tokenizer(text, return_tensors='pt', padding=True)
    # Move inputs to correct device if model on GPU
    try:
        if device.startswith('cuda'):
            inputs = {k:v.to('cuda') for k,v in inputs.items()}
        else:
            inputs = {k:v for k,v in inputs.items()}
    except Exception:
        pass
    # NLLB requires forced_bos_token_id for target language if tokenizer supports it
    generate_kwargs = {'max_new_tokens': MAX_NEW_TOKENS, 'do_sample': False}
    if hasattr(tokenizer, 'lang_code_to_id') and tgt_lang in tokenizer.lang_code_to_id:
        forced_id = tokenizer.lang_code_to_id[tgt_lang]
        generate_kwargs['forced_bos_token_id'] = forced_id
    out = model.generate(**inputs, **generate_kwargs)
    decoded = tokenizer.batch_decode(out, skip_special_tokens=True)[0]
    return decoded
