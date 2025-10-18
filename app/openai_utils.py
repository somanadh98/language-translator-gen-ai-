import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or None

# We attempt to support multiple OpenAI SDK shapes:
# 1) openai (classic) -> openai.ChatCompletion.create(...)
# 2) openai with 'OpenAI' client (newer) -> OpenAI().chat.completions.create(...)
# 3) if neither available, raise informative error.

def translate_with_openai(text: str, tgt_lang: str, system_prompt: str='You are a helpful translator.') -> str:
    if OPENAI_API_KEY is None:
        raise RuntimeError('OPENAI_API_KEY not set.')

    # Try classic openai package usage
    try:
        import openai
        # If the client is the new style (from openai import OpenAI)
        if hasattr(openai, 'OpenAI'):
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            # Using chat completions (new API shape)
            prompt = f"Translate the following text to the target language ({tgt_lang}).\n\nText:\n{text}\n\nProvide only the translated text."
            resp = client.chat.completions.create(
                model='gpt-4o' if 'gpt-4o' in getattr(client, 'models', []) else 'gpt-4o-mini',
                messages=[{'role':'system','content':system_prompt},{'role':'user','content':prompt}],
                max_tokens=1024,
                temperature=0.2
            )
            # New client returns different shapes; try to extract safely
            choices = resp.get('choices') or resp.get('result', {}).get('choices') or []
            if choices:
                return choices[0].get('message', {}).get('content', '').strip() or choices[0].get('text','').strip()
        else:
            # Classic openai.ChatCompletion.create
            openai.api_key = OPENAI_API_KEY
            prompt = f"Translate the following text to the target language ({tgt_lang}).\n\nText:\n{text}\n\nProvide only the translated text."
            resp = openai.ChatCompletion.create(
                model='gpt-4o' if _model_exists_in_openai('gpt-4o') else 'gpt-4o-mini',
                messages=[{'role':'system','content':system_prompt},{'role':'user','content':prompt}],
                max_tokens=1024,
                temperature=0.2
            )
            # Extract response
            if 'choices' in resp and len(resp['choices'])>0:
                msg = resp['choices'][0].get('message') or {}
                return (msg.get('content') or resp['choices'][0].get('text') or '').strip()
    except Exception as e:
        # If any method fails, raise a clear error for the caller to handle/fallback
        raise RuntimeError(f'OpenAI translate failed: {e}')

def _model_exists_in_openai(model_name: str) -> bool:
    # Try to check model existence without crashing
    try:
        import openai
        if hasattr(openai, 'OpenAI'):
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            models = client.models.list().get('data', [])
            return any(m.get('id')==model_name for m in models)
        else:
            # classic openai
            openai.api_key = OPENAI_API_KEY
            models = openai.Model.list().get('data', [])
            return any(m.get('id')==model_name for m in models)
    except Exception:
        return False
