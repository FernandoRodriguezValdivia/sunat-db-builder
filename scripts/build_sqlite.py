import os
import sqlite3
import zipfile
import requests
from tqdm import tqdm


URL = "http://www2.sunat.gob.pe/padron_reducido_ruc.zip"

ZIP_FILE = "padron_reducido_ruc.zip"

OUTPUT_DIR = "output"

DB_FILE = f"{OUTPUT_DIR}/sunat.sqlite"


os.makedirs(OUTPUT_DIR, exist_ok=True)



def download():

    print("Descargando ZIP...")

    r = requests.get(URL, stream=True)

    total = int(r.headers.get("content-length", 0))

    with open(ZIP_FILE, "wb") as f:

        for chunk in tqdm(
            r.iter_content(chunk_size=1024*1024),
            total=total//1024//1024,
            unit="MB"
        ):
            f.write(chunk)



def create_db():

    print("ENTRANDO A CREATE_DB", flush=True)

    print("Abriendo ZIP...", flush=True)


    conn = sqlite3.connect(DB_FILE)

    cur = conn.cursor()


    cur.execute("""
    CREATE TABLE empresas(

        ruc TEXT PRIMARY KEY,
        nombre TEXT,
        estado TEXT,
        condicion TEXT

    )
    """)


    conn.commit()


    with zipfile.ZipFile(ZIP_FILE) as z:
        print("ZIP abierto", flush=True)

        print(z.namelist(), flush=True)

        txt = z.namelist()[0]

        with z.open(txt) as file:

            header = file.readline()


            batch=[]

            count = 0

            for line in file:

                count += 1

                if count % 500000 == 0:
                    print(
                        f"Procesados: {count}",
                        flush=True
                    )

                row=line.decode(
                    "utf-8",
                    errors="ignore"
                ).strip().split("|")


                batch.append(
                    (
                    row[0],
                    row[1],
                    row[2],
                    row[3]
                    )
                )


                if len(batch)>=10000:

                    cur.executemany(
                    """
                    INSERT INTO empresas
                    VALUES (?,?,?,?)
                    """,
                    batch
                    )

                    conn.commit()

                    batch=[]


            if batch:

                cur.executemany(
                """
                INSERT INTO empresas
                VALUES (?,?,?,?)
                """,
                batch
                )

                conn.commit()


    conn.close()



download()

print("PASO 1: descarga finalizada", flush=True)

print(
    "Tamaño ZIP:",
    os.path.getsize(ZIP_FILE),
    flush=True
)

create_db()


print("LISTO")