import pandas as pd

# Lê a aba de ligação PAN <-> espécie do arquivo ODS
df_especies = pd.read_excel(
    r"C:\Users\Merinho Gatinho\Downloads\20251112_tabelapandadosabertos.ods",
    sheet_name="20251112-tabelaPanEspecies",
    engine="odf"
)

print(df_especies.shape)
print(df_especies.columns.tolist())
print(df_especies.head(10))

# Checagem de qualidade que fizemos
print("Nulos:", df_especies.isnull().sum())
print("IDs únicos:", df_especies["idTaxon"].nunique(), "de", len(df_especies))
print("Duplicatas:", df_especies.duplicated().sum())