"""Container baslarken veritabani baglantisi hazir olana kadar bekler."""
import os
import sys
import time

import sqlalchemy
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///itsm.db")
MAX_RETRIES = 30
WAIT_SECONDS = 2


def wait_for_db():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))
            print("Veritabani baglantisi hazir.")
            return
        except OperationalError as exc:
            print(f"[{attempt}/{MAX_RETRIES}] Veritabani hazir degil, bekleniyor... ({exc.__class__.__name__})")
            time.sleep(WAIT_SECONDS)

    print("Veritabanina baglanilamadi, cikiliyor.")
    sys.exit(1)


if __name__ == "__main__":
    wait_for_db()
