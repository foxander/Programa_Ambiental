import arcpy, os, datetime, sys
import glob
import input_date
import funtions_aux

def classify_module():

    if input_date.file_or_mosaic == 1: # Por Arquivo
        walk = arcpy.da.Walk(input_date.workspace, datatype="RasterDataset", type="TIF")
        dir_control = []
        for dirpath, dirnames, filenames in walk:
            list_dir = []
            if "Sentinel" in dirpath:
                auxx = dirpath.split("\\")[-1]
                data, per = dirpath.split("\\")[-2][0:4], dirpath.split("\\")[-2][5:]
                barragem = dirpath.split("\\")[-3]
                if "Sentinel" in auxx:
                    if not "*" in input_date.barragem_filtro:
                        if input_date.barragem_filtro in barragem and (data in input_date.filter_year or per in input_date.filter_year):
                            if len (input_date.lista_imagens_sentinel) == 0:
                                classify_for_mosaic("*_SENTINEL")
                            else:
                                classify_for_files_sentinel()
                                lista_imagens_sentinel = []  #Limpa a lista principal
                    else:
                        if not "*" in input_date.filter_year:
                            if data in input_date.filter_year or per in input_date.filter_year:
                                if len (input_date.lista_imagens_sentinel) != 0:
                                    classify_for_files_sentinel()
                                    lista_imagens_sentinel = []  #Limpa a lista principal
                                else:
                                    classify_for_mosaic("*_SENTINEL")
                        else:
                            if len (input_date.lista_imagens_sentinel) != 0:
                                classify_for_files_sentinel()
                                lista_imagens_sentinel = []  #Limpa a lista principal
                            else:
                                classify_for_mosaic("*_SENTINEL")

            elif "Landsat" in dirpath: #Opção Por arquivo ativanda, porem para Landsat se tiver faz por mosaico
                auxx = dirpath.split("\\")[-1]
                data, per = dirpath.split("\\")[-2][0:4], dirpath.split("\\")[-2][5:]
                barragem = dirpath.split("\\")[-3]
                if "Landsat" in auxx:
                    if not "*" in input_date.barragem_filtro:
                        if input_date.barragem_filtro in barragem and (data in input_date.filter_year or per in input_date.filter_year):
                            classify_for_mosaic("*_LANDSAT")
                    else:
                        if not "*" in input_date.filter_year:
                            if data in input_date.filter_year or per in input_date.filter_year:
                                classify_for_mosaic("*_LANDSAT")
                        else:
                            classify_for_mosaic("*_LANDSAT")

    elif input_date.file_or_mosaic == 2: # Por Mosaic
        classify_for_mosaic("*")

