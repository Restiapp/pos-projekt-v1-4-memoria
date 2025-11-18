### Audit Jelentés: CRM Admin UI
* Állapot: INKONZISZTENCIA
* Talált Hibák:
    * **Hibás mezőnév: 'usage_limit' helyett 'max_uses'**: A `CouponEditor.tsx` komponens a `usage_limit` mezőt küldi a backendnek, de a backend a `max_uses` mezőt várja.
    * **Helytelen GiftCard PIN validáció**: A `GiftCardEditor.tsx` nem validálja a PIN kódot, mielőtt elküldené a backendnek.
    * **Inkonzisztens DiscountType enumok**: A `CouponEditor.tsx`-ben a `DiscountType` enumok nem egyeznek a backend `DiscountTypeEnum` definíciójával.
