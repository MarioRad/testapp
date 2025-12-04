from datetime import datetime
import pandas as pd

# Definimos las variantes
variante_2 = {16, 24, 22, 12, 8, 31}
variante_6 = {16, 42, 22, 31, 24, 29}

# Datos de ejemplo (pega más sorteos si querés ampliar)
data = """
Fecha	Tradicional	Segunda	Revancha	SiempreSale	Detalle
5/10/2025	05 32 06 44 09 34	06 20 44 45 13 25	22 21 19 15 03 43	26 06 41 20 45 30
1/10/2025	25 08 36 32 31 30	27 03 18 08 01 20	31 25 20 22 17 29	43 20 42 28 07 39
28/9/2025	22 14 02 09 30 31	33 13 18 12 04 10	02 18 15 07 22 27	38 12 28 23 33 11
24/9/2025	21 34 37 41 18 12	06 03 17 21 31 24	03 30 32 00 23 35	41 15 02 42 36 44
21/9/2025	01 16 19 21 35 38	23 20 37 30 11 21	41 11 37 24 45 30	45 25 21 14 18 29
17/9/2025	19 04 44 12 40 39	04 15 20 29 16 35	31 36 04 22 15 11	03 17 21 09 19 41
"""

# Procesar los datos
rows = data.strip().split('\n')[1:]
records = []
for row in rows:
    parts = row.split('\t')
    if len(parts) >= 4:
        fecha = datetime.strptime(parts[0], "%d/%m/%Y")
        revancha_nums = set(map(int, parts[3].split()))
        records.append({
            "fecha": fecha,
            "revancha": revancha_nums,
            "v2_aciertos": len(variante_2 & revancha_nums),
            "v6_aciertos": len(variante_6 & revancha_nums)
        })

# Convertimos a DataFrame
df = pd.DataFrame(records)

# Conteo de aciertos por variante
v2_counts = df["v2_aciertos"].value_counts().sort_index()
v6_counts = df["v6_aciertos"].value_counts().sort_index()

# Mostrar resultados
print("Resultados por sorteo:")
print(df[["fecha", "v2_aciertos", "v6_aciertos"]])

print("\nResumen Variante 2:")
print(v2_counts)

print("\nResumen Variante 6:")
print(v6_counts)
