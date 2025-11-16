# Mikroszolgáltatás Architektúra

A rendszer 9 logikai modulra van bontva, melyek különálló, de együttműködő mikroszolgáltatásként működnek.

## API Gateway:

Minden külső kérés (frontend, külső partnerek) egyetlen API Gateway-en keresztül érkezik. Ez felel a kérések továbbításáért a megfelelő mikroszolgáltatáshoz, az authentikációért (JWT token validálás), a rate limitingért és a kérések logolásáért.
Javasolt technológia: Google Cloud API Gateway.

## Szolgáltatások közötti kommunikáció:

1. **Szinkron (REST API):** Amikor egy szolgáltatásnak azonnali válaszra van szüksége egy másiktól (pl. a Rendeléskezelő lekérdezi a Terméktörzs-től egy termék árát), a szolgáltatások közvetlenül, a belső hálózaton keresztül kommunikálnak REST API hívásokkal.
2. **Aszinkron (Eseményvezérelt):** A nem időkritikus, de garantáltan végrehajtandó folyamatokhoz (pl. "Rendelés lezárva" esemény, ami kiváltja a készletcsökkentést és az NTAK adatszolgáltatást), a rendszer Google Pub/Sub-ot használ. Ez a megközelítés növeli a rendszer rugalmasságát és hibatűrését.

## AI Fordítási Folyamat (Modul 0):

1. A felhasználó a Frontend Admin felületen módosít egy termék nevét vagy leírását.
2. A Frontend elküldi a kérést az API Gateway-en keresztül a Terméktörzs Szolgáltatás-nak.
3. A Terméktörzs Szolgáltatás elmenti az alapnyelvű (magyar) szöveget az adatbázisba.
4. Aszinkron módon meghívja a Vertex AI Translation LLM API-t az EN és DE nyelvekre.
5. A kapott fordításokat visszaírja a `products` tábla `translations` JSONB oszlopába.

## AI Képkezelési Architektúra (Modul 0):

1. A Frontend egy authentikált kérést küld a Terméktörzs Szolgáltatás-nak, hogy képet szeretne feltölteni egy termékhez.
2. A szolgáltatás generál egy Google Cloud Storage (GCS) Signed URL-t, ami egy rövid ideig érvényes, biztonságos feltöltési link, és visszaadja a frontendnek.
3. A Frontend közvetlenül a GCS-re tölti fel a képet ezzel az URL-lel, tehermentesítve a backend szolgáltatást.
4. A GCS-en a sikeres feltöltés eseményt generál, ami automatikusan elindít egy Google Cloud Function-t.
5. Ez a Cloud Function (Python runtime + Pillow library) letölti a feltöltött képet, létrehozza a szükséges méreteket (pl. thumbnail 200x200, medium 800x800), majd visszatölti őket a GCS-be egy másik mappába.
6. A kép URL-eket (az eredetit és az átméretezetteket) egy Cloud CDN-en keresztül szolgáltatjuk ki, ami biztosítja a globálisan gyors betöltést és a cache-elést. Az URL-eket a Terméktörzs Szolgáltatás menti el az `image_assets` táblába.
