# -*- coding: utf-8 -*-

import datetime
import input_date
import arcpy
import os
import json
import time

TEMP_DIR = os.path.join(os.getcwd(), 'temp') # Tudo local

# ------------ Funções auxiliares

def get_rect (shaper):
    rows = arcpy.SearchCursor(shaper)
    shapeName = arcpy.Describe(shaper).shapeFieldName
    for row in rows:
        feat = row.getValue(shapeName)
        extent = feat.extent
    rect = "%s %s %s %s"%(extent.XMin,extent.YMin,extent.XMax,extent.YMax)
    return rect

def deletar_temp(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path) # mesma coisa que remove()
        except Exception as e:
            print(e)

#Verifica a projeção

def walk_rasters_proj(folderpath):
    walk = arcpy.da.Walk(workspace, datatype="RasterDataset", type="TIF")
    for dirpath, dirnames, filenames in walk:
        rasters_dict = {}
        for filename in filenames:
            sr = arcpy.Describe(os.path.join(dirpath, filename)).spatialReference
            if not sr:
                #print('projecao do %s: %s' % (filename, sr.name))
            #else:
                print('%s nao tem projecao' % filename)

#descompactador
def descompact (rootPath, pattern):
    for root, dirs, files in os.walk(rootPath):
        for filename in fnmatch.filter(files, pattern):
            print(os.path.join(root, filename))
            tarfile.open(os.path.join(root, filename)).extractall(
                    os.path.join(root, filename.split(".")[0]))


# Verificação das analises
erro = 0
def verify_analys ():
    erro = 0
    with arcpy.da.SearchCursor(r"D:\Aes0119\Processamento\Analise.gdb\Estatistica_UHE", ["UHE", "Ano", "Epoca", "Perc_Agua", "Perc_macrofita"]) as cursor:
        for row in cursor:
            Perc_macrofita = float(row[4])
            Perc_agua = float(row[3])
            perc_total = Perc_agua + Perc_macrofita
            if perc_total < 96:
                erro = 1
                barragem = row[0]+ "_" + row[1] + "_Q" + row[2]
                arcpy.AddMessage("Barragem: " + barragem + u" está com o seu calculo de percentual com erros!")
    del cursor

def savelog(mensagem, essential_mensage):
    if not essential_mensage:
        if input_date.show_message: #Write or not on Screen
            arcpy.AddMessage(mensagem)
    else: arcpy.AddMessage(mensagem)
    now  = datetime.datetime.now()
    the_file = "Log_AES-Tiete_" + str(now.strftime("%d-%m-%Y"))
    folder = input_date.out_dir + "\log"
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, the_file) + ".txt"
    file = open( file_path, "a")
    file.write(now.strftime("%d-%m-%Y %H:%M:%S") + ' - ' +mensagem+ '\n')
    file.close()

def free_memory():
    savelog("Liberando memória...", 1)
    #Clear
    if input_date.delete_opta_point:
        for opta_point in input_date.list_opta_point:
            if arcpy.Exists(opta_point):
                arcpy.Delete_management(opta_point)

    if input_date.deleta_img_original:
        for ima_orig in input_date.list_ima_original:
            if arcpy.Exists(ima_orig):
                arcpy.Delete_management(ima_orig)

    if input_date.list_jp2_to_tif: #Deleta os tiff resultantes da conversão jp2 e seus arquivos auxiliares
        for ima_jp2_to_tiff in input_date.list_jp2_to_tif:
            if arcpy.Exists(ima_jp2_to_tiff):
                arcpy.Delete_management(ima_jp2_to_tiff)

    if input_date.lista_imagens_sentinel:
        for imagens_sentinel in input_date.lista_imagens_sentinel:
            if arcpy.Exists(imagens_sentinel):
                arcpy.Delete_management(imagens_sentinel)

    if input_date.delete_temp_global:
        if os.path.exists(input_date.GDB_AUX):
            arcpy.Delete_management(input_date.GDB_AUX)

    #set_data_all() # Salving Json

