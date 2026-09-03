#!/usr/bin/env python3
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"


def ask_ollama(prompt: str) -> str:
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("response", "").strip()


def main() -> None:
    print("Chat IA local (escribe 'salir' para terminar)")
    while True:
        text = input("Tú: ").strip()
        if text.lower() in {"salir", "exit", "quit"}:
            break
        try:
            print("IA:", ask_ollama(text))
        except Exception as exc:
            print(f"Error consultando Ollama: {exc}")


if __name__ == "__main__":
    main()
