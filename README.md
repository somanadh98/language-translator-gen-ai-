# Multilingual Translator (Updated)

## What's new
- Quantized / CPU-friendly loading using `bitsandbytes` when a CUDA GPU is available, with safe fallbacks to CPU-only loads.
- Improved language code mapping: maps 2-letter ISO codes (en, fr, hi, etc.) to NLLB-style codes like `eng_Latn`, `hin_Deva`.
- Hardened OpenAI integration that supports multiple OpenAI SDK shapes.
- A minimal React frontend (in `frontend/`) to try translations from the browser (proxy requests to FastAPI).

## Quickstart (Local)
1. Ensure Python 3.10+ is installed.
2. Create a venv and install Python deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. (Optional) If using a GPU, install a CUDA-compatible PyTorch and ensure bitsandbytes is compatible.
4. Set `.env` from `.env.example` and set `HF_MODEL` and `OPENAI_API_KEY` if you want online fallback.
5. Run the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
6. (Optional) Run the frontend (requires npm/node):
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Notes
- The frontend assumes the FastAPI server is reachable at the same origin (development proxy or reverse proxy needed).
- The project still does NOT include model weights; transformers will auto-download on first run (internet required).
- For CPU-only servers, use smaller distilled models or explore ONNX/Optimum for better CPU throughput.