def classify_for_mosaic(param):

    old_workspace = arcpy.env.workspace
    arcpy.env.workspace = input_date.IMA_RESERVATORIOS_GDB

    rasters = arcpy.ListRasters(param)

    for mosaic_name in rasters:

        list_delete = []

        raster_split = mosaic_name.split('_')
        UHEfc = raster_split[0]

        mosaic_name_year_est = "_".join(raster_split[1:3])

        if not "*" in input_date.barragem_filtro:    #Filtro por barragem
            if not input_date.barragem_filtro in UHEfc:
                continue

        # Filtro caso houver
        if not "*" in input_date.filter_year:
            filter_ = mosaic_name_year_est
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

        funtions_aux.savelog("Mosaico -> Processando: " + mosaic_name + "...", 1)

        lista_temp = []
        lista_agua_compl = []
        lista_final = []
        lista_aguanuvem = []

        arcpy.env.mask = input_date.grade_espelhodagua + "\\" + "%s_MASC_MAX" % UHEfc

        if UHEfc == "CAC" or UHEfc == "EUC" or UHEfc == "LMO" or UHEfc == "MOG":
            prj = input_date.prj_23
        else: prj = input_date.prj_22

        Band_B = "\Band_1"
        Band_G = "\Band_2"
        Band_R = "\Band_3"

        #Banda
        if '_RAPIDEYE' in mosaic_name:
            Band_I = "\Band_5"
            n_bands = 5
        else: #LandSat, Sentiner and Planet
            Band_I = "\Band_4"
            n_bands = 4

        if input_date.file_or_mosaic == 1 and not '_landsat' in mosaic_name.lower() and not '_SENTINEL' in mosaic_name: # Por Arquivo
            img_rec = input_date.GDB_AUX + "\\" + mosaic_name + "_" + str(parts) + "_clip"
        else:
            img_rec = input_date.GDB_AUX + "\\" + mosaic_name + "_clip"

        arcpy.management.Clip(mosaic_name, funtions_aux.get_rect(arcpy.env.mask), img_rec, input_date.grade_espelhodagua + "\\" + "%s_MASC_MAX" % UHEfc,'', "ClippingGeometry", "NO_MAINTAIN_EXTENT")
        list_delete.append(img_rec)

        funtions_aux.savelog(u"Imagem recortada com espelho D'água: %s" % mosaic_name, 0)

        arcpy.env.mask = img_rec

        #Get Resolution
        description = arcpy.Describe(img_rec)
        cellsize1 = description.children[0].meanCellHeight  # Cell size in the Y axis and / or
        cellsize2 = description.children[0].meanCellWidth   # Cell size in the X axis

        #GERAÇÃO DO NDVI - VERIFICAR AS BANDAS CONFORME SENSOR
        img_ndvi = img_rec+"_NDVI"
        NDVI = (arcpy.Raster(img_rec+Band_I) - arcpy.Raster(img_rec+Band_R)) / (arcpy.Raster(img_rec+Band_I) + arcpy.Raster(img_rec+Band_R)) #RapidEye
        NDVI.save(os.path.join(input_date.GDB_AUX, img_ndvi))
        list_delete.append(img_ndvi)
        funtions_aux.savelog("NDVI gerado: %s" % img_ndvi, 0)

        #GERAÇÃO DE MÁSCARA A PARTIR DO NDVI
        img_masc_ndvi = img_ndvi + "_Mask"
        MASC_NDVI = arcpy.sa.Reclassify(img_ndvi, "Value", "-1 1 1", "DATA");
        MASC_NDVI.save(os.path.join(input_date.GDB_AUX, img_masc_ndvi))
        list_delete.append(img_masc_ndvi)
        funtions_aux.savelog(u"Máscara NDVI gerada: %s" % img_masc_ndvi, 0)

        img_nuvem = img_rec + "_NUVEM"

        if input_date.have_clody_compilation:  #Se usuário quer que  anuvem entre na compilação, meswmo que não tenha nuvens
            #GERAÇÃO DE NUVEM - BANDA AZUL
            img_entrada_BAzul = arcpy.Raster(img_rec+Band_B)
            img_nuvem_temp = img_rec + "_Nuvem_temp"

            ValorMAXXpx = arcpy.Raster(img_rec+Band_B).maximum
            ValorTYPEpx = arcpy.GetRasterProperties_management(img_rec+Band_B,"VALUETYPE",'').getOutput(0)

            if (int(ValorMAXXpx) >= input_date.magic_number_8bits and int(ValorTYPEpx) == 3) or (int(ValorMAXXpx) >= input_date.magic_number_16bits and int(ValorTYPEpx) == 5):

                if '_LANDSAT' in mosaic_name or '_SENTINEL' in mosaic_name:
                    if UHEfc == "CAC":
                        img_nuvem_temp2 = img_rec + "_Nuvem_temp2"
                        NUVEM_temp = arcpy.sa.PrincipalComponents(img_rec, n_bands, None)
                        NUVEM_temp.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp))
                        NUVEM_temp2 = arcpy.sa.Slice(img_nuvem_temp+"\Band_3", 4, "NATURAL_BREAKS", 5) #VAI SEPARAR NUVEM E OUTROS OBJETOS
                        NUVEM_temp2.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp2))
                        NUVEM = arcpy.sa.Reclassify(img_nuvem_temp2, "Value", "4 NODATA;5 NODATA;6 NODATA;7 NODATA;8 4", "NODATA")
                        NUVEM.save(os.path.join(input_date.GDB_AUX, img_nuvem))
                        nulo_nuvem = arcpy.sa.IsNull(img_nuvem)
                        list_delete.append(img_nuvem_temp2)
                    else:
                        NUVEM_temp = arcpy.sa.Slice(img_rec+Band_B, 4, "NATURAL_BREAKS", 4) #VAI SEPARAR NUVEM E OUTROS OBJETOS
                        NUVEM_temp.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp))
                        NUVEM = arcpy.sa.Reclassify(img_nuvem_temp, "Value", "4 NODATA;5 4;6 4;7 4", "NODATA")
                        NUVEM.save(os.path.join(input_date.GDB_AUX, img_nuvem))
                        nulo_nuvem = arcpy.sa.IsNull(img_nuvem)

                elif '_PLANET' in mosaic_name or '_RAPIDEYE' in mosaic_name:
                        range_reclassify = str(input_date.magic_number_16bits) + " " + str(ValorMAXXpx) + " 4"
                        NUVEM_temp = arcpy.sa.Reclassify(img_rec+Band_B, "Value", range_reclassify, "NODATA")
                        NUVEM_temp.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp_reclassify))
                        NUVEM_temp_1 = arcpy.sa.Reclassify(img_ndvi, "Value", "-0.20 0.29 4", "NODATA") #faixa média de nuvem no NDVI
                        NUVEM_temp_1.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp_ndvi))
                        NUVEM_CON = arcpy.sa.Con(NUVEM_temp_1,NUVEM_temp)
                        NUVEM_CON.save(os.path.join(input_date.GDB_AUX, img_nuvem))
                        nulo_nuvem = arcpy.sa.IsNull(img_nuvem)

                list_delete.append(img_nuvem_temp)
                funtions_aux.savelog("Nuvem gerada: %s" % img_nuvem, 0)

            else:
                funtions_aux.savelog(u"Imagem sem a presença de Nuvens!!!", 0)

            if arcpy.Exists(img_nuvem):
                lista_temp.append(img_nuvem)
                lista_aguanuvem.append(img_nuvem)
                list_delete.append(img_nuvem)

        #GERAÇÃO DA ÁGUA GERAL - BANDA INFRAVERMELHO (IV) - VERIFICAR A BANDA CONFORME SENSOR
        img_agua_temp = img_rec + "_agua_temp"
        img_agua = img_rec + "_AGUA"
        AGUAtemp = arcpy.sa.Slice(img_rec+Band_I, 2, "NATURAL_BREAKS",1) #VAI SEPARAR AGUA E OUTROS OBJETOS
        AGUAtemp.save(os.path.join(input_date.GDB_AUX, img_agua_temp))
        AGUA = arcpy.sa.Reclassify(img_agua_temp, "Value", "1 1", "NODATA") #VAI SALVAR APENAS A AGUA DA BANDA DO (IV)
        AGUA.save(os.path.join(input_date.GDB_AUX, img_agua))
        nulo_agua = arcpy.sa.IsNull(img_agua)
        list_delete.append(img_agua_temp)
        funtions_aux.savelog(u"Água gerada: %s" % img_agua, 0)
        if arcpy.Exists(img_agua):
            lista_temp.append(img_agua)
            lista_aguanuvem.append(img_agua)
            lista_agua_compl.append(img_agua)
            list_delete.append(img_agua)

        #GERAÇÃO DO SOLO GERAL - BANDA VERMELHO (V) - VERIFICAR A BANDA CONFORME SENSOR
        img_solo_temp = img_rec + "_solo_e_outros_temp"
        img_solo_temp2 = img_solo_temp + "_reclass"
        img_solo = img_rec + "_SOLO"
        img_entrada_BV = arcpy.Raster(img_rec+Band_R)
        if arcpy.Exists(img_nuvem):
            Solotemp = arcpy.sa.Con(nulo_agua & nulo_nuvem,img_entrada_BV) #VAI SOBRERPOR A AREA DE AGUA E TRANSFORMAR EM NODATA E PERMANECE A AREA RESTANTE (SOLO E OUTROS OBJETOS)
        else:
            Solotemp = arcpy.sa.Con(nulo_agua,img_entrada_BV) #VAI SOBRERPOR A AREA DE AGUA E TRANSFORMAR EM NODATA E PERMANECE A AREA RESTANTE (SOLO E OUTROS OBJETOS)
        Solotemp.save(os.path.join(input_date.GDB_AUX, img_solo_temp))
        Solotempreclass = arcpy.sa.Slice(img_solo_temp, 2, "NATURAL_BREAKS", 8) #VAI SEPARAR SOLO E OUTROS OBJETOS
        Solotempreclass.save(os.path.join(input_date.GDB_AUX, img_solo_temp2))
        Solo = arcpy.sa.Reclassify(img_solo_temp2, "Value", "9 9", "NODATA") #VAI SALVAR APENAS O SOLO DA BANDA DO (V)
        Solo.save(os.path.join(input_date.GDB_AUX, img_solo))
        nulo_solo = arcpy.sa.IsNull(img_solo)
        list_delete.append(img_solo_temp)
        list_delete.append(img_solo_temp2)
        funtions_aux.savelog("Solo gerado: %s" % img_solo, 0)

        if arcpy.Exists(img_solo):
            lista_temp.append(img_solo_temp)
            list_delete.append(img_solo)

        #GERAÇÃO DO NDVI FORA DA ÁREA DE ÁGUA E SOLO
        img_ndviforaagua = img_ndvi + "_foradaAGUA"
        NDVIforaagua = arcpy.sa.Con(nulo_agua & nulo_solo, img_ndvi) #VAI MANTER NDVI SOMENTE NA AREA QUE NAO TEM ÁGUA E SOLO
        NDVIforaagua.save(os.path.join(input_date.GDB_AUX, img_ndviforaagua))
        list_delete.append(img_ndviforaagua)
        funtions_aux.savelog(u"NDVI fora da água gerado: %s" % img_ndviforaagua, 0)

        #GERAÇÃO DA MACRÓFITA EMERSA/MISTA
        img_emersamista = img_rec + "_macrofita_EM"
        range_macrofita_em = "-1 " + str(input_date.magic_number_min_macrophytes_er) + " NODATA;" + str(input_date.magic_number_min_macrophytes_er) + " " + str(input_date.magic_number_max_macrophytes_er) +" 5;" + str(input_date.magic_number_max_macrophytes_er) +" 1 8"
        #"-1 0,200000 NODATA;0,200000 0,750000 5;0,750000 1 6"
        EmersaMista = arcpy.sa.Reclassify(img_ndviforaagua, "VALUE", range_macrofita_em, "DATA") #CLASSIFICA MACRÓFITA EMERSA/MISTA
        EmersaMista.save(os.path.join(input_date.GDB_AUX, img_emersamista))
        nulo_emersamista = arcpy.sa.IsNull(img_emersamista)
        funtions_aux.savelog(u"Macrófita Emersa/Mista gerada: %s" % img_emersamista, 0)
        if arcpy.Exists(img_emersamista):
            lista_temp.append(img_emersamista)
            list_delete.append(img_emersamista)

        #GERAÇÃO DO NDVI DENTRO DA ÁREA DE ÁGUA
        img_ndvidentroagua = img_ndvi + "_dentrodaAGUA"
        NDVIdentroagua = arcpy.sa.Over(img_ndvi, img_agua) #VAI MANTER NDVI SOMENTE DENTRO DA AREA DE AGUA
        NDVIdentroagua.save(os.path.join(input_date.GDB_AUX, img_ndvidentroagua))
        list_delete.append(img_ndvidentroagua)
        funtions_aux.savelog(u"NDVI dentro da água gerado: %s" % img_ndvidentroagua, 0)

        #GERAÇÃO DA MACRÓFITA FLUTUANTE
        img_flutuante = img_rec + "_macrofita_F"
        range_macrofita_flu = "-1 " + str(input_date.magic_number_min_macrophytes_flu) +" NODATA;" + str(input_date.magic_number_min_macrophytes_flu) + " " + str(input_date.magic_number_max_macrophytes_flu) + " 7;" + str(input_date.magic_number_max_macrophytes_flu) + " 1 NODATA"
        #"-1 0,200000 NODATA;0,200000 0,750000 7;0,750000 1 NODATA"
        Flutuante = arcpy.sa.Reclassify(img_ndvidentroagua, "VALUE", range_macrofita_flu, "DATA") #CLASSIFICA MACRÓFITA FLUTUANTE
        Flutuante.save(os.path.join(input_date.GDB_AUX, img_flutuante))
        nulo_flutuante = arcpy.sa.IsNull(img_flutuante)
        funtions_aux.savelog(u"Macrófita Flutuante gerada: %s" % img_flutuante, 0)
        if arcpy.Exists(img_flutuante):
            lista_temp.append(img_flutuante)
            list_delete.append(img_flutuante)

        #GERAÇÃO DE MOSAICO TEMPORÁRIO PARA VERIFICAR "GAPS" ENTRE AGUA E OUTRAS CAMADAS
        entradamos_temp = ";".join(lista_temp)
        entradamos_aguanuvem = ";".join(lista_aguanuvem)
        img_mosaico_temp = img_rec + "_mosaico_temp"
        arcpy.management.CreateMosaicDataset(input_date.GDB_AUX, img_mosaico_temp, prj, None, '', "NONE", None)
        if arcpy.Exists(img_nuvem):
            arcpy.management.AddRastersToMosaicDataset(img_mosaico_temp, "Raster Dataset", entradamos_aguanuvem, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)
        else:
            arcpy.management.AddRastersToMosaicDataset(img_mosaico_temp, "Raster Dataset", entradamos_temp, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)
        list_delete.append(img_mosaico_temp)
        funtions_aux.savelog(u"Mosaico TEMP gerado: %s" % img_mosaico_temp, 0)

        #GERAÇÃO CAMADA GAPS
        img_gap = img_rec + "_GAP"
        img_gap_poly= img_rec + "_GAP_poly"
        img_mosaico_agua = img_agua + "_mosaico"
        img_mosaico_agua2 = img_agua + "_mosaico_2"
        if arcpy.Exists(img_nuvem):
            arcpy.conversion.RasterToPolygon(img_mosaico_temp, img_gap, "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
            arcpy.analysis.Union(img_gap, img_gap_poly, "ALL", None, "NO_GAPS")
            arcpy.management.CalculateField(img_gap_poly, "gridcode", "1", "PYTHON3", '', "TEXT")
            arcpy.conversion.PolygonToRaster(img_gap_poly, "gridcode",img_mosaico_agua2, "CELL_CENTER", "NONE", cellsize2) #5.001) #DEIXAR VALOR CELLSIZE DINÂMICO
            TIRANUVEM = arcpy.sa.Con(nulo_nuvem, img_mosaico_agua2)
            TIRANUVEM.save(os.path.join(input_date.GDB_AUX, img_mosaico_agua))
            list_delete.append(img_gap_poly)
            list_delete.append(img_mosaico_agua2)
        else:
            GAP_temp = arcpy.sa.IsNull(img_mosaico_temp)
            GAP = arcpy.sa.Con(GAP_temp, img_masc_ndvi)
            GAP.save(os.path.join(input_date.GDB_AUX, img_gap))
            lista_agua_compl.append(img_gap)
            entradamos_agua = ";".join(lista_agua_compl)
            arcpy.management.CreateMosaicDataset(input_date.GDB_AUX, img_mosaico_agua, prj, None, '', "NONE", None)
            arcpy.management.AddRastersToMosaicDataset(img_mosaico_agua, "Raster Dataset", entradamos_agua, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)
        list_delete.append(img_gap)
        list_delete.append(img_mosaico_agua)
        funtions_aux.savelog(u"Mosaico água gerado: %s" % img_mosaico_agua, 0)

        #GERAÇÃO DA ÁGUA FATIADA - BANDA VERDE - VERIFICAR A BANDA CONFORME SENSOR
        img_aguafatiada_temp = img_rec + "_AguaFatiada_Temp"
        img_aguafatiada = img_rec + "_AguaFatiada"
        img_aguafatiada2 = img_rec + "_AguaFatiada_2"
        img_entrada_BVerde = arcpy.Raster(img_rec+Band_G)
        AguaFatiadatemp = arcpy.ia.Over(img_entrada_BVerde, img_mosaico_agua) #VAI CORTAR A BANDA VERDE NO MESMO LIMITE DA ÁGUA
        #AguaFatiadatemp = arcpy.ia.Over(img_entrada_BVerde, img_agua) #VAI CORTAR A BANDA VERDE NO MESMO LIMITE DA ÁGUA
        AguaFatiadatemp.save(os.path.join(input_date.GDB_AUX, img_aguafatiada_temp))
        AguaFatiadatempreclass = arcpy.sa.Slice(img_aguafatiada_temp, 3, "NATURAL_BREAKS", 1) #VAI SEPARAR A ÁGUA EM TRÊS CLASSES
        AguaFatiadatempreclass.save(os.path.join(input_date.GDB_AUX, img_aguafatiada))
        AguasemsobreposicaoMacroF = arcpy.sa.Con(nulo_flutuante, img_aguafatiada)
        AguasemsobreposicaoMacroF.save(os.path.join(input_date.GDB_AUX, img_aguafatiada2))
        list_delete.append(img_aguafatiada_temp)
        list_delete.append(img_aguafatiada)
        list_delete.append(img_aguafatiada2)

        funtions_aux.savelog(u"Água Fatiada gerada: %s" % img_aguafatiada2, 0)

        #GERAÇÃO MOSAICO CLASSIFICADO
        if arcpy.Exists(img_nuvem):
            lista_final.append(img_nuvem) # 4
        lista_final.append(img_emersamista) # 5 6
        lista_final.append(img_flutuante) # 7
        lista_final.append(img_aguafatiada2) # 1 2 3
        if arcpy.Exists(img_solo_temp2):
            lista_final.append(img_solo_temp2) # 8 9
        entradamos_final = ";".join(lista_final)
        img_mosaico_final = img_rec + "_Classificacao"
        arcpy.management.CreateMosaicDataset(input_date.GDB_AUX, img_mosaico_final, prj, None, '', "NONE", None)
        arcpy.SetMosaicDatasetProperties_management(img_mosaico_final, default_mosaic_method = "ByAttribute", order_field = "ZOrder", order_base = "0")
        arcpy.management.AddRastersToMosaicDataset(img_mosaico_final, "Raster Dataset", entradamos_final, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)
        image_end_raster = input_date.CLASSIFY_GDB + "\\" + mosaic_name + "_Classificado"
        arcpy.management.CopyRaster(img_mosaico_final, image_end_raster, '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
        funtions_aux.savelog("Mosaico FINAL: %s" % img_mosaico_final, 1)
        statis_calc(image_end_raster)
        list_delete.append(img_mosaico_final)

        funtions_aux.savelog(u"Liberando Memória...", 1)
        if input_date.delete_temp:
            for rastername in list_delete: #Clear
                if arcpy.Exists(rastername):
                    arcpy.Delete_management(rastername)

        funtions_aux.savelog("...", 1)

    arcpy.env.workspace = old_workspace

    #print("------------ Feito ----------------")

def statis_calc(raster):
    name_file = raster.split("\\")[-1]
    aux1 = name_file.split("_")

    #name = '_'.join(aux1[0:3])
    data = '_'.join(aux1[3:-2])

    #Consertar datas trocadas e duplicadas
    data = funtions_aux.date_analisy(data, 0)

    aux = "_".join(aux1[0:3]) #Somente nome da barragem e o quadrante

    reservatorio = aux1[0]

    sensor = aux1[-2]

    input_date.dict_sensor[aux] = []
    input_date.dict_sensor[aux].append(sensor)

    funtions_aux.savelog("-> Raster to Polygon...", 0)
    arcpy.conversion.RasterToPolygon(raster, input_date.IMA_VECTOR_GDB + "\\" + aux,  "NO_SIMPLIFY", "Value", "MULTIPLE_OUTER_PART", None)
    funtions_aux.savelog(u"-> Raster to Polygon finalizado! Inicializando a criação de campos...", 0)

    funtions_aux.savelog("-> Criando campos...", 1)

    #Criação da Tabela
    arcpy.AddField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field_name = "Classe", field_type = "TEXT", field_precision = "",field_scale = "",field_length = "",field_alias = "",field_is_nullable="NULLABLE",field_is_required="NON_REQUIRED", field_domain = "")
    arcpy.CalculateField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field = "Classe", expression = "Reclass(!GRIDCODE!)", expression_type = "PYTHON3", code_block = input_date.codeblock)

    calculateFieldExpression  = "'"+data+"'"
    arcpy.AddField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field_name="Date", field_type="TEXT", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.CalculateField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field="Date", expression= calculateFieldExpression , expression_type="PYTHON3", code_block="")

    # Cria Área de cada Classe
    arcpy.AddField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field_name="Area_ha", field_type="DOUBLE", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.CalculateField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field="Area_ha", expression="!Shape_Area!/10000", expression_type="PYTHON3", code_block="")

    # Cria Área Total
    area_total_reservatorio = input_date.grade_espelhodagua + "\\" + reservatorio + "_MASC_MAX"
    area_total = arcpy.da.SearchCursor(area_total_reservatorio, ("Shape_Area")).next()[0]
    exp = "{}".format(area_total)
    arcpy.AddField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field_name="AreaTotal_ha", field_type="DOUBLE", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.CalculateField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field="AreaTotal_ha", expression=exp, expression_type="PYTHON3", code_block="")

    # Cria Percentual
    arcpy.AddField_management(in_table=input_date.IMA_VECTOR_GDB + "\\" + aux, field_name="Perc_Area", field_type="DOUBLE", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
    arcpy.CalculateField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, field="Perc_Area", expression="(!Area_ha!/(!AreaTotal_ha! / 10000) * 100)", expression_type="PYTHON3", code_block="")

    # Execute DeleteField
    dropFields = ["AreaTotal_ha", "Id", "GRIDCODE"]
    arcpy.DeleteField_management(input_date.IMA_VECTOR_GDB + "\\" + aux, dropFields)

    funtions_aux.savelog(u"-> Criação de campos finalizado!", 1)
    funtions_aux.savelog(u"Barragem/Ano/Periodo: " + str(aux) + " -> Classificação finalizada!", 1)

