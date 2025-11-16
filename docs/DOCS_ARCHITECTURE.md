# RAG Dokumentum: Architektúra

Ez a dokumentum a rendszer magas szintű architektúráját írja le, a ChatGPT RAG képességeihez optimalizálva.

A rendszer egy mikroszolgáltatás-alapú architektúrát követ, amely 9 fő szolgáltatásra bomlik. A kommunikáció egy központi API Gateway-en keresztül történik, ami a Google Cloud API Gateway. A frontend alkalmazások (React) ezt a gateway-t hívják.

A szolgáltatások közötti kommunikáció kétféle lehet: szinkron REST API hívások a belső hálózaton (gyors, azonnali választ igénylő feladatokhoz) és aszinkron események Google Pub/Sub segítségével (hibatűrő, lazán csatolt folyamatokhoz, mint a készletcsökkentés rendelés után).

Az AI-alapú funkciók szorosan integrálódnak a Google Cloud platformba:

  * **Képkezelés:** GCS Signed URL-ek a biztonságos feltöltéshez, amit egy Cloud Function dolgoz fel (Pillow könyvtárral), és a Cloud CDN szolgáltat ki globálisan.
  * **Fordítás:** A Vertex AI Translation LLM API biztosítja a menüelemek kontextus-érzékeny fordítását.
  * **Számlaolvasás:** A Google Document AI Invoice Parser automatikusan kinyeri az adatokat a feltöltött szállítói számlákból.
