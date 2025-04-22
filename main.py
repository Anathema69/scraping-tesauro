# main.py
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper import scrape_page

def main():
    TOTAL_PAGES = 20   # ajustar según necesidad
    pages = list(range(1, TOTAL_PAGES + 1))
    progress = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_page = {executor.submit(scrape_page, p): p for p in pages}
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                result = future.result()
                progress.extend(result)
                print(f"[✔] Página {page}: {len(result)} tarjetas procesadas")
            except Exception as e:
                print(f"[✖] Error en página {page}: {e}")

    # Guardar log de avance
    with open("progress.json", "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    print("Log guardado en progress.json")

if __name__ == "__main__":
    main()
