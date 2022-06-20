import arcpy
import sys
import input_date
import funtions_aux

# clody landsat 5 e 7 -> 1 Landsat 8 -> 2  Santinel -> 1
# ---------------------------------------------
# Faz o composite, reprojeta e calcula o NDVI para imagens LandSat e Sentinel

def ajust_images(rasters, rastername, sensor):

    if not "*" in input_date.barragem_filtro:    #Filtro por barragem
        if "_LANDSAT" in sensor:
            filter_barragem = rasters[0].split("\\")[-6]
        elif "_SENTINEL" in sensor:
            filter_barragem = rasters[0].split("\\")[-5]
        if not input_date.barragem_filtro in filter_barragem:
            return

    # Filtro caso houver
    if not "*" in input_date.filter_year:       #filtro por ano e quadrante
        if "_LANDSAT" in sensor:
            filter_ = rasters[0].split("\\")[-5]
        elif "_SENTINEL" in sensor:
            filter_ = rasters[0].split("\\")[-4]
        if not input_date.filter_year in filter_:
            return
        else:
            if len (input_date.filter_year) > 4:
                station = filter_.split("_")[-1]
                station_filter = input_date.filter_year.split("_")[-1]
                year_1 = filter_.split("_")[-2]
                year_2 = input_date.filter_year.split("_")[-2]
                if not station == station_filter:
                    return
                if not year_1 == year_2:
                    return

    funtions_aux.savelog("Arquivo: " + str(rastername) + " -> Iniciando...", 1)

    for file_ in rasters: #Verifica a lista de arquivos antes do composite
        if "_LANDSAT" in sensor:
            dirr_ = funtions_aux.directory_is_corret(file_, 1)  # Verifica o nome do diretorio
        elif "_SENTINEL" in sensor:
            dirr_ = funtions_aux.directory_is_corret(file_, 0)  # Verifica o nome do diretorio
        if not dirr_:
            return #Diretorio com problema

    arcpy.env.workspace = input_date.GDB_AUX

    funtions_aux.savelog("-> Fazendo o Composite...", 1)

    composite = arcpy.CompositeBands_management(rasters, arcpy.env.workspace + "\\" + rastername)

    funtions_aux.savelog(u"-> Composite finalizado! Verificando a projeção da imagem...", 1)

    funtions_aux.verify_name_projetion(rastername) # Verifica e arruma nomes errados de projeção

    proj = funtions_aux.verify_projetion(rastername) # Reprojeta

    if proj == 1:
        funtions_aux.savelog("-> Imagem foi Reprojetada.", 1)
    elif proj == 0:
        sys.exit() # Finaliza o programa
    else:
        funtions_aux.savelog("-> Imagem com projeção correta!", 1)

    if sensor == "_LANDSAT" :
        select_orbita = rastername.split("_")[-1]
        #select_orbita = rastername[10:16]
        selection = "NOME = " + "'" + select_orbita + "'"
        ttt = arcpy.management.SelectLayerByAttribute(input_date.grade_buffer_negativo, "NEW_SELECTION", selection , None)

        with arcpy.da.SearchCursor(ttt, ["Min_X", "Min_Y", "Max_X", "MAx_Y"]) as cursor:
            for row in cursor:
                rect = "%s %s %s %s"%(row[0],row[1], row[2], row[3])

        funtions_aux.savelog("-> Recortando a imagem...", 1) # para o Mosaico...")

        arcpy.management.Clip(rastername, rect, rastername + "_clip", ttt,'', "ClippingGeometry", "NO_MAINTAIN_EXTENT")

        if arcpy.Exists(rastername):
            arcpy.Delete_management(rastername)
            arcpy.Rename_management(rastername + "_clip", rastername + sensor)

        funtions_aux.savelog("-> Recorte Finalizado!", 1) # Calculando o NDVI...")
    else: #Sentinel
        arcpy.Rename_management(rastername, rastername + sensor)
        arcpy.management.CopyRaster(rastername + sensor, input_date.IMA_RESERVATORIOS_GDB + "\\" +  rastername + sensor, '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")

    if input_date.file_or_mosaic == 1: #Para Files
        input_date.lista_files.append(rastername + sensor)

    funtions_aux.savelog("Arquivo: " + str(rastername + sensor) + " -> Finalizado", 1)


def ajust_images_special(filename, rastername, sensor):

    if not "*" in input_date.barragem_filtro:    #Filtro por barragem
        filter_barragem = filename.split("\\")[-5]
        if not input_date.barragem_filtro in filter_barragem:
            return

    # Filtro caso houver
    if not "*" in input_date.filter_year:       #filtro por ano e quadrante
        filter_ = filename.split("\\")[-4]
        if not input_date.filter_year in filter_:
            return
        else:
            if len (input_date.filter_year) > 4:
                station = filter_.split("_")[-1]
                station_filter = input_date.filter_year.split("_")[-1]
                year_1 = filter_.split("_")[-2]
                year_2 = input_date.filter_year.split("_")[-2]
                if not station == station_filter:
                    return
                if not year_1 == year_2:
                    return

    dirr_ = funtions_aux.directory_is_corret(filename, 0)  # Verifica o nome do diretorio
    if not dirr_:
        return

    arcpy.env.workspace = input_date.GDB_AUX

    funtions_aux.savelog("Arquivo: " + str(filename) + " -> Iniciando...", 1)

    name_ = input_date.IMA_RESERVATORIOS_GDB + "\\" +  rastername + sensor

    funtions_aux.savelog("-> Copiando arquivo para um banco de imagens...", 1)

    arcpy.management.CopyRaster(filename, name_, '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")

    funtions_aux.savelog(u"-> Verificando a projeção da imagem...", 1)

    funtions_aux.verify_name_projetion(name_) # Verifica e arruma nomes errados de projeção

    proj = funtions_aux.verify_projetion(name_) # Reprojeta

    if proj == 1:
        funtions_aux.savelog("-> Imagem foi Reprojetada.", 1)
    elif proj == 0:
        sys.exit(1) # Finaliza o programa
    else:
        funtions_aux.savelog(u"-> Imagem com projeção correta!", 1)

    funtions_aux.savelog("Arquivo: " + str(rastername + sensor) + " -> Finalizado", 1)







