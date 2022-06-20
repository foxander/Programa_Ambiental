# -*- coding: utf-8 -*-

import input_date
import funtions_aux
import arcpy
import os

dike = {}
dike['AVG'] = []
dike['NAV'] = []
dike['IBI'] = []
dike['BAB'] = []
dike['BAR'] = []
dike['MOG'] = []
dike['PRO'] = []
dike['LMO'] = []
dike['EUC'] = []
dike['CAC'] = []

def calc():
    have = 0

    for i in dike.keys():
        flag = 1
        for rastername in dike[i]:
            water_dam = {} #Dicionário das águas
            aux = rastername[0:3]
            years = rastername[4:]
            sum_water = 0
            sum_macrofitas = 0
            waters = 0
            macrofitas = 0
            clody = solo = veget = flutuante = emersas = agua1 = agua2 = agua3 = False

            sensor = input_date.dict_sensor[rastername][0]

            if not sensor:
                sensor = ""

            if flag:
                funtions_aux.savelog("Analisando os dados da barragem de " + input_date.barragens[aux] + "...", 1)
                funtions_aux.savelog("Ano: " + years, 1)
                flag = 0
                have = 1
            else:
                funtions_aux.savelog("     " + years, 1)

            #Get the Date
            date = arcpy.da.SearchCursor(input_date.IMA_VECTOR_GDB + "\\" + rastername, ("Date")).next()[0]

            data_i = ""
            data_f = ""

            #Consertar datas trocadas, duplicadas, calcular data inicial e final
            date, data_i, data_f = funtions_aux.date_analisy(date, 1)

            rows = arcpy.InsertCursor(input_date.Estatistica_Pivot)
            rowp = rows.newRow()
            rows.insertRow(rowp)
            del rows

            calculateFieldExpression  = "'"+sensor+"'"
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Satelite", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            calculateFieldExpression  = "'"+aux+"'"
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "UHE", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            aux = rastername[4:8]
            calculateFieldExpression  = "'"+aux+"'"
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Ano", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            calculateFieldExpression  = "'"+date+"'"
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Periodo", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            calculateFieldExpression  = "'"+data_i+"'"
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Data_Inicial", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            calculateFieldExpression  = "'"+data_f+"'"
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Data_Final", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            aux = rastername[9:11]
            calculateFieldExpression  = "'"+aux+"'"
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Epoca", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            calculateFieldExpression = "Reclass(!Epoca!)"
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Estacao", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = input_date.codeblock2)

            with arcpy.da.SearchCursor(input_date.IMA_VECTOR_GDB + "\\" + rastername, ['Classe','Perc_Area','Area_ha']) as cursor:
                for row in cursor:
                    exp = "{}".format(row[2])
                    if row[1] < 0.01: #Evitar o Zero na porcentagem
                        calculateFieldExpression = "{:.5f}".format(row[1])
                    else:
                        calculateFieldExpression = "{:.2f}".format(row[1])
                    if "Agua 1" in row[0]:
                        waters += row[2]
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Agua_1", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Agua_1", expression = exp, expression_type = "PYTHON3", code_block = "")
                        agua1 = True
                    elif "Agua 2" in row[0]:
                        waters += row[2]
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Agua_2", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Agua_2", expression = exp, expression_type = "PYTHON3", code_block = "")
                        agua2 = True
                    elif "Agua 3" in row[0]:
                        waters += row[2]
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Agua_3", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Agua_3", expression = exp, expression_type = "PYTHON3", code_block = "")
                        agua3 = True
                    elif "Solo" in row[0]:
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Solo", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Solo", expression = exp, expression_type = "PYTHON3", code_block = "")
                        solo = True
                    elif "Vegetacao" in row[0]:
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Vegetacao", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Vegetacao", expression = exp, expression_type = "PYTHON3", code_block = "")
                        veget = True
                    elif "Nuvem" in row[0]:
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Nuvem", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Nuvem", expression = exp, expression_type = "PYTHON3", code_block = "")
                        clody = True
                    elif "Emersa_Mista" in row[0]:
                        macrofitas += row[2]
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Emersa_Mista", expression = exp, expression_type = "PYTHON3", code_block = "")
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Emersa_Mista", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                        emersas = True
                    elif "Flutuante" in row[0]:
                        macrofitas += row[2]
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Flutuante", expression = exp, expression_type = "PYTHON3", code_block = "")
                        arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Flutuante", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                        flutuante = True

                    if "Agua 1" in row[0] or "Agua 2" in row[0] or "Agua 3" in row[0] or "Nuvem" in row[0]:
                        sum_water += row[1]

                    if "Emersa_Mista" in row[0] or "Flutuante" in row[0]:
                        sum_macrofitas += row[1]

            calculateFieldExpression = "0"

            if not clody:
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Nuvem", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Nuvem", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            if not veget:
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Vegetacao", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Vegetacao", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            if not solo:
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Solo", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Solo", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            if not emersas:
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Emersa_Mista", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Emersa_Mista", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            if not flutuante:
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Flutuante", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Flutuante", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            if not agua1:
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Agua_1", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Agua_1", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            if not agua2:
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Agua_2", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Agua_2", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            if not agua3:
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Agua_3", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")
                arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Agua_3", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            calculateFieldExpression = "{:.2f}".format(sum_water)
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Agua", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            calculateFieldExpression = "{:.2f}".format(sum_macrofitas)
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Perc_Macrofita", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")

            # Soma das Águas
            exp = "{}".format(waters)
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Agua", expression = exp, expression_type = "PYTHON3", code_block = "")

            # Soma das Macrofitas
            exp = "{}".format(macrofitas)
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field = "Area_Macrofita", expression = exp, expression_type = "PYTHON3", code_block = "")

            # Cria Área do Reservatório
            area_total_reservatorio = input_date.grade_espelhodagua + "\\" + rastername[0:3] + "_MASC_MAX"
            area_total = arcpy.da.SearchCursor(area_total_reservatorio, ("Shape_Area")).next()[0]
            exp = "{}".format(area_total/10000) #Em hactares
            arcpy.CalculateField_management(input_date.Estatistica_Pivot, field="Area_UHE", expression=exp, expression_type="PYTHON3", code_block="")

            fields_valid = funtions_aux.get_field_valid(input_date.Estatistica_Pivot)
            fieldCount = len(fields_valid)

            #Check se existem Null values
            with arcpy.da.UpdateCursor(input_date.Estatistica_Pivot, fields_valid) as curU:
                for row in curU:
                    for field_ in range(fieldCount):
                        if row[field_] == None:
                            row[field_] = "0"
                    curU.updateRow(row)
                del curU

            arcpy.Append_management(inputs = input_date.Estatistica_Pivot, target=input_date.Estatistica_UHE, schema_type="NO_TEST") #, field_mapping=r"UHE 'UHE' true true false 255 Text 0 0,First,#," + input_date.Freq_Temp + ",UHE,0,255;Ano 'Ano' true true false 255 Text 0 0,First,#," + input_date.Freq_Temp + ",Ano,0,255;Periodo 'Periodo' true true false 255 Text 0 0,First,#," + input_date.Freq_Temp + ",Periodo,0,255;Epoca 'Epoca' true true false 255 Text 0 0,First,#," + input_date.Freq_Temp + ",Epoca,0,255;Estacao 'Estacao' true true false 255 Text 0 0,First,#," + input_date.Freq_Temp + ",Estacao,0,255;Area_UHE 'Area_UHE' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Area_UHE,-1,-1," + input_date.Freq_Temp + ",Area_UHE,-1,-1," + input_date.Freq_Temp + ",Area_UHE,-1,-1;Agua_1 'Agua 1' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Agua_1,-1,-1," + input_date.Freq_Temp + ",Agua_1,-1,-1," + input_date.Freq_Temp + ",Agua_1,-1,-1;Agua_2 'Agua 2' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Agua_2,-1,-1," + input_date.Freq_Temp + ",Agua_2,-1,-1," + input_date.Freq_Temp + ",Agua_2,-1,-1;Agua_3 'Agua 3' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Agua_3,-1,-1," + input_date.Freq_Temp + ",Agua_3,-1,-1," + input_date.Freq_Temp + ",Agua_3,-1,-1;Agua 'Agua' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Agua,-1,-1," + input_date.Freq_Temp + ",Agua,-1,-1," + input_date.Freq_Temp + ",Agua,-1,-1;Solo 'Solo' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Solo,-1,-1," + input_date.Freq_Temp + ",Solo,-1,-1,"   + input_date.Freq_Temp + ",Solo,-1,-1;Vegetação 'Vegetação' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Vegetação,-1,-1," + input_date.Freq_Temp + ",Vegetação,-1,-1,"+ input_date.Freq_Temp + ",Vegetação,-1,-1;Flutuante 'Flutuante' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Flutuante,-1,-1,"   + input_date.Freq_Temp + ",Flutuante,-1,-1," + input_date.Freq_Temp + ",Flutuante,-1,-1;Emersa__Mista 'Emersa__Mista' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Emersa__Mista,-1,-1,"   + input_date.Freq_Temp + ",Emersa__Mista,-1,-1,"   + input_date.Freq_Temp + ",Emersa / Mista,-1,-1;Nuvem 'Nuvem' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Nuvem,-1,-1,"   + input_date.Freq_Temp + ",Nuvem,-1,-1,"   + input_date.Freq_Temp + ",Nuvem,-1,-1;Perc_Agua_1 'Perc_Agua_1' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_1,-1,-1;Perc_Agua_2 'Perc_Agua_2' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_2,-1,-1;Perc_Agua_3 'Perc_Agua_3' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1," + input_date.Freq_Temp + ",Perc_Agua_3,-1,-1;Perc_Agua 'Perc_Agua' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Perc_Agua,-1,-1," + input_date.Freq_Temp + ",Perc_Agua,-1,-1," + input_date.Freq_Temp + ",Perc_Agua,-1,-1," + input_date.Freq_Temp + ",Perc_Agua,-1,-1," + input_date.Freq_Temp + ",Perc_Agua,-1,-1," + input_date.Freq_Temp + ",Perc_Agua,-1,-1," + input_date.Freq_Temp + ",Perc_Agua,-1,-1," + input_date.Freq_Temp + ",Perc_Agua,-1,-1," + input_date.Freq_Temp + ",Perc_Agua,-1,-1;Perc_Macrofita 'Perc_Macrofitas' true true false 8 Double 0 0,First,#," + input_date.Freq_Temp + ",Perc_Macrofita,-1,-1," + input_date.Freq_Temp + ",Perc_Macrofita,-1,-1," + input_date.Freq_Temp + ",Perc_Macrofita,-1,-1," + input_date.Freq_Temp + ",Perc_Macrofita,-1,-1", subtype="", expression="")

            if not input_date.Acumular_Estatisticas:
                arcpy.Append_management(inputs = input_date.Estatistica_Pivot, target=input_date.Estatistica_Temp, schema_type="NO_TEST")

            arcpy.TruncateTable_management(input_date.Estatistica_Pivot) # Apaga todas as linhas

    if input_date.Acumular_Estatisticas:
        if not "*" in input_date.barragem_filtro:
            calculateFieldExpression  = "UHE = '"+input_date.barragem_filtro+"'"
            seletion = arcpy.management.SelectLayerByAttribute(input_date.Estatistica_UHE, "NEW_SELECTION", calculateFieldExpression, None)
            arcpy.Append_management(inputs = seletion, target=input_date.Estatistica_Temp, schema_type="NO_TEST")
    if have:
        funtions_aux.calculate_ocupation(input_date.Estatistica_UHE) # Faz somente se inseriu dados novos
        funtions_aux.savelog("Analises realizadas com sucesso!", 1)

