### Audit Jelentés: CRM Admin UI
* Állapot: INKONZISZTENCIA (Javítva)
* Talált Hibák:
    * **Helytelen GiftCard PIN validáció**: A `GiftCardEditor.tsx` nem validálta a PIN kódot kliensoldalon, mielőtt elküldte volna a backendnek. Ezt a hibát javítottam.
