import os
import sqlite3
import zipfile
import requests
from tqdm import tqdm


URL = "URL_DEL_ZIP_SUNAT"

ZIP_FILE = "padron.zip"

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

    print("Creando SQLite...")


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

        txt = z.namelist()[0]

        with z.open(txt) as file:

            header = file.readline()


            batch=[]


            for line in file:

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
create_db()


print("LISTO")