# RAG Dokumentum: Modulok és Üzleti Logika

Ez a dokumentum összefoglalja a 9 modul legfontosabb üzleti logikáit.

  * **Modul 0 (Terméktörzs):** Komplex, többszintű módosítókat kezel (kötelező/opcionális, feláras). Árakat és láthatóságot kezel értékesítési csatornánként. Vertex AI-t használ fordításra, és GCS+Cloud Function folyamatot képkezelésre.
  * **Modul 1 (Rendeléskezelés):** Kezeli a többcsatornás rendeléseket. Kulcsfontosságú funkciója az NTAK-kompatibilis ÁFA váltás (27% -> 5%) nyitott rendeléseknél.
  * **Modul 2 (Asztalkezelés):** Vizuális asztaltérképet és személyre (seat) bontott rendelést tesz lehetővé.
  * **Modul 3 (KDS):** Valós időben jeleníti meg a rendelési tételeket a megfelelő konyhai állomáson.
  * **Modul 4 (Számlázás):** Támogatja a dinamikus fizetési módokat (SZÉP kártyák) és a számla személyenkénti felosztását. A rendelés lezárása itt váltja ki az NTAK küldést.
  * **Modul 5 (Készletkezelés):** Kettős készletkezelést valósít meg: egy automatikus, receptúra-alapú (perpetuális) és egy manuális, napi leltáron alapuló rendszert. Google Document AI-t használ a szállítói számlák beolvasására.
  * **Modul 6 (Munkatárs):** Finomhangolható jogosultságkezelést biztosít, de a munkaidő-nyilvántartás és bérszámfejtés kívül esik a rendszer hatáskörén.
  * **Modul 7 (CRM):** Hűségpontokat és törzsvevői hitelkeretet kezel. API kaput biztosít külső integrációkhoz.
  * **Modul 8 (Admin):** Felelős a kötelező NTAK adatszolgáltatásért ("Rendelésösszesítő", "Sztornó"), a digitális HACCP naplózásért és az offline működés szinkronizációjáért.
