# Kichkina tabib

Telegram bot: istalgan matn, iqtibos yoki tabrikni chiroyli rasmli
kartochkaga aylantirib beradi. Dizayn — asimmetrik jurnal uslubi (editorial
layout), organik gul illyustratsiyasi va mavzuga mos palitra/ikonka bilan.

## Ishga tushirish

```bash
pip install -r requirements.txt
cp .env.example .env   # BOT_TOKEN ni @BotFather dan olingan token bilan to'ldiring
python3 bot.py
```

## Qanday ishlaydi

- Foydalanuvchi matn yuboradi (ixtiyoriy: oxiriga `— Muallif` qo'shib).
- `imagegen/` matn (+ muallif) asosida mavzuni aniqlaydi (tug'ilgan kun,
  sevgi, hikmat, diniy, muvaffaqiyat, ...) va mos palitra + ikonka +
  sarlavha tanlaydi (`imagegen/occasions.py`).
- `imagegen/editorial.py` yakuniy kartochkani chizadi: gradient fon, organik
  gul buketi (`draw_bouquet`), nafis tipografiya.
- Bot inline tugmalar orqali qayta generatsiya ("🔄 Boshqa dizayn") va
  format almashtirish (kvadrat ↔ vertikal status) imkonini beradi.

## Loyihaning tuzilishi

```
bot.py              - Telegram bot (python-telegram-bot)
quote_parser.py      - matndan muallifni ajratib olish
config.py            - .env dan sozlamalarni o'qish
imagegen/
  editorial.py        - asosiy rasm chizish (fon, bulet, tipografiya)
  occasions.py         - mavzu -> palitra/sarlavha/teg xaritasi
  icons.py              - kichik chiziqli ikonalar (yurak, tort, kitob, ...)
  card.py                - yuqori darajadagi compose_card/compose_status
  themes.py, engine.py, layout.py - eski/yordamchi renderlash qatlami
```