def classify_for_files_sentinel():
    list_end_mosaic = []
    files_numbers = 0

    sensor = "_SENTINEL"

    UHEfc_aux = input_date.lista_imagens_sentinel[0].split("\\")[-1]
    UHEfc = UHEfc_aux.split("_")[0]

    filename_list= []

    #files_numbers = len(input_date.lista_imagens_sentinel)
    filename_list = input_date.lista_imagens_sentinel.copy()

    #fator = files_numbers
    rasters_dict = {}
    parts = 1
    list_shapes = []
    list_delete_shapes = []
    list_end_mosaic = []
    #list_aux_input_imagens = []
    flag_landsat = False
    flag_no_file_exe = False

    filename_list = sorted(filename_list)

    for file_ in filename_list:

        fileT = file_.split("\\")
        file_aux_name = fileT[-1]

        if not "*" in input_date.barragem_filtro:    #Filtro por barragem
            filter_barragem = file_aux_name.split("_")[-9]
            if not input_date.barragem_filtro in filter_barragem:
                continue

        # Filtro caso houver
        if not "*" in input_date.filter_year:
            filter_ = "_".join(file_aux_name.split("_")[-8:-6])
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

    
        #Somente a Data
        date_key_aux1 = file_.split("\\")[-1]
        date_key = '_'.join(date_key_aux1.split("_")[-6:-3])

        if date_key not in rasters_dict:
            rasters_dict[date_key] = []
        rasters_dict[date_key].append(file_)

    rasters = []

    #list_aux_input_imagens = []

    for key, value in sorted(rasters_dict.items(), reverse=True):
        rasters += value

    if len(rasters) > 0:
        date_filename_first_1 = rasters[0].split("\\")[-1]
        date_filename_first_2 = date_filename_first_1.split("_")[3:-3] #-1
        date_filename_first = date_filename_first_2[-1] + "_" + date_filename_first_2[-2] + "_" + date_filename_first_2[-3]

        date_filename_last_1 = rasters[-1].split("\\")[-1]
        date_filename_last_2 = date_filename_last_1.split("_")[3:-3] #-1
        date_filename_last = date_filename_last_2[-1] + "_" + date_filename_last_2[-2] + "_" + date_filename_last_2[-3]

        #year_quad_aux1 = rasters[0].split("\\")[-2]
        year_quad_aux = date_filename_first_1.split("_")
        year_quad = year_quad_aux[1] + "_" + year_quad_aux[2]
        #year_quad = rasters[0].split("\\")[-4]

        if UHEfc == "CAC" or UHEfc == "EUC" or UHEfc == "LMO" or UHEfc == "MOG":
                prj = input_date.prj_23
        else: prj = input_date.prj_22

        #Para não haver repetição de datas
        if date_filename_first == date_filename_last:
            data = date_filename_first
        else:
            data = date_filename_first + '_' + date_filename_last

        mosaic_name = (UHEfc + '_' + year_quad + '_' + data + sensor).upper() #Letras maiusculas com data

        rasters = sorted(rasters)

        for raster in rasters:
            funtions_aux.savelog(u"Processando arquivo: " + str(raster), 1)

            list_delete = []

            UHEfc = mosaic_name[:3]

            lista_temp = []
            lista_agua_compl = []
            lista_final = []
            lista_aguanuvem = []

            file_name = raster.split("\\")[-1]

            sufixo_ = file_name.split("_")[-2] #Pega sufixo para ordenação do dataset

            arcpy.env.mask = input_date.grade_espelhodagua + "\\" + "%s_MASC_MAX" % UHEfc

            if UHEfc == "CAC" or UHEfc == "EUC" or UHEfc == "LMO" or UHEfc == "MOG":
                prj = input_date.prj_23
            else: prj = input_date.prj_22

            Band_B = "\Band_1"
            Band_G = "\Band_2"
            Band_R = "\Band_3"

            #Banda
            if '_RAPIDEYE' in mosaic_name:
                Band_I = "\Band_5"
                n_bands = 5
            else: #LandSat, Sentiner and Planet
                Band_I = "\Band_4"
                n_bands = 4

            img_rec = input_date.GDB_AUX + "\\" + mosaic_name + "_" + str(parts) + "_clip"

            funtions_aux.savelog(u"Arquivo: " + str(raster) + "-> Calculando Estatísticas...", 0)
            arcpy.CalculateStatistics_management(in_raster_dataset=raster, x_skip_factor="1", y_skip_factor="1", ignore_values="", skip_existing="OVERWRITE")
            funtions_aux.savelog(u"Calculo de Estatísticas finalizado...", 0)

            n_max = arcpy.Raster(raster).maximum
            raster_temp = input_date.GDB_AUX + "\\" + mosaic_name + "_temp"
            if n_max == 65535:
                arcpy.gp.SetNull_sa(raster, "1", raster_temp, "VALUE = 65535")
            else:
                arcpy.gp.SetNull_sa(raster, "1", raster_temp, "VALUE = 0")
            # Process: Raster to Polygon
            #funtions_aux.savelog ("-> Raster to polygon...")
            arcpy.RasterToPolygon_conversion(in_raster= raster_temp, out_polygon_features= raster_temp + "_Raster2poly", simplify="NO_SIMPLIFY", raster_field="Value", create_multipart_features="SINGLE_OUTER_PART", max_vertices_per_feature="")
            #funtions_aux.savelog ("-> Dissolve...")
            arcpy.Dissolve_management(raster_temp + "_Raster2poly",raster_temp + "_Raster2poly_Dissolve" + "_" + str(parts), multi_part = "MULTI_PART")
            arcpy.AddField_management(raster_temp + "_Raster2poly_Dissolve" + "_" + str(parts), field_name="File", field_type="TEXT", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
            calculateFieldExpression  = "'"+file_name+"'"
            arcpy.CalculateField_management(raster_temp + "_Raster2poly_Dissolve" + "_" + str(parts), field="File", expression=calculateFieldExpression  , expression_type="PYTHON3", code_block="")

            list_delete.append(raster_temp)
            list_delete.append(raster_temp + "_Raster2poly")
            list_delete_shapes.append(raster_temp + "_Raster2poly_Dissolve" + "_" + str(parts))

            #CLIP DO MOSAICO COM A MÁSCARA DO RESERVATÓRIO
            try:
                arcpy.management.Clip(raster, funtions_aux.get_rect(raster_temp + "_Raster2poly_Dissolve"+ "_" + str(parts)), img_rec , raster_temp + "_Raster2poly", '0', "ClippingGeometry", "NO_MAINTAIN_EXTENT")
            except:
                funtions_aux.savelog(u"Imagem fora do Retângulo Envolvente: %s" % mosaic_name, 1)
                continue

            list_delete.append(img_rec)

            funtions_aux.savelog(u"Imagem recortada com espelho D'água: %s" % mosaic_name, 0)

            arcpy.env.mask = img_rec

            #Get Resolution
            description = arcpy.Describe(img_rec)
            cellsize1 = description.children[0].meanCellHeight  # Cell size in the Y axis and / or
            cellsize2 = description.children[0].meanCellWidth   # Cell size in the X axis

            #GERAÇÃO DO NDVI - VERIFICAR AS BANDAS CONFORME SENSOR
            img_ndvi = img_rec + "_NDVI"
            #NDVI = arcpy.ia.NDVI(img_rec, 5, 3)
            NDVI = (arcpy.Raster(img_rec+Band_I) - arcpy.Raster(img_rec+Band_R)) / (arcpy.Raster(img_rec+Band_I) + arcpy.Raster(img_rec+Band_R)) #RapidEye
            NDVI.save(os.path.join(input_date.GDB_AUX, img_ndvi))
            list_delete.append(img_ndvi)
            funtions_aux.savelog("NDVI gerado: %s" % img_ndvi, 0)

            #GERAÇÃO DE MÁSCARA A PARTIR DO NDVI
            img_masc_ndvi = img_ndvi + "_Mask"
            #funtions_aux.savelog ("NDVI: "+ img_ndvi)
            #funtions_aux.savelog ("MASC_NDVI: " + img_masc_ndvi)
            MASC_NDVI = arcpy.sa.Reclassify(img_ndvi, "Value", "-1 1 1", "DATA");
            MASC_NDVI.save(os.path.join(input_date.GDB_AUX, img_masc_ndvi))
            list_delete.append(img_masc_ndvi)
            funtions_aux.savelog(u"Máscara NDVI gerada: %s" % img_masc_ndvi, 0)

            img_nuvem = img_rec + "_NUVEM"

            if input_date.have_clody_compilation:  #Se usuário quer que as nuvem entre na compilação, mesmo que não tenha nuvens

                #GERAÇÃO DE NUVEM - BANDA AZUL
                img_entrada_BAzul = arcpy.Raster(img_rec+Band_B)
                img_nuvem_temp = img_rec + "_Nuvem_temp"

                img_nuvem_temp_reclassify = img_rec + "_Nuvem_Reclassify"
                img_nuvem_temp_ndvi = img_rec + "_Nuvem_NDVI"

                ValorMAXXpx = arcpy.Raster(img_rec+Band_B).maximum
                ValorTYPEpx = arcpy.GetRasterProperties_management(img_rec+Band_B,"VALUETYPE",'').getOutput(0)

                if (int(ValorMAXXpx) >= input_date.magic_number_8bits and int(ValorTYPEpx) == 3) or (int(ValorMAXXpx) >= input_date.magic_number_16bits and int(ValorTYPEpx) == 5):

                    if '_LANDSAT' in mosaic_name or '_SENTINEL' in mosaic_name:
                        if UHEfc == "CAC":
                            img_nuvem_temp2 = img_rec + "_Nuvem_temp2"
                            NUVEM_temp = arcpy.sa.PrincipalComponents(img_rec, n_bands, None)
                            NUVEM_temp.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp))
                            NUVEM_temp2 = arcpy.sa.Slice(img_nuvem_temp+"\Band_3", 4, "NATURAL_BREAKS", 5) #VAI SEPARAR NUVEM E OUTROS OBJETOS
                            NUVEM_temp2.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp2))
                            NUVEM = arcpy.sa.Reclassify(img_nuvem_temp2, "Value", "4 NODATA;5 NODATA;6 NODATA;7 NODATA;8 4", "NODATA")
                            NUVEM.save(os.path.join(input_date.GDB_AUX, img_nuvem))
                            nulo_nuvem = arcpy.sa.IsNull(img_nuvem)
                            list_delete.append(img_nuvem_temp2)
                        else:
                            NUVEM_temp = arcpy.sa.Slice(img_rec+Band_B, 4, "NATURAL_BREAKS", 4) #VAI SEPARAR NUVEM E OUTROS OBJETOS
                            NUVEM_temp.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp))
                            NUVEM = arcpy.sa.Reclassify(img_nuvem_temp, "Value", "4 NODATA;5 4;6 4;7 4", "NODATA")
                            NUVEM.save(os.path.join(input_date.GDB_AUX, img_nuvem))
                            nulo_nuvem = arcpy.sa.IsNull(img_nuvem)

                    elif '_PLANET' in mosaic_name or '_RAPIDEYE' in mosaic_name:
                            range_reclassify = str(input_date.magic_number_16bits) + " " + str(ValorMAXXpx) + " 4"
                            NUVEM_temp = arcpy.sa.Reclassify(img_rec+Band_B, "Value", range_reclassify, "NODATA")
                            NUVEM_temp.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp_reclassify))
                            NUVEM_temp_1 = arcpy.sa.Reclassify(img_ndvi, "Value", "-0.20 0.29 4", "NODATA") #faixa média de nuvem no NDVI
                            NUVEM_temp_1.save(os.path.join(input_date.GDB_AUX, img_nuvem_temp_ndvi))
                            NUVEM_CON = arcpy.sa.Con(NUVEM_temp_1,NUVEM_temp)
                            NUVEM_CON.save(os.path.join(input_date.GDB_AUX, img_nuvem))
                            nulo_nuvem = arcpy.sa.IsNull(img_nuvem)

                    list_delete.append(img_nuvem_temp)
                    funtions_aux.savelog("Nuvem gerada: %s" % img_nuvem, 0)

                else:
                    funtions_aux.savelog(u"Imagem sem a presença de Nuvens!!!", 0)

                if arcpy.Exists(img_nuvem):
                    list_delete.append(img_nuvem)
                    lista_temp.append(img_nuvem)
                    v_min, v_max = funtions_aux.get_number_class(img_nuvem)
                    if v_max > 2:
                        lista_aguanuvem.append(img_nuvem)

            #GERAÇÃO DA ÁGUA GERAL - BANDA INFRAVERMELHO (IV) - VERIFICAR A BANDA CONFORME SENSOR
            img_agua_temp = img_rec + "_agua_temp"
            img_agua = img_rec + "_AGUA"
            AGUAtemp = arcpy.sa.Slice(img_rec+Band_I, 2, "NATURAL_BREAKS",1) #VAI SEPARAR AGUA E OUTROS OBJETOS
            AGUAtemp.save(os.path.join(input_date.GDB_AUX, img_agua_temp))
            AGUA = arcpy.sa.Reclassify(img_agua_temp, "Value", "1 1", "NODATA") #VAI SALVAR APENAS A AGUA DA BANDA DO (IV)
            AGUA.save(os.path.join(input_date.GDB_AUX, img_agua))
            nulo_agua = arcpy.sa.IsNull(img_agua)
            list_delete.append(img_agua_temp)
            funtions_aux.savelog("Água gerada: %s" % img_agua, 0)
            if arcpy.Exists(img_agua):
                lista_temp.append(img_agua)
                lista_aguanuvem.append(img_agua)
                lista_agua_compl.append(img_agua)
                list_delete.append(img_agua)

            #GERAÇÃO DO SOLO GERAL - BANDA VERMELHO (V) - VERIFICAR A BANDA CONFORME SENSOR
            img_solo_temp = img_rec + "_solo_e_outros_temp"
            img_solo_temp2 = img_solo_temp + "_reclass"
            img_solo = img_rec + "_SOLO"
            img_entrada_BV = arcpy.Raster(img_rec+Band_R)
            if arcpy.Exists(img_nuvem):
                Solotemp = arcpy.sa.Con(nulo_agua & nulo_nuvem,img_entrada_BV) #VAI SOBRERPOR A AREA DE AGUA E TRANSFORMAR EM NODATA E PERMANECE A AREA RESTANTE (SOLO E OUTROS OBJETOS)
            else:
                Solotemp = arcpy.sa.Con(nulo_agua,img_entrada_BV) #VAI SOBRERPOR A AREA DE AGUA E TRANSFORMAR EM NODATA E PERMANECE A AREA RESTANTE (SOLO E OUTROS OBJETOS)
            Solotemp.save(os.path.join(input_date.GDB_AUX, img_solo_temp))
            Solotempreclass = arcpy.sa.Slice(img_solo_temp, 2, "NATURAL_BREAKS", 8) #VAI SEPARAR SOLO E OUTROS OBJETOS
            Solotempreclass.save(os.path.join(input_date.GDB_AUX, img_solo_temp2))
            Solo = arcpy.sa.Reclassify(img_solo_temp2, "Value", "9 9", "NODATA") #VAI SALVAR APENAS O SOLO DA BANDA DO (V)
            Solo.save(os.path.join(input_date.GDB_AUX, img_solo))
            nulo_solo = arcpy.sa.IsNull(img_solo)
            list_delete.append(img_solo_temp)
            list_delete.append(img_solo_temp2)
            funtions_aux.savelog("Solo gerado: %s" % img_solo, 0)

            if arcpy.Exists(img_solo):
                lista_temp.append(img_solo_temp)
                list_delete.append(img_solo)

            #GERAÇÃO DO NDVI FORA DA ÁREA DE ÁGUA E SOLO
            img_ndviforaagua = img_ndvi + "_foradaAGUA"
            NDVIforaagua = arcpy.sa.Con(nulo_agua & nulo_solo, img_ndvi) #VAI MANTER NDVI SOMENTE NA AREA QUE NAO TEM ÁGUA E SOLO
            NDVIforaagua.save(os.path.join(input_date.GDB_AUX, img_ndviforaagua))
            list_delete.append(img_ndviforaagua)
            funtions_aux.savelog(u"NDVI fora da água gerado: %s" % img_ndviforaagua, 0)

            #GERAÇÃO DA MACRÓFITA EMERSA/MISTA
            img_emersamista = img_rec + "_macrofita_EM"
            #range_macrofita_em = "-1 0,200000 NODATA;0,200000 0,750000 5;0,750000 1 6"
            range_macrofita_em = "-1 " + str(input_date.magic_number_min_macrophytes) + " NODATA;" + str(input_date.magic_number_min_macrophytes) + " " + str(input_date.magic_number_max_macrophytes) +" 5;" + str(input_date.magic_number_max_macrophytes) +" 1 8"
            EmersaMista = arcpy.sa.Reclassify(img_ndviforaagua, "VALUE", range_macrofita_em, "DATA") #CLASSIFICA MACRÓFITA EMERSA/MISTA
            EmersaMista.save(os.path.join(input_date.GDB_AUX, img_emersamista))
            nulo_emersamista = arcpy.sa.IsNull(img_emersamista)
            funtions_aux.savelog(u"Macrófita Emersa/Mista gerada: %s" % img_emersamista, 0)
            if arcpy.Exists(img_emersamista):
                lista_temp.append(img_emersamista)
                list_delete.append(img_emersamista)

            #GERAÇÃO DO NDVI DENTRO DA ÁREA DE ÁGUA
            img_ndvidentroagua = img_ndvi + "_dentrodaAGUA"
            NDVIdentroagua = arcpy.sa.Over(img_ndvi, img_agua) #VAI MANTER NDVI SOMENTE DENTRO DA AREA DE AGUA
            NDVIdentroagua.save(os.path.join(input_date.GDB_AUX, img_ndvidentroagua))
            list_delete.append(img_ndvidentroagua)
            funtions_aux.savelog(u"NDVI dentro da água gerado: %s" % img_ndvidentroagua, 0)

            #GERAÇÃO DA MACRÓFITA FLUTUANTE
            img_flutuante = img_rec + "_macrofita_F"
            #range_macrofita_flu = "-1 0,200000 NODATA;0,200000 0,750000 7;0,750000 1 NODATA"
            range_macrofita_flu = "-1 " + str(input_date.magic_number_min_macrophytes) +" NODATA;" + str(input_date.magic_number_min_macrophytes) + " " + str(input_date.magic_number_max_macrophytes) + " 7;" + str(input_date.magic_number_max_macrophytes) + " 1 NODATA"
            Flutuante = arcpy.sa.Reclassify(img_ndvidentroagua, "VALUE", range_macrofita_flu, "DATA") #CLASSIFICA MACRÓFITA FLUTUANTE
            Flutuante.save(os.path.join(input_date.GDB_AUX, img_flutuante))
            nulo_flutuante = arcpy.sa.IsNull(img_flutuante)
            funtions_aux.savelog(u"Macrófita Flutuante gerada: %s" % img_flutuante, 0)
            if arcpy.Exists(img_flutuante):
                lista_temp.append(img_flutuante)
                list_delete.append(img_flutuante)

            #GERAÇÃO DE MOSAICO TEMPORÁRIO PARA VERIFICAR "GAPS" ENTRE AGUA E OUTRAS CAMADAS
            entradamos_temp = ";".join(lista_temp)
            entradamos_aguanuvem = ";".join(lista_aguanuvem)
            img_mosaico_temp = img_rec + "_mosaico_temp"
            arcpy.management.CreateMosaicDataset(input_date.GDB_AUX, img_mosaico_temp, prj, None, '', "NONE", None)
            if arcpy.Exists(img_nuvem):
                arcpy.management.AddRastersToMosaicDataset(img_mosaico_temp, "Raster Dataset", entradamos_aguanuvem, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)
            else:
                arcpy.management.AddRastersToMosaicDataset(img_mosaico_temp, "Raster Dataset", entradamos_temp, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)
            list_delete.append(img_mosaico_temp)
            funtions_aux.savelog(u"Mosaico TEMP gerado: %s" % img_mosaico_temp, 0)

            #GERAÇÃO CAMADA GAPS
            img_gap = img_rec + "_GAP"
            img_gap_poly= img_rec + "_GAP_poly"
            img_mosaico_agua = img_agua + "_mosaico"
            img_mosaico_agua2 = img_agua + "_mosaico_2"
            if arcpy.Exists(img_nuvem):
                arcpy.conversion.RasterToPolygon(img_mosaico_temp, img_gap, "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
                img_gap = img_gap + " #"
                funtions_aux.savelog(u"img_gap: %s" % img_gap, 0)
                funtions_aux.savelog(u"img_gap_poly: %s" % img_gap_poly, 0)

                arcpy.analysis.Union(img_gap, img_gap_poly, "ALL", None, "NO_GAPS")

                arcpy.management.CalculateField(img_gap_poly, "gridcode", "1", "PYTHON3", '', "TEXT")
                arcpy.conversion.PolygonToRaster(img_gap_poly, "gridcode",img_mosaico_agua2, "CELL_CENTER", "NONE", cellsize2) #5.001) #DEIXAR VALOR CELLSIZE DINÂMICO
                TIRANUVEM = arcpy.sa.Con(nulo_nuvem, img_mosaico_agua2)
                TIRANUVEM.save(os.path.join(input_date.GDB_AUX, img_mosaico_agua))
                list_delete.append(img_gap_poly)
                list_delete.append(img_mosaico_agua2)
            else:
                GAP_temp = arcpy.sa.IsNull(img_mosaico_temp)
                GAP = arcpy.sa.Con(GAP_temp, img_masc_ndvi)
                GAP.save(os.path.join(input_date.GDB_AUX, img_gap))
                lista_agua_compl.append(img_gap)
                entradamos_agua = ";".join(lista_agua_compl)
                arcpy.management.CreateMosaicDataset(input_date.GDB_AUX, img_mosaico_agua, prj, None, '', "NONE", None)
                arcpy.management.AddRastersToMosaicDataset(img_mosaico_agua, "Raster Dataset", entradamos_agua, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)
            list_delete.append(img_gap)
            list_delete.append(img_mosaico_agua)
            funtions_aux.savelog(u"Mosaico água gerado: %s" % img_mosaico_agua, 0)

            #GERAÇÃO DA ÁGUA FATIADA - BANDA VERDE - VERIFICAR A BANDA CONFORME SENSOR
            img_aguafatiada_temp = img_rec + "_AguaFatiada_Temp"
            img_aguafatiada = img_rec + "_AguaFatiada"
            img_aguafatiada2 = img_rec + "_AguaFatiada_2"
            img_entrada_BVerde = arcpy.Raster(img_rec+Band_G)
            AguaFatiadatemp = arcpy.ia.Over(img_entrada_BVerde, img_mosaico_agua) #VAI CORTAR A BANDA VERDE NO MESMO LIMITE DA ÁGUA
            AguaFatiadatemp.save(os.path.join(input_date.GDB_AUX, img_aguafatiada_temp))
            AguaFatiadatempreclass = arcpy.sa.Slice(img_aguafatiada_temp, 3, "NATURAL_BREAKS", 1) #VAI SEPARAR A ÁGUA EM TRÊS CLASSES
            AguaFatiadatempreclass.save(os.path.join(input_date.GDB_AUX, img_aguafatiada))
            AguasemsobreposicaoMacroF = arcpy.sa.Con(nulo_flutuante, img_aguafatiada)
            AguasemsobreposicaoMacroF.save(os.path.join(input_date.GDB_AUX, img_aguafatiada2))
            list_delete.append(img_aguafatiada_temp)
            list_delete.append(img_aguafatiada)
            list_delete.append(img_aguafatiada2)

            funtions_aux.savelog(u"Água Fatiada gerada: %s" % img_aguafatiada2, 0)

            #GERAÇÃO MOSAICO CLASSIFICADO
            if arcpy.Exists(img_nuvem):
                lista_final.append(img_nuvem) # 4
            lista_final.append(img_emersamista) # 5 6
            lista_final.append(img_flutuante) # 7
            lista_final.append(img_aguafatiada2) # 1 2 3
            if arcpy.Exists(img_solo_temp2):
                lista_final.append(img_solo_temp2) # 8 9
            entradamos_final = ";".join(lista_final)
            img_mosaico_final = img_rec + "_Classificacao_" + sufixo_
            arcpy.management.CreateMosaicDataset(input_date.GDB_AUX, img_mosaico_final, prj, None, '', "NONE", None)
            arcpy.SetMosaicDatasetProperties_management(img_mosaico_final, default_mosaic_method = "ByAttribute", order_field = "ZOrder", order_base = "0")
            arcpy.management.AddRastersToMosaicDataset(img_mosaico_final, "Raster Dataset", entradamos_final, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)
            arcpy.management.CopyRaster(img_mosaico_final, img_mosaico_final + "_" + str(parts), '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
            list_delete.append(img_mosaico_final)
            list_end_mosaic.append(img_mosaico_final + "_" + str(parts))
            parts+=1
            funtions_aux.savelog("Mosaico FINAL: %s" % img_mosaico_final, 0)

            if input_date.delete_temp:
                for rastername in list_delete: #Clear
                    if arcpy.Exists(rastername):
                        arcpy.Delete_management(rastername)

            funtions_aux.savelog(u"Processamentp do arquivo: " + str(raster) + " finalizado.", 1)

        funtions_aux.savelog(u"Finalizando a Classificação...",1)

        if len (list_end_mosaic) > 0:
            image_end = input_date.GDB_AUX + "\\" + mosaic_name + "_Classificado"
            image_end_raster = input_date.CLASSIFY_GDB + "\\" + mosaic_name + "_Classificado"
            arcpy.management.CreateMosaicDataset(input_date.GDB_AUX, image_end, prj, None, '', "NONE", None)
            arcpy.management.AddRastersToMosaicDataset(image_end, "Raster Dataset", list_end_mosaic, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None)

            #Colocar ZOrder em ordem crescente
            with arcpy.da.UpdateCursor(image_end, ["Name","ZOrder"]) as cursor:
                for row in cursor:
                    name = row[0]
                    prefix_name = name.split("_")[-2]
                    prefix_name_2 = name.split("_")[-1]
                    if prefix_name.isdigit():
                        digital = int(prefix_name) #name[0:3])
                    else:
                        digital = 999 + int(prefix_name_2) #Garantir a ordem alfabéica
                    row[1]  = digital
                    cursor.updateRow(row)
     
            arcpy.SetMosaicDatasetProperties_management(image_end, default_mosaic_method = "ByAttribute", allowed_mosaic_methods = "ByAttribute", order_field = "ZOrder", order_base = "0")
            arcpy.management.CopyRaster(image_end, image_end_raster, '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
            funtions_aux.savelog("Imagem Classificada: %s" % mosaic_name, 1)

            if input_date.delete_temp_global:
                if arcpy.Exists(image_end):
                    arcpy.Delete_management(image_end)

            statis_calc(image_end_raster)
            #arcpy.Merge_management(list_shapes, input_date.CLASSIFY_GDB + "\\" + mosaic_name + "_Masc")

        funtions_aux.savelog(u"Liberando Memória...", 1)
        for rastername1 in list_end_mosaic: #Clear
            if arcpy.Exists(rastername1):
                arcpy.Delete_management(rastername1)
        if input_date.delete_temp:
            for listdelShapes in list_delete_shapes: #Deleta apenas dos shapes
                if arcpy.Exists(listdelShapes):
                    arcpy.Delete_management(listdelShapes)
        funtions_aux.savelog("...", 1)

        #print("------------ Feito ----------------")

