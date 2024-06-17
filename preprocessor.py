import pandas as pd
import numpy as np

class Preprocessor:
    PATH = "datasets"

    def __init__(self):
        pd.options.display.float_format = '{:,.2f}'.format

    def read_csv(self, file):
        file_to_read = self.PATH + "/" + file
        return pd.read_csv(file_to_read, sep=";", converters={"Total": lambda x: int(x.replace(".", "")) if x else ""})

    def process_data(self):
        population = self.read_csv("poblacion-provincia.csv")
        population = population.rename(columns={"Total": "Poblacion"})

        deaths = self.read_csv("defunciones.csv")
        deaths = deaths.rename(columns={"Total": "Defunciones"})

        births = self.read_csv("natalidad.csv")
        births = births.rename(columns={"Total": "Nacimientos"})

        crimes = self.read_csv("delitos.csv")
        crimes = crimes.rename(columns={"Total": "Delitos", "Sexo del infractor": "Sexo", "Lugar de condena": "Provincias"})
        
        return population, deaths, births, crimes

    def explore_data(self, df, name):
        print("\nEXPLORACION A", name.upper(), "\n")
        print(df)
        print("\nTipos\n")
        print(df.info())
        print("\nEstadisticas basicas\n")
        print(df.describe())
        print("\nNull values\n")
        print(df.isnull().sum())
        print("\nValue counts\n")
        print(pd.Series(df["Provincias"]).value_counts())
        print("")
        print(pd.Series(df["Sexo"]).value_counts())

    def calculate_mortality_rate(self, df):
        mortality_rates = []
        for _, row in df.iterrows():
            defunciones = pd.to_numeric(row["Defunciones"], errors='coerce')
            total = pd.to_numeric(row["Poblacion"], errors='coerce')
            
            if not np.isnan(defunciones) and not np.isnan(total) and total != 0:
                mortality_rates.append(round((defunciones / total) * 1000, 2))
            else:
                mortality_rates.append(np.nan)
        
        return pd.Series(mortality_rates)

    def calculate_birth_rate(self, df):
        birth_rates = []
        for _, row in df.iterrows():
            births = pd.to_numeric(row["Nacimientos"], errors="coerce")
            total = pd.to_numeric(row["Poblacion"], errors="coerce")

            if not np.isnan(births) and not np.isnan(total) and total != 0:
                birth_rates.append(round((births / total) * 1000, 2))
            else:
                birth_rates.append(np.nan)

        return pd.Series(birth_rates)

    def calculate_crime_rate(self, df):
        crime_rates = []
        for _, row in df.iterrows():
            crimes = pd.to_numeric(row["Delitos"],  errors="coerce")
            total = pd.to_numeric(row["Poblacion"], errors="coerce")

            if not np.isnan(crimes) and not np.isnan(total) and total != 0:
                crime_rates.append(round((crimes / total) * 1000, 2))
            else:
                crime_rates.append(np.nan)

        return pd.Series(crime_rates)
    
    def add_dash_after_space(self, s):
        return s.replace(r'(\d{2})\s', r'\1-', regex=True)
    
    def deleteNoResidentes(self, df):
        return df[df["Provincias"] != "No residente"]
    
    def changeNames(self, df):
        
        df["Provincias"] = df["Provincias"].replace("01 Araba/Álava", "01 Álava")
        df["Provincias"] = df["Provincias"].replace("07 Balears Illes", "07 Baleares")
        df["Provincias"] = df["Provincias"].replace("48 Bizkaia", "48 Vizcaya")
        df["Provincias"] = df["Provincias"].replace("15 Coruña A", "15 A Coruña")
        df["Provincias"] = df["Provincias"].replace("20 Gipuzkoa", "20 Guipúzcoa")
        df["Provincias"] = df["Provincias"].replace("35 Palmas Las", "35 Las Palmas")
        df["Provincias"] = df["Provincias"].replace("26 Rioja La", "26 La Rioja")

        df['Provincias'] = df['Provincias'].str.replace(r'(\d{2})\s', r'\1-', regex=True)

        return df
        