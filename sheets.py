""" This module implements a bunch of functions to retrieve, parse and wrangle CAi's spreadsheets.
Every function has been implemented naively and are *not* optimized, so their results should always be cached.
The only side effects of the module are in the Google Sheets API endpoint log.

While the module does its best to handle possible edge cases, a million different things could go wrong with a simple change in the spreadsheet, so be advised to check for errors. """

from json import loads, load, dumps
import requests as r
from pprint import pprint
from googleapiclient import discovery
import pandas as pd
from ejemplos import academico_ordinario, academico_extraordinario

def setup_service():
    return discovery.build("sheets", "v4")


def get_range(service, id, range_):
    """ Receives a service instance for GoogleAPIClient, a spreadsheet ID and a Sheets range and returns the given cells as a list of lists. """

    assert isinstance(service, discovery.Resource)
    assert isinstance(id, str) and isinstance(range_, str)

    date_time_render_option = "SERIAL_NUMBER"

    return (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=id, range=range_, dateTimeRenderOption=date_time_render_option
        )
        .execute()
    )


def quantify_dates(dates):
    """Takes a Pandas Series of str dates in Spanish format (ex. "1/6/20") and quantifies them using approximate days. Returns a Series of integers."""
    assert isinstance(dates, pd.Series)
    for indice, date_str in enumerate(dates):
        date = [int(number) for number in date_str.split("/")]

        assert 1 <= date[0] <= 31
        assert 1 <= date[1] <= 12
        assert 0 <= date[2] <= 99  # if this lasts until 2099... xd

        # Note the approximation on the month
        dates[indice] = date[0] + date[1] * 30 + date[2] * 365
    return dates


##########################################
# Funciones para el Consejo Generacional #
##########################################


def get_generational(service, id):
    """ Gets the GoogleAPIClient service for GSheets and the ID of the CAi spreadsheet for the generational council.
    Receives an instance of discovery.Resource and an id str. Returns a list of lists with the sheet. """
    assert isinstance(service, discovery.Resource)
    assert isinstance(id, str)

    ordinarios = get_range(service, id, "A9:M37")["values"]
    ordinarios = fix_dates_g(normalizar_primera_col_g(ordinarios))
    extraordinarios = get_range(service, id, "'Consejos Extraordinarios'!A10:Q38")[
        "values"
    ]
    extraordinarios = fix_dates_g(normalizar_primera_col_g(extraordinarios))

    planilla = merge_and_sort_dates_g(ordinarios, extraordinarios)

    assert isinstance(planilla, list)
    return planilla


def normalizar_primera_col_g(planilla):
    """ Takes the first column for a generational council, repeats the merged cells and maps the roles to standarized names.
    Receives a sheet represented by a list of lists and returns a list of lists. """

    assert isinstance(planilla, list)

    for indice, linea in enumerate(planilla):
        if linea[0]:
            representa_a = linea[0]
        else:
            planilla[indice][0] = representa_a

    roles = {
        "consejeros territoriales": "CT",
        "cai": "CAI",
        "directiva": "CAI",
        "comite directivo": "CAI",
        "comité directivo": "CAI",
        "dg": "DG",
    }

    for indice, linea in enumerate(planilla[1:]):
        rol = linea[0].lower().strip()

        try:
            planilla[indice + 1][0] = roles[rol]
        except KeyError:
            try:
                planilla[indice + 1][0] = str(int(str(rol)))
            except ValueError:
                if "y ant" in rol:
                    planilla[indice + 1][0] = rol.strip(".") + "."
                else:
                    raise UncompatibleRole

    assert isinstance(planilla, list)
    return planilla


def fix_dates_g(planilla):
    """ Takes weird, seemingly unavoidable month names in spanish in the sheet and standarizes them as numbers.
    Receives a list of lists, returns a list of lists. """

    assert isinstance(planilla, list)

    meses = {
        "ene.": 1,
        "feb.": 2,
        "mar.": 3,
        "abr.": 4,
        "may.": 5,
        "jun.": 6,
        "jul.": 7,
        "ago.": 8,
        "sep.": 9,
        "oct.": 10,
        "nov.": 11,
        "dic.": 12,
    }
    header = planilla[0]
    for indice, fecha in enumerate(header[2:]):
        partes = fecha.split("-")
        if len(partes) == 3:
            try:
                partes[1] = str(meses[partes[1]])
            except KeyError:
                print("El formato entregado no divide las fechas como se esperaba.")
                print("Fecha procesada:", fecha)
                raise ValueError
            planilla[0][indice + 2] = "/".join(partes)
        elif not fecha:
            planilla[0][indice + 2] = "?"
            print("Fecha no encontrada en tabla, reemplazando por '?'")
        else:
            print("El formato entregado no calza el formato esperado.")
            print("Fecha procesada:", fecha)
            raise ValueError

    assert isinstance(planilla, list)
    return planilla


def sort_planilla_by_date_g(planilla_df):
    """ Receives a DataFrame and returns a list of lists. """
    assert isinstance(planilla_df, pd.DataFrame)
    izq = planilla_df.iloc[:, 0:2]
    fechas = planilla_df.iloc[:, 2:]
    fechas = fechas.sort_values(
        0, axis=1, key=lambda x: quantify_dates(x)
    )  # Sortea por los días cuantificados
    plantilla_df = pd.concat(
        [izq, fechas], axis=1
    )  # Une los nombres con las fechas ya sorteadas

    return plantilla_df.values.tolist()


def merge_and_sort_dates_g(p1, p2):
    """ Receives two lists and returns one list """
    assert isinstance(p1, list) and isinstance(p2, list)
    p1, p2 = pd.DataFrame(p1), pd.DataFrame(p2)
    planilla = pd.concat([p1, p2.iloc[:, 2:]], axis=1)
    return sort_planilla_by_date_g(planilla)


#######################################
# Funciones para el Consejo Académico #
#######################################


def sort_planilla_by_date_a(planilla_df):
    """ Receives a DataFrame and returns a list of lists. """
    assert isinstance(planilla_df, pd.DataFrame)
    izq = planilla_df.iloc[:, 0:2]
    fechas = planilla_df.iloc[:, 2:]
    fechas = fechas.sort_values(
        0, axis=1, key=lambda x: quantify_dates(x)
    )  # Sortea por los días cuantificados
    plantilla_df = pd.concat(
        [izq, fechas], axis=1
    )  # Une los nombres con las fechas ya sorteadas

    return plantilla_df.values.tolist()

def get_academic(service, id):
    """ Gets the GoogleAPIClient service for GSheets and the ID of the CAi spreadsheet for the academic council.
    Receives an instance of discovery.Resource and an id str. Returns a list of lists with the sheet. """
    assert isinstance(service, discovery.Resource)
    assert isinstance(id, str)

    # ordinarios = get_range(service, id, "CAO!A3:F43")["values"]
    ordinarios, extraordinarios = academico_ordinario, academico_extraordinario
    # remover DGs 2020 y 2019.
    ordinarios.pop(1)
    ordinarios.pop(1)
    extraordinarios.pop(1)
    extraordinarios.pop(1)

    print(pd.DataFrame(ordinarios))

    # ordinarios = fix_dates_g(normalizar_primera_col_g(ordinarios))

    # extraordinarios = get_range(service, id, "CAEx!A3:G43")["values"]
    # extraordinarios = fix_dates_g(normalizar_primera_col_g(extraordinarios))


    # planilla = merge_and_sort_dates_g(ordinarios, extraordinarios)

    # assert isinstance(planilla, list)
    # return planilla


service = setup_service()
get_academic(service, "1ditHP6pQUyAx73t_76csuJUH4t4TPqlRa5CHHWRXz3o")
