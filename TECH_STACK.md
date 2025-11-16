# Technológiai Választások (Tech Stack) - 2025. November

Ez a dokumentum rögzíti a projekt technológiai választásait és azok rövid indoklását. A választások a teljesítményt, a fejlesztői hatékonyságot és a Google Cloud ökoszisztémával való szoros integrációt helyezték előtérbe.

| Komponens | Választott Technológia | Verzió (Stabil, 2025 Q4) | Indoklás |
|---|---|---|---|
| **Backend** | **Python (FastAPI)** | `0.115.x` | A FastAPI aszinkron képességei és kiemelkedő teljesítménye ideális a nagy terhelésű mikroszolgáltatásokhoz. Az automatikus OpenAPI dokumentáció-generálás felgyorsítja az API-k fejlesztését és az ágensek közötti kommunikációt. Python kiterjedt AI/ML könyvtárai előnyt jelentenek. |
| **Adatbázis** | **PostgreSQL** | `17.x` | A POS rendszer tranzakcionális természete (rendelések, fizetések, készlet) erős adatkonzisztenciát (ACID) követel meg, amiben a relációs adatbázisok, mint a PostgreSQL, kiválóak. A `JSONB` adattípus elegendő rugalmasságot biztosít a Modul 0 komplex, dinamikus módosítóinak kezeléséhez anélkül, hogy a relációs integritást feláldoznánk. |
| **Frontend** | **React (Vite)** | `19.x` (React), `6.x` (Vite) | A React hatalmas ökoszisztémája, komponens-alapú architektúrája és a Vite villámgyors fejlesztői környezete a legproduktívabb választás egy komplex, interaktív UI létrehozásához. |
| **AI Képkezelés** | **GCS + Cloud Functions + Pillow** | `N/A` | Ez a Google Cloud natív stack rendkívül skálázható és költséghatékony. A GCS a tárolásért, a Cloud Functions a szervermentes, eseményvezérelt képfeldolgozásért (Pillow könyvtárral), a Cloud CDN pedig a globális, gyors kiszolgálásért felel. |
| **AI Fordítás** | **Vertex AI Translation LLM API** | `v2 (stable)` | Közvetlen integráció a Google Cloud ökoszisztémába. A legújabb generációs LLM-alapú fordító modellek sokkal pontosabb és kontextus-érzékenyebb fordítást biztosítanak a hagyományos API-knál. |
| **AI Számlaolvasás (OCR)** | **Google Document AI (Invoice Parser)** | `v2 (stable)` | A Document AI egy célzott, előre tréningezett megoldás számlák feldolgozására. Pontossága és képessége a strukturált adatok (tételek, árak, szállító) kinyerésére messze felülmúlja az általános OCR megoldásokat, minimalizálva a manuális adatbevitelt. |
