# ITSM Talep Yonetim Sistemi (Ogrenme Projesi)

ManageEngine ServiceDesk Plus benzeri, kucuk capli bir **BT talep/ticket takip sistemi**.
Python (Flask) + PostgreSQL ile yazilmis, Docker ve docker-compose ile calisir.

## Ozellikler

- Kullanici kayit / giris (Flask-Login), rol tabanli yetkilendirme: `user`, `agent`, `admin`
- Talep (ticket) olusturma, listeleme, filtreleme (durum / oncelik / kategori)
- Talep detayinda yorum (comment) ekleme
- Agent/Admin icin: durum guncelleme, oncelik degistirme, personel atama
- Admin panelinde kategori yonetimi ve kullanici rol yonetimi
- Basit istatistik paneli (dashboard)
- PostgreSQL veritabani, Docker Compose ile tek komutla ayaga kalkar

## Proje Yapisi

```
itsm-project/
├── app/
│   ├── __init__.py        # Flask app factory + CLI (seed-db)
│   ├── extensions.py      # db, login_manager
│   ├── models.py          # User, Category, Ticket, Comment
│   ├── forms.py           # WTForms formlari
│   ├── routes/
│   │   ├── auth.py        # login / register / logout
│   │   ├── main.py        # dashboard
│   │   ├── tickets.py     # ticket CRUD + yorumlar
│   │   └── admin.py       # kategori & kullanici yonetimi
│   ├── templates/         # Jinja2 + Bootstrap 5 sablonlari
│   └── static/css/style.css
├── config.py
├── wsgi.py                # Gunicorn giris noktasi
├── wait_for_db.py         # Container baslarken DB'yi bekler
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Calistirma (Docker ile - onerilen)

1. `.env` dosyasini olusturun (ornek dosya zaten `.env` olarak kopyalanmis durumda, isterseniz duzenleyin):

   ```bash
   cp .env.example .env
   ```

2. Container'lari build edip ayaga kaldirin:

   ```bash
   docker compose up --build
   ```

   Bu komut:
   - PostgreSQL container'ini baslatir (`db`)
   - Web container'i veritabaninin hazir olmasini bekler (`wait_for_db.py`)
   - `flask seed-db` komutu ile tablolari olusturur ve varsayilan admin + kategorileri ekler
   - Gunicorn ile Flask uygulamasini `0.0.0.0:5000` uzerinde baslatir

3. Tarayicidan acin: **http://localhost:5000**

4. Varsayilan admin girisi (`.env` dosyasindaki degerler):
   - Kullanici adi: `admin`
   - Sifre: `Admin123!`

   > Ilk giristen sonra guvenlik icin sifreyi degistirmeniz onerilir (yeni bir rol yonetimi/sifre degistirme
   > ekrani eklemek istersen bu, projeyi genisletmek icin iyi bir alistirma olur).

5. Durdurmak icin: `Ctrl+C`, container'lari tamamen kaldirmak icin: `docker compose down`
   (verileri de silmek isterseniz: `docker compose down -v`)

## Rutin Kullanim Akisi

- **user** rolundeki biri kayit olur, giris yapar, "Yeni Talep" ile ticket acar.
- **agent** veya **admin** rolundeki biri talebi gorur, kendine atar, durumunu
  `Acik -> Islemde -> Cozuldu -> Kapatildi` seklinde ilerletir, yorum ekler.
- **admin**, `/admin/categories` ve `/admin/users` sayfalarindan kategori ekleyip
  kullanicilarin rolunu degistirebilir (orn. bir kullaniciyi `agent` yapmak icin).

## Docker Olmadan (lokal Python ile) Calistirma

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# DATABASE_URL'i sqlite'a cevirin (sqlite:///itsm.db) veya lokal bir postgres kullanin
export DATABASE_URL=sqlite:///itsm.db
export FLASK_APP=wsgi.py
export FLASK_SECRET_KEY=dev-secret

flask seed-db
flask run
```

## Ogrenme icin genisletme fikirleri

- SLA / son teslim tarihi (due date) alani ve gecikme uyarilari
- E-posta bildirimleri (talep olusturuldugunda / durum degistiginde)
- Dosya eki yukleme (ticket'a screenshot vb. eklemek)
- Talep gecmisi / audit log (kim ne zaman neyi degistirdi)
- REST API (Flask-RESTX / Flask-Smorest) ekleyip Postman ile test etmek
- Basit arama (baslik/aciklama icinde full-text search)
- Unit test yazmak (pytest + Flask test client)

## Kullanilan Teknolojiler

- Python 3.11, Flask 3
- Flask-SQLAlchemy, Flask-Login, Flask-WTF
- PostgreSQL 16 (Docker), Gunicorn
- Bootstrap 5 (CDN) - frontend