#----- Análise dos Dados
def analise_barragens():
    try:
        arcpy.env.workspace = input_date.IMA_VECTOR_GDB

        arcpy.TruncateTable_management(input_date.Estatistica_Temp) # Apaga todas as linhas
        arcpy.TruncateTable_management(input_date.Estatistica_Pivot) # Apaga todas as linhas

        dike['AVG'] = []
        dike['NAV'] = []
        dike['IBI'] = []
        dike['BAB'] = []
        dike['BAR'] = []
        dike['MOG'] = []
        dike['PRO'] = []
        dike['LMO'] = []
        dike['EUC'] = []
        dike['CAC'] = []

        featureclasses = sorted (arcpy.ListFeatureClasses())

        for rastername in featureclasses:

            if not "*" in input_date.barragem_filtro:    #Filtro por barragem
                filter_barrgem = rastername.split("_")[0]
                if not input_date.barragem_filtro in filter_barrgem:
                    continue

            # Filtro caso houver
            if not "*" in input_date.filter_year:       #filtro por ano e quadrante
                filter_ = rastername[4:]
                if not input_date.filter_year in filter_:
                    continue
                else:
                    if len (input_date.filter_year) > 4:
                        station = filter_.split("_")[-1]
                        station_filter = input_date.filter_year.split("_")[-1]
                        year_1 = filter_.split("_")[-2]
                        year_2 = input_date.filter_year.split("_")[-2]
                        if not station == station_filter:
                            continue
                        if not year_1 == year_2:
                            continue

            #Check se existem linhas
            funtions_aux.check_update_table(rastername[0:3], rastername[4:8], rastername[9:11])

            if 'AGV_' in rastername:
                dike['AVG'].append(rastername)
                continue
            if 'NAV_' in rastername:
                dike['NAV'].append(rastername)
                continue
            if 'BAB_' in rastername:
                dike['BAB'].append(rastername)
                continue
            if 'BAR_' in rastername:
                dike['BAR'].append(rastername)
                continue
            if 'EUC_' in rastername:
                dike['EUC'].append(rastername)
                continue
            if 'CAC_' in rastername:
                dike['CAC'].append(rastername)
                continue
            if 'LMO_' in rastername:
                dike['LMO'].append(rastername)
                continue
            if 'MOG_' in rastername:
                dike['MOG'].append(rastername)
                continue
            if 'IBI_' in rastername:
                dike['IBI'].append(rastername)
                continue
            if 'PRO_' in rastername:
                dike['PRO'].append(rastername)
                continue

        calc()

        if input_date.table_estatistica_excel:
            funtions_aux.export_excel()

        arcpy.TruncateTable_management(input_date.Estatistica_Temp) # Apaga todas as linhas

    except Exception as e:
        arcpy.AddError("Não foi possível cálcular as estatísticas.")
        arcpy.AddError(e)


