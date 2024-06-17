import preprocessor as p
import pandas as pd

preprocessor = p.Preprocessor()
population, deaths, births, crimes = preprocessor.process_data()

preprocessor.explore_data(population, "POBLACION")
preprocessor.explore_data(deaths, "DEFUNCIONES")
preprocessor.explore_data(births, "NACIMIENTOS")
preprocessor.explore_data(crimes, "DELITOS")

dataset = pd.merge(population, deaths, on=["Provincias", "Sexo", "Periodo"], how="outer")
dataset = pd.merge(dataset, births, on=["Provincias", "Sexo", "Periodo"], how="outer")
dataset = pd.merge(dataset, crimes, on=["Provincias", "Sexo", "Periodo"], how="outer")

dataset["Poblacion"] = dataset["Poblacion"].replace("", pd.NA)
dataset["Poblacion"] = dataset["Poblacion"].astype("Int64")
dataset["Delitos"] = dataset["Delitos"].astype("Int64")
dataset["Tasa de mortalidad"] = preprocessor.calculate_mortality_rate(dataset)
dataset["Tasa de natalidad"] = preprocessor.calculate_birth_rate(dataset)
dataset["Tasa de criminalidad"] = preprocessor.calculate_crime_rate(dataset)

dataset = preprocessor.deleteNoResidentes(dataset)
dataset = preprocessor.changeNames(dataset)

preprocessor.explore_data(dataset, "DATASET")

dataset.to_csv("datasets/out.csv")