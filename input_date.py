# -*- coding: utf-8 -*-

#import arcpy, os, datetime, shutil, tarfile, fnmatch
import time, arcpy, os

# --- Entrada de Dados
workspace = r"D:\Projetos\Programa_Ambiental\01_Entrada"  #LandSat 5,7 e 8 ,RapaidEye, Planet or Sentinel

# ---- Diretório de Saída
out_dir = r"D:\Projetos\Programa_Ambiental\03_Saida"

# ---- Lista de imagens com nuvens

lista_clody = []   # lista de arquivos que contem nuvens
lista_files = []   # Lista de arquivos que serão executados

dict_landsat = {}  # Dicionário de imagens landsat
dict_sensor  = {}  # Dicionário de sensores

#camp = os.getcwd()
camp = os.path.dirname(os.path.realpath(__file__))

Projs = camp + "\\Proj"

# ------- Grades Auxiliares
grade_buffer_negativo = camp + "\\Aes_dados_apoio.gdb\\Grade_Landsat_BuffNeg"
grade_espelhodagua    = camp + "\\Aes_dados_apoio.gdb"

#-------- Criação dos Banco de Dados

gdb_name = str(time.strftime("%Y_%m_%d_%H_%M_%S"))

#IMA_RESERVATORIOS_GDB     = r"D:\Aes0119\Imagens_19\Landsats\2019_12_06_17_31_53_images_reservatorios.gdb" #Mosaicos da Landsat de 2000/2015

IMA_RESERVATORIOS_GDB     = str(arcpy.CreateFileGDB_management(out_dir, gdb_name + "_images_reservatorios.gdb"))
IMA_VECTOR_GDB            = str(arcpy.CreateFileGDB_management(out_dir, gdb_name + "_images_vector.gdb"))
CLASSIFY_GDB              = str(arcpy.CreateFileGDB_management(out_dir, gdb_name + "_images_classify.gdb"))

GDB_AUX                   = str(arcpy.CreateFileGDB_management(out_dir, gdb_name + "_gdb_aux.gdb"))

#-------- Bancos auxiliares (Utilizado quando já existem Banco de imagens e NDVI  formado)

'''arcpy.env.workspace       = r"D:\Aes0119\Processamento\2020_06_01_16_14_49.gdb"

gdb_fullpath              = r"D:\Aes0119\Processamento\2020_06_01_16_14_49.gdb"
CLASSIFY_GDB              = r"D:\Aes0119\Processamento\2020_06_01_16_14_49_images_classify.gdb"
GDB_AUX                   = r""
IMA_RESERVATORIOS_GDB     = r"D:\Aes0119\Processamento\2020_06_01_16_14_49_images_reservatorios.gdb"
#IMA_VECTOR_GDB            = r"D:\Aes0119\Processamento\2020_06_01_16_14_49_images_vector.gdb"
IMA_VECTOR_GDB            = camp + r"\\Process\\2020_05_25_16_16_26_images_vector.gdb"'''


# ---------- Statitics

Freq_Temp           = camp + "\\Aes_dados_apoio.gdb\\Freq_Temp"
Freq_Temp_Pivot     = camp + "\\Aes_dados_apoio.gdb\\Freq_Temp_Pivot"
Estatistica_UHE     = camp + "\\Aes_dados_apoio.gdb\\Estatistica_UHE"
Estatistica_Temp    = camp + "\\Aes_dados_apoio.gdb\\Estatistica_Temp"

Estatistica_Pivot   = camp + "\\Aes_dados_apoio.gdb\\Estatistica_Pivot"

table_estatistica_excel = camp + r"\\Estatisticas"

# Individuais
#Estatistica_UHE_Barragem     = ""
#EstatisticaPorBarragem       = 0
Acumular_Estatisticas        = 0

# ---- Bloco de Códigos Globais

codeblock = """def Reclass(valor):
            if (valor == 1):
                return "Agua 1"
            elif (valor == 2):
                return "Agua 2"
            elif (valor == 3):
                return "Agua 3"
            elif (valor == 4):
                return "Nuvem"
            elif (valor == 5):
                return "Emersa_Mista"
            elif (valor == 6):
                return "Emersa_Mista"
            elif (valor == 7):
                return "Flutuante"
            elif (valor == 8):
                return "Vegetacao"
            elif (valor == 9):
                return "Solo" """

'''codeblock = """def Reclass(valor):
            if (valor == 1):
                return "Agua_1"
            elif (valor == 2):
                return "Agua_2"
            elif (valor == 3):
                return "Agua_3"
            elif (valor == 4):
                return "Agua_4"
            elif (valor == 5):
                return "Macrofita"
            elif (valor == 6):
                return "Nuvem" """'''

codeblock2 = """def Reclass(valor):
            if (valor == 'Q1'):
                return "Chuvoso"
            elif (valor == 'Q2'):
                return "Chuvoso"
            elif (valor == 'Q3'):
                return "Seco"
            elif (valor == 'Q4'):
                return "Seco" """

codeblock4 = """def Reclass2(valor):
            if (valor == 'Flutuante'):
                return "Flutuante"
            elif (valor == 'Agua 1'):
                return "Agua 1"
            elif (valor == 'Agua 2'):
                return "Agua 2"
            elif (valor == 'Agua 3'):
                return "Agua 3"
            elif (valor == "Nuvem"):
                return "Nuvem"
            elif (valor == "Solo"):
                return "Solo"
            elif (valor == "Vegetacao"):
                return "Vegetacao"
            elif (valor == "Emersa_Mista"):
                return "Emersa_Mista"
            else: return "None" """

# ----- Acompanhamento das barragens pela tela

barragens = {"AGV" : "Água Vermelha",
             "CAC" : "Caconde",
             "BAB" : "Barra Bonita",
             "BAR" : "Bariri",
             "IBI" : "Ibitinga",
             "NAV" : "Nova Avanhandava",
             "PRO" : "Promissão",
             "LMO" : "Limoeiro",
             "MOG" : "Mogi-Guaçu",
             "EUC" : "Euclides da Cunha"
             }

# Atributos do ArcGis Globais

arcpy.env.overwriteOutput   = True
arcpy.gp.loghistory         = False

delete_temp                 = False   #Se deleto ou não os arquivos temporários da classificação
delete_temp_global          = False  #Se deleta arquivos globais Datasets
delete_opta_point           = True   #Se deleta as orbitas ponto das imagens landsat temporarias
deleta_img_original         = True   #Se deleta as lista de imagens (Rapid ou Planet) originais

magic_number_8bits          = 250
magic_number_16bits         = 14000

magic_number_min_macrophytes_er = 0.600000
magic_number_max_macrophytes_er = 0.750000

magic_number_min_macrophytes_flu = 0.600000
magic_number_max_macrophytes_flu = 0.750000

have_clody_compilation      = True

file_or_mosaic              = 1      # File = 1 or Mosaic = 2 or both = 0

filter_year                 = "2020_Q1"    # * Todos ;  2018 Somente o ano de 2018 ; 2018_Q1 Somente o ano de 2018 no quadrante Q1

Multiprocessing             = False  #True

barragem_filtro             = "PRO"   #Todas or [AGV, BAB, BAR, IBI, EUC, MOG, LMO, NAV, PRO, CAC]

# Projeção
prj_22 = "PROJCS['SIRGAS_2000_UTM_Zone_22S',GEOGCS['GCS_SIRGAS_2000',DATUM['D_SIRGAS_2000',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',-51.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
prj_23 = "PROJCS['SIRGAS_2000_UTM_Zone_23S',GEOGCS['GCS_SIRGAS_2000',DATUM['D_SIRGAS_2000',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',10000000.0],PARAMETER['Central_Meridian',-45.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"

conversion_22 = "PROJCS['WGS_1984_UTM_Zone_22N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-51.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
conversion_23 = "PROJCS['WGS_1984_UTM_Zone_23N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-45.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"

bd = 'Novo'
type_classify = 'Arquivos'

show_message = True #Se escreve as mensagens não essenciais na tela

fase_1 = True
fase_2 = True
fase_3 = True

list_opta_point = []
list_ima_original = []
list_jp2_to_tif = []

sentinel_multi = 0
lista_imagens_sentinel = []