def get_default_data():
    data = {u'Dados_de_Entrada': u'',
            u'Diretorio_Processamento': u'',
            u'Grade_Espelho_Agua': u'',
            u'Reservatorio': u'Todas',
            u'Banco_Dados': u'Novo',
            u'Banco_Dados_Reservatorios': u'',
            u'Banco_Dados_Classificadas': u'',
            u'Banco_Dados_Vector': u'',
            u'Fase_1': 1,
            u'Fase_2': 1,
            u'Fase_3': 1,
            u'Fase_4': 1,
            u'Compilar_Nuvens': 0,
            u'Valor_Min_Nuvens_8Bits': 250,
            u'Valor_Min_Nuvens_16Bits': 14000,
            u'Valor_Max_Macrofitas': 0.750000,
            u'Valor_Min_Macrofitas': 0.200000,
            u'Type_Classifiy': u'Arquivos',
            u'Banco_Dados_GDB_Mosaicos': u'',
            u'Filtrar': u'*',
            u'Tabela_Estatisticas': u'',
            u'Acumular_Estatisticas': 0,
            u'Tabela_Excel': u'',}
    return data

def get_data_path():
    data_path = os.path.join(TEMP_DIR, 'data.json')
    return data_path

def create_data():
    data = get_default_data()
    data_path = get_data_path()

    with open(data_path, 'w') as f:
        json.dump(data, f)
    return data

def get_data():
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    data_path = get_data_path()
    if not os.path.exists(data_path):
        data = create_data()
    else:
        #with open(data_path, 'r') as f:
        data = json.loads(data_path)
        #    data = json.load(f)
    return data

def get_data_old():
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    data_path = get_data_path()
    if not os.path.exists(data_path):
        data = create_data()
    else:
        with open(data_path, 'r') as f:
            #data = json.loads(data_path)
            data = json.load(f)
    return data

def set_path_data(key, value):
    value = value.replace("\'", '\\')
    set_data(key, value)

def set_data(key, value):
    if not key or not value:
        return
    data = get_data()
    data[key] = value

    data_path = get_data_path()
    with open(data_path, 'w') as f:
        json.dump(data, f)

def set_data_all():
    data = get_data()
    data['Dados_de_Entrada'] = input_date.workspace
    data['Diretorio_Processamento'] = input_date.out_dir
    data['Grade_Espelho_Agua']= input_date.grade_espelhodagua
    data['Grade_Buffer_Negativo']= input_date.grade_buffer_negativo
    data['Banco_Dados']= input_date.bd
    data['Banco_Dados_Imagens']= input_date.gdb_fullpath
    data['Banco_Dados_Reservatorios']= input_date.IMA_RESERVATORIOS_GDB
    data['Banco_Dados_Classificadas']= input_date.CLASSIFY_GDB
    data['Banco_Dados_Vector']= input_date.IMA_VECTOR_GDB
    data['Banco_Dados_GDB_Temp']= input_date.GDB_AUX
    data['Fase_1']= input_date.fase_1
    data['Fase_2']= input_date.fase_2
    data['Fase_3']= input_date.fase_3
    data['Fase_4']= input_date.fase_4
    data['Valor_Min_Nuvens_8Bits']= input_date.magic_number_8bits
    data['Valor_Min_Nuvens_16Bits']= input_date.magic_number_16bits
    data['Valor_Max_Macrofitas']= input_date.valor_minimo_macrofita
    data['Type_Classifiy']= input_date.type_classify
    data['Deletar_Arq_Temp']= input_date.delete_temp
    data['Deletar_Arq_Global_Temp']= input_date.delete_temp_global
    data['Compilar_Nuvens']= input_date.have_clody_compilation
    data['Multipeocessamento']= input_date.Multiprocessing
    data['Filtrar']= input_date.filter_year
    data['Tabela_Estatisticas']= input_date.Estatistica_UHE
    data['Acumular_Estatisticas']= input_date.Acumular_Estatisticas
    data['Tabela_Excel']= input_date.table_estatistica_excel

    data_path = get_data_path()
    with open(data_path, 'w') as f:
        json.dump(data, f)

def verify_name_projetion(raster):
    proj_name = arcpy.Describe(raster).SpatialReference.Name

    if proj_name == 'SAD_1969_UTM_Zone_22S' or proj_name == 'South_American_1969_UTM_Zone_22S':
            arcpy.management.DefineProjection(raster, 29192)
    if proj_name == 'SAD_1969_UTM_Zone_23S' or proj_name == 'South_American_1969_UTM_Zone_23S':
            arcpy.management.DefineProjection(raster, 29193)

    #print('%s; %s; %s' % (filename, arcpy.Describe(os.path.join(dirpath, filename)).SpatialReference.Name, arcpy.Describe(os.path.join(dirpath, filename)).SpatialReference.factoryCode))

