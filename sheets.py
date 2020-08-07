from json import loads, load, dumps
import requests as r
from pprint import pprint
from googleapiclient import discovery
import pandas as pd


generacional = "1USCGq_T6GfEC2662Z6iRrSzc1AAoMHM4W13ATAvFs54"


def setup_service():
    return discovery.build("sheets", "v4")


def get_range(service, id, range_):
    date_time_render_option = "SERIAL_NUMBER"
    return (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=id, range=range_, dateTimeRenderOption=date_time_render_option
        )
        .execute()
    )


def get_generational(service):
    ordinarios = get_range(service, generacional, "A9:M37")["values"]
    ordinarios = fix_dates(normalizar_primera_col(ordinarios))
    extraordinarios = get_range(
        service, generacional, "'Consejos Extraordinarios'!A10:Q38"
    )["values"]
    extraordinarios = fix_dates(normalizar_primera_col(extraordinarios))

    pprint(ordinarios)
    pprint(extraordinarios)


def normalizar_primera_col(planilla):
    for indice, linea in enumerate(planilla):
        if linea[0]:
            representa_a = linea[0]
        else:
            planilla[indice][0] = representa_a

    return planilla


def fix_dates(planilla):
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

    return planilla


service = setup_service()

get_generational(service)
