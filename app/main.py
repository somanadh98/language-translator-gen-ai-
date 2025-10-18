import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from .detection import detect_language
from . import model_utils
from . import openai_utils
import traceback

app = FastAPI(title='Multilingual Translator')

class TranslateRequest(BaseModel):
    text: str
    tgt_lang: str
    src_lang: str | None = None
    use_online: bool | None = False

class TranslateResponse(BaseModel):
    translated_text: str
    used_model: str
    src_lang: str | None
    tgt_lang: str

@app.post('/translate', response_model=TranslateResponse)
async def translate(req: TranslateRequest):
    text = req.text
    tgt = req.tgt_lang
    src = req.src_lang
    use_online = req.use_online or False

    # 1) detect source if not provided
    detected = None
    if not src:
        detected = detect_language(text)
    else:
        detected = src

    # 2) Prefer local model unless user set use_online or local fails
    if not use_online:
        try:
            translated = model_utils.translate_with_local(text, tgt, src_lang=detected)
            return TranslateResponse(translated_text=translated, used_model='nllb', src_lang=detected, tgt_lang=tgt)
        except Exception as e:
            # fallback to online if available
            print('Local model failed, falling back to online if available:', e)
            traceback.print_exc()

    # 3) Online fallback via OpenAI
    try:
        translated = openai_utils.translate_with_openai(text, tgt)
        return TranslateResponse(translated_text=translated, used_model='openai', src_lang=detected, tgt_lang=tgt)
    except Exception as e:
        print('OpenAI fallback failed:', e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail='No available model: local model failed and OpenAI fallback failed.')