def verify_projetion(raster):

    flag = True

    description = arcpy.Describe(raster)
    proj_name = description.SpatialReference.Name
    cellsize1 = description.children[0].meanCellHeight  # Cell size in the Y axis and / or
    cellsize2 = description.children[0].meanCellWidth   # Cell size in the X axis
    cellsize = str(cellsize2) + " " + str(cellsize1)

    if not raster.endswith('.tif'):
        raster_out = str(raster) + "_conv"
    else:
        raster_out = "{}{}".format(os.path.splitext(raster)[0], "_conv.tif")

    if arcpy.Exists(input_date.Projs + "\\SIRGAS_2000_UTM_Zone_22S.prj") and arcpy.Exists(input_date.Projs + "\\SIRGAS_2000_UTM_Zone_23S.prj"):
        if '22' in proj_name:
            proj_env = input_date.Projs + "\\SIRGAS_2000_UTM_Zone_22S.prj"
        elif '23' in proj_name:
            proj_env = input_date.Projs + "\\SIRGAS_2000_UTM_Zone_23S.prj"
    else:
        savelog(u"-> Diretório de Projeções está incompleto.", 1)
        return 0

    # Reprojeta as imagens de acordo com o fuso
    if "WGS_1984_UTM_Zone_22N" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize, "SIRGAS_2000_To_WGS_1984_1")
    elif "WGS_1984_UTM_Zone_22S" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize, "SIRGAS_2000_To_WGS_1984_1")
    elif "WGS_1984_UTM_Zone_23N" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize, "SIRGAS_2000_To_WGS_1984_1")
    elif "WGS_1984_UTM_Zone_23S" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize, "SIRGAS_2000_To_WGS_1984_1")
    elif "SIRGAS_2000_UTM_Zone_22N" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize)
    elif "SIRGAS_2000_UTM_Zone_22S" in proj_name:
        return 2
    elif "SIRGAS_2000_UTM_Zone_23N" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize)
    elif "SIRGAS_2000_UTM_Zone_23S" in proj_name:
        return 2
    elif "SAD_1969_UTM_Zone_22S" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize, "'SAD_1969_To_WGS_1984_14 + SIRGAS_2000_To_WGS_1984_1'")
    elif "SAD_1969_UTM_Zone_23S" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize, "'SAD_1969_To_WGS_1984_14 + SIRGAS_2000_To_WGS_1984_1'")

    elif "SAD_1969_UTM_Zone_22N" in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, proj_env, "NEAREST", cellsize, "'SAD_1969_To_WGS_1984_14 + SIRGAS_2000_To_WGS_1984_1'")
    elif "WGS_1984_Web_Mercator_Auxiliary_Sphere"  in proj_name:
        arcpy.management.ProjectRaster(raster, raster_out, "PROJCS['SIRGAS_2000_UTM_Zone_22S',GEOGCS['GCS_SIRGAS_2000',DATUM['D_SIRGAS_2000',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',-51.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", "NEAREST", "4,77731426715991 4,77731426716002", "SIRGAS_2000_To_WGS_1984_1", None, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NO_VERTICAL")
    else:
        savelog(u"-> Uma das imagens está com projeção desconhecida! Favor arruma-la... A Ferramenta será finalizada.", 1)
        flag = False


    if flag:
        if arcpy.Exists(raster):
            arcpy.Delete_management(raster)
            arcpy.Rename_management(raster_out, raster)
            return 1
    else:
        return 0

def directory_is_corret(dirr, flag_landsat):
    verify_ = verify_directory(dirr, flag_landsat)
    if verify_ == "Correto":
        return True
    elif verify_ == "Satelite_have_problem":
        savelog(u"Verifique no nome do diretório do satélite! Nome do satélite deve ser RapidEye, Planet, Landsat ou Sentinel. Verifique inclusive as letras maiusculas.", 1)
        return False
    elif verify_ == "Year_have_problem":
        savelog(u"Verifique no nome do diretório do Ano/Estação! Ano deve vim antes da estação ou ano está errado. Verifique se tem o caracter '_' entre eles. ", 1)
        return False
    elif verify_ == "Seasons_have_problem":
        savelog(u"Verifique no nome do diretório do Ano/Estação! Estação deve vir depois do ano. Verifique se tem o caracter '_' entre eles. As estações devem ser Q1, Q2, Q3 ou Q4.", 1)
        return False
    elif verify_ == "Dam_have_problem":
        savelog(u"Verifique no nome do diretório da barragem! Nome deve ter as siglas da barragem em maiusculo [AVG, BAB, BAR, CAC, EUC, IBI, LMO, MOG, NAV ou PRO] ", 1)
        return False
    elif verify_ == "Reversed_date":
        savelog(u"Verifique no nome do diretório da data! Data deve estar innvertida, verifique se o diretorio está no padrão <ano_mes_dia>. Ano deverá ter 4 digitos.", 1)
        return False
    elif verify_ == "Date_have_problem":
        savelog(u"Verifique no nome do diretório da data! Data deve seguir o padrão <ano_mes_dia>. Ano deverá ter 4 digitos.", 1)
        return False
    elif verify_ == "Orbital_have_problem":
        savelog(u"Verifique no nome do diretório da órbita ponto! Órbita ponto deveria ter 6 digitos.", 1)
        return False
    else:
        savelog(u"Erro no diretório!", 1)
        return False

def verify_directory(dirr, flag_landsat): #Verifica se o diretório é válido
    directory_parts = dirr.split("\\")

    # Verifica se o nome do Satélite está certo (Planet, RapidEye, Sentinel ou Landsat - Inclusive começando com a letra maiuscula)
    satelite_ = directory_parts[-3 - flag_landsat]
    if not satelite_ == "Planet" and not satelite_ == "RapidEye" and not satelite_ == "Sentinel" and not satelite_ == "Landsat":
        return "Satelite_have_problem"

    # Verifica se o ano e a estação estão dentro do padrão
    ano_estacao = directory_parts[-4 - flag_landsat].split("_")
    if not ano_estacao[-2].isdigit():
        return "Year_have_problem"

    if not ano_estacao[-1] == "Q1" and not ano_estacao[-1] == "Q2" and not ano_estacao[-1] == "Q3" and not ano_estacao[-1] == "Q4":
        return "Seasons_have_problem"

    # Verifica se o nome da barragem está correto
    if not directory_parts[-5 - flag_landsat] in input_date.barragens:
        return "Dam_have_problem"

    # Verificar a data
    isdate_ = len(str(directory_parts[-2 - flag_landsat]))
    if isdate_ >= 8:
        data_ = directory_parts[-2 - flag_landsat].split("_")
        isdate_year = len(str(data_[-3]))
        if not isdate_year == 4:
            return "Reversed_date"
        isdate_month = len(str(data_[-2]))
        if not isdate_month >= 1:
            return "Date_have_problem"
        isdate_day = len(str(data_[-1]))
        if not isdate_day >= 1:
            return "Date_have_problem"
        month = int(data_[-2])
        day_ = int(data_[-1])
        if month < 1 or month > 12: # Se está nos doze meses
            return "Date_have_problem"
        if day_ < 1 or day_ > 31: # Verifica se o dia é válido
            return "Date_have_problem"
    else:
        return "Date_have_problem"

    if flag_landsat: # Diretorio de landsat - Verificar a orbita ponto
        orbital_ = directory_parts[-2]
        cont_number_orbital = len(str(directory_parts[-2]))
        if not orbital_.isdigit():
            return "Orbital_have_problem"
        if not cont_number_orbital == 6:
            return "Orbital_have_problem"

    return "Correto" # Diretorio correto

def get_field_valid(table):

    fieldObs = arcpy.ListFields(table)
    fieldNames = []
    fields_elim = ["OBJECTID", "UHE", "Ano", "Epoca", "Estacao", "Periodo", "Data_Inicial", "Data_final"]
    for field in fieldObs:
        if not field.name in fields_elim:
            fieldNames.append(field.name)
    del fieldObs

    return fieldNames

def check_update_table(barragem_, ano_, epoca_):

    result = arcpy.GetCount_management(input_date.Estatistica_UHE)
    if not result[0] == '0':
        try: #Atualiza a tabela, se existir o registro é eliminado para o novo registro atualizado
            with arcpy.da.UpdateCursor(input_date.Estatistica_UHE, ["UHE", "Ano", "Epoca"]) as cursor:
                for row in cursor:
                    if row[0] == barragem_ and row[1] == ano_ and row[2] == epoca_:
                        cursor.deleteRow()
                        break
                del cursor
        except:
            funtions_aux.savelog(u"Erro ao atualizar tabela das estatisticas...", 1)

def export_excel():
    name = ""
    sufixo = str(time.strftime("%Y_%m_%d_%H_%M_%S"))  #Nome do arquivo será diferenciado pela data de realização para diferentes filtres e diferentes barragens
    savelog("Exportando tabela...", 1)
    barr = input_date.barragem_filtro
    if input_date.Acumular_Estatisticas:
        if not "*" in barr:
            name = input_date.table_estatistica_excel + "\\Estatistica_" + barr + "_" + sufixo + ".xlsx"
            arcpy.TableToExcel_conversion(input_date.Estatistica_Temp, name, "NAME", "CODE")
        else:
            name = input_date.table_estatistica_excel + "\\Estatistica_Todas" + "_" + sufixo + ".xlsx"
            arcpy.TableToExcel_conversion(input_date.Estatistica_UHE,name, "NAME", "CODE")
    else:
        if "*" in barr:
            barr = "Todas"
        name = input_date.table_estatistica_excel + "\\Estatistica_" + barr + "_" + sufixo + ".xlsx"
        arcpy.TableToExcel_conversion(input_date.Estatistica_Temp, name, "NAME", "CODE")

    savelog("Tabela exportada em " + name, 1)

def date_analisy(date, format_): # Date = Data e format_ = retorna a data e formota e retorna no padrão <dia/mes/ano> as datas inicial e final
    if len(date) > 10:
        data1 = date [:10]
        data2 = date [11:]
        if data1 == data2:
            date = data1
            data_i = data_f = date.replace("_", "/")
        else:
            mes1 = int(date [3:5])
            mes2 = int(date [14:16])
            if mes1 == mes2:
                dia1 = int(date[0:2])
                dia2 = int(date[11:13])
                if dia1 > dia2:
                    date = data2 + "_" + data1
                    data_i = data2.replace("_", "/")
                    data_f = data1.replace("_", "/")
                else:
                    data_i = data1.replace("_", "/")
                    data_f = data2.replace("_", "/")
            else:
                if mes1 > mes2:
                    date = data2 + "_" + data1
                    data_i = data2.replace("_", "/")
                    data_f = data1.replace("_", "/")
                else:
                    data_i = data1.replace("_", "/")
                    data_f = data2.replace("_", "/")
    else:
        data_i = data_f = date.replace("_", "/")

    if format_:
        return date, data_i, data_f
    else:
        return date

def calculate_ocupation(statistic_table):
    with arcpy.da.UpdateCursor(statistic_table, ['UHE', 'ANO', 'EPOCA', 'AREA_MACROFITA', 'TAXA_OCUPACAO_M'], sql_clause=(None, 'ORDER BY UHE, ANO, EPOCA')) as cursor:
        last_macrofita_area = 0
        units = []
        for row in cursor:
            if row[0] not in units:
                last_macrofita_area = row[3]
                row[4] = 0
                cursor.updateRow(row)
                units.append(row[0])
                continue

            current_area_macrofita = row[3]
            ocupaction_rate = current_area_macrofita - last_macrofita_area
            row[4] = ocupaction_rate

            cursor.updateRow(row)

            last_macrofita_area = current_area_macrofita


def get_number_class(fc):
    my_list = [i[0] for i in arcpy.da.SearchCursor(fc,'Count')]
    if my_list:
        my_max = max(my_list)
        my_min = min(my_list)
    else:
        my_max = my_min = 0

    return my_min, my_max

def update_field(dirp, sensor):
    barragem = dirp.split("\\")[-3]
    quarter  = (dirp.split("\\")[-2]).split("_")[-1]
    ano      = (dirp.split("\\")[-2]).split("_")[-2]
    print ("Atualizando o reservatório de " + barragem + ", no ano de " + ano + ", no período " + quarter + "..." )
    selection = arcpy.management.SelectLayerByAttribute(input_date.Estatistica_UHE, "NEW_SELECTION", "UHE = '"+barragem+"'" +" AND "+  "ANO = '"+ano+"'" +" AND "+ "EPOCA = '"+quarter+"'", None)
    calculateFieldExpression  = "'"+sensor+"'"
    arcpy.CalculateField_management(selection, field = "Satelite", expression = calculateFieldExpression, expression_type = "PYTHON3", code_block = "")


#Varre do banco de dados para atualizar o campo satelite
def update_bd_field(workspace):
    walk = arcpy.da.Walk(workspace, datatype="RasterDataset",type=['TIF', 'JP2'])
    for dirpath, dirnames, filenames in walk:
        if "Landsat" in dirpath.split("\\")[-1]:
            update_field(dirpath, "LandSat")
        elif "RapidEye" in dirpath.split("\\")[-1]:
            update_field(dirpath, "RapidEye")
        elif "Planet" in dirpath.split("\\")[-1]:
            update_field(dirpath, "Planet")
        elif "Sentinel" in dirpath.split("\\")[-1]:
            update_field(dirpath, "Sentinel")
        else:
            continue

#Felizes são os peixes...