# -*- coding: utf-8 -*-

import input_date
import funtions_aux
import arcpy
import os

#----Enveloped-----

# ---- Recorte da Imagem de Fundo
def image_recorte():

    raster_agv = []
    raster_bab = []
    raster_pro = []
    raster_nav = []
    raster_bar = []
    raster_ibi = []
    raster_cac = []
    raster_euc = []
    raster_lmo = []
    raster_mog = []

    arcpy.env.workspace = input_date.GDB_AUX

    datasets = arcpy.ListDatasets(feature_type='Raster')

    RESERVATORIOS_GDB = arcpy.env.workspace

    for rastername in datasets:
        if 'RAPIDEYE' in rastername: continue # Imagens RapidEyes não precisa de fundo
        if 'PLANET'   in rastername: continue # Imagens Planets não precisam de fundo
        if 'SENTINEL' in rastername: continue # Imagens Sentinel não precisam de fundo

        if '222074' in rastername:
            raster_agv.append(os.path.join(RESERVATORIOS_GDB, rastername))
            continue
        if '222075' in rastername:
            raster_nav.append(os.path.join(RESERVATORIOS_GDB, rastername))
            continue
        if '221074' in rastername:
            raster_agv.append(os.path.join(RESERVATORIOS_GDB, rastername))
            continue
        if '221075' in rastername:
            if 'IBI' in rastername:
                raster_ibi.append(os.path.join(RESERVATORIOS_GDB, rastername))
            elif 'PRO' in rastername:
                raster_pro.append(os.path.join(RESERVATORIOS_GDB, rastername))
            elif 'NAV' in rastername:
                raster_nav.append(os.path.join(RESERVATORIOS_GDB, rastername))
            elif 'BAR' in rastername:
                raster_bar.append(os.path.join(RESERVATORIOS_GDB, rastername))
            continue
        if '220075' in rastername:
            if 'EUC' in rastername:
                raster_euc.append(os.path.join(RESERVATORIOS_GDB, rastername))
            elif 'LMO' in rastername:
                raster_lmo.append(os.path.join(RESERVATORIOS_GDB, rastername))
            continue
        if '220076' in rastername:
            if 'BAB' in rastername:
                raster_bab.append(os.path.join(RESERVATORIOS_GDB, rastername))
            elif 'BAR' in rastername:
                raster_bar.append(os.path.join(RESERVATORIOS_GDB, rastername))
            continue
        if '219075' in rastername:
            raster_cac.append(os.path.join(RESERVATORIOS_GDB, rastername))
            continue
        if '219076' in rastername:
            raster_mog.append(os.path.join(RESERVATORIOS_GDB, rastername))
            continue

    arcpy.env.workspace = input_date.IMA_RESERVATORIOS_GDB

    if raster_bab:
        funtions_aux.savelog("Processando imagem de Barra Bonita...", 1)
        do_recort_enveloped("BAB_MASC_Envelope",raster_bab,"BAB_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)
    if raster_ibi:
        funtions_aux.savelog("Processando imagem de Ibitinga...", 1)
        do_recort_enveloped("IBI_MASC_Envelope",raster_ibi,"IBI_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)
    if raster_pro:
        funtions_aux.savelog("Processando imagem de Promissão...", 1)
        do_recort_enveloped("PRO_MASC_Envelope",raster_pro,"PRO_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)
    if raster_cac:
        funtions_aux.savelog("Processando imagem de Caconde...", 1)
        do_recort_enveloped("CAC_MASC_Envelope",raster_cac,"CAC_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)
    if raster_euc:
        funtions_aux.savelog("Processando imagem de Euclides da Cunha...", 1)
        do_recort_enveloped("EUC_MASC_Envelope",raster_euc,"EUC_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)
    if raster_lmo:
        funtions_aux.savelog("Processando imagem de Limoeiro...", 1)
        do_recort_enveloped("LMO_MASC_Envelope",raster_lmo,"LMO_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)
    if raster_mog:
        funtions_aux.savelog("Processando imagem de Mogi-Guaçu...", 1)
        do_recort_enveloped("MOG_MASC_Envelope",raster_mog,"MOG_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)

    #Barragens que precisam de Mosaico
    if raster_agv:
        funtions_aux.savelog("Processando imagem de Água Vermelha...", 1)
        do_juncao_image("AGV_MASC_Envelope",raster_agv,"AGV_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)
    if raster_nav:
        funtions_aux.savelog("Processando imagem de Nova Avanhandava...", 1)
        do_juncao_image("NAV_MASC_Envelope",raster_nav,"NAV_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)
    if raster_bar:
        funtions_aux.savelog("Processando imagem de Bariri...", 1)
        do_juncao_image("BAR_MASC_Envelope",raster_bar,"BAR_MASC_MAX")
        funtions_aux.savelog("Finalizado!", 1)

# Para imagens que apenas usam uma orbita ponto
def do_recort_enveloped(envelope, lista, reservatorio):
    flag = True
    for rastername in lista:
        name = envelope[:3]

        name_raster = rastername.split("_")
        data = name_raster[-3] + "_" + name_raster[-4] + "_" + name_raster[-5]

        aux = name + "_" + name_raster[-7] + "_" + name_raster[-6] + "_" + data + "_LANDSAT"

        if flag:
           funtions_aux.savelog("-> Recortando a imagem de fundo...", 1)
           flag = False
        arcpy.management.Clip(rastername, "#", rastername + "_clip", input_date.grade_espelhodagua + "\\" + envelope,'', "ClippingGeometry", "NO_MAINTAIN_EXTENT")

        if arcpy.Exists(rastername + "_clip"):
            arcpy.management.CopyRaster(rastername + "_clip", input_date.IMA_RESERVATORIOS_GDB + "\\" +  aux, '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
            arcpy.Delete_management(rastername + "_clip")


# Função utilizado para barragens que utilizam 2 orbitas ponto - Ou seja, precisa que sejam Mosaicada
def do_juncao_image(envelope, lista, reservatorio):

    dic_date = {} #Dicionário de Datas

    lista1 = []
    lista2 = []
    lista1_s = []
    lista2_s = []
    lista_end = []

    if envelope == "AGV_MASC_Envelope":
        for rastername in lista:
            if '221074' in rastername:
                lista1.append(rastername)
            elif '222074' in rastername:
                lista2.append(rastername)

    if envelope == "NAV_MASC_Envelope":
        for rastername in lista:
            if '222075' in rastername:
                lista1.append(rastername)
            elif '221075' in rastername:
                lista2.append(rastername)

    if envelope == "BAR_MASC_Envelope":
        for rastername in lista:
            if '221075' in rastername:
                lista1.append(rastername)
            elif '220076' in rastername:
                lista2.append(rastername)

    lista1_s = sorted(lista1)
    lista2_s = sorted(lista2)

    for name_raster in lista1_s:
        ima = ''
        mosaico_test = []
        name_res = envelope[:3]
        raster_name_aux = name_raster.split("\\")[-1]
        raster_name = raster_name_aux.split("_")
        aux = raster_name[-8] + "_" + raster_name[-6]
        auxx = raster_name[-7] + "_" + raster_name[-6]
        mosaico_reservatorio = ''
        data_1 = raster_name[-3] + "_" + raster_name[-4] + "_" + raster_name[-5]

        for name_raster2 in lista2_s:
            if auxx in name_raster2:
               ima = "%s;%s"%(name_raster, name_raster2)
               mosaico_test.append(name_raster)
               mosaico_test.append(name_raster2)
               raster_name_aux2 = name_raster2.split("\\")[-1]
               raster_name2 = raster_name_aux2.split("_")
               data_2 = raster_name2[-3] + "_" + raster_name2[-4] + "_" + raster_name2[-5]
               while name_raster2 in lista2_s: lista2_s.remove(name_raster2)
               break
        if not ima == '':
            mosaico_reservatorio = envelope + "_juncao_" + name_res + "_" + auxx
            arcpy.management.CreateMosaicDataset(input_date.IMA_RESERVATORIOS_GDB, mosaico_reservatorio, input_date.prj_22 , None, '', "NONE", None)
            arcpy.management.AddRastersToMosaicDataset( mosaico_reservatorio, "Raster Dataset", mosaico_test)
            #Colocar ZOrder em ordem crescente
            fc = input_date.IMA_RESERVATORIOS_GDB + "\\" + mosaico_reservatorio
            with arcpy.da.UpdateCursor(fc, ["Name","ZOrder"]) as cursor:
                for row in cursor:
                    name = row[0]
                    prefix_name = name.split("_")[0]
                    if prefix_name.isdigit():
                        digital = int(name[0:3])
                    else:
                        digital = 999
                    row[1]  = digital
                    cursor.updateRow(row)
            arcpy.management.BuildFootprints(mosaico_reservatorio, '', "RADIOMETRY", 1, 65534, -1, 0, "NO_MAINTAIN_EDGES", "SKIP_DERIVED_IMAGES", "UPDATE_BOUNDARY", 2000, 100, "NONE", None, 20, 0.05)
            arcpy.SetMosaicDatasetProperties_management(mosaico_reservatorio, default_mosaic_method = "ByAttribute", allowed_mosaic_methods = "ByAttribute", order_field = "ZOrder", order_base = "0")
            lista_end.append(mosaico_reservatorio)

        else:
            mosaico_reservatorio = envelope + "_juncao_" + name_res + "_" + auxx
            arcpy.management.CopyRaster(name_raster, input_date.IMA_RESERVATORIOS_GDB + "\\" +  mosaico_reservatorio, '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
            lista_end.append(mosaico_reservatorio)

        #Datas
        if len(data_1) > 0:
            if len(data_2) > 0:
                if data_1 == data_2:
                    date = data_1
                else:
                    date = data_1 + "_" + data_2
            else:
                date = data_1
        else:
            date = ''

       #Consertar datas trocadas
        if len(date) > 10:
            data1 = date [:10]
            data2 = date [11:]
            if data1 == data2:
                date = data1
            else:
                mes1 = int(date [3:5])
                mes2 = int(date [14:16])
                if mes1 == mes2:
                    dia1 = int(date[0:2])
                    dia2 = int(date[11:13])
                    if dia1 > dia2: date = data2 + "_" + data1
                else:
                    if mes1 > mes2:
                        date = data2 + "_" + data1
        dic_date[mosaico_reservatorio] = []
        dic_date[mosaico_reservatorio].append(date)

        if input_date.file_or_mosaic == 1:
            #Add imagens Landasat para fazer processamento por arquivos
            aux_1 = envelope[:3] + "_" + mosaico_reservatorio[-6::] + "Q_" + date
            input_date.dict_landsat[aux_1] = []
            input_date.dict_landsat[aux_1].append(ima)

    if lista2_s:
        for name_raster in lista2_s:
            raster_name_aux = name_raster.split("\\")[-1]
            raster_name = raster_name_aux.split("_")
            date = raster_name[-3] + "_" + raster_name[-4] + "_" + raster_name[-5]
            aux = raster_name[-8] + "_" + raster_name[-7] + "_" + raster_name[-6]
            mosaico_reservatorio = envelope + "_juncao_" + aux
            arcpy.management.CopyRaster(name_raster, input_date.IMA_RESERVATORIOS_GDB + "\\" +  mosaico_reservatorio, '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
            lista_end.append(mosaico_reservatorio)
            dic_date[mosaico_reservatorio] = []
            dic_date[mosaico_reservatorio].append(date)

    flag = True

    for rastername in lista_end:
        if "D:\\" in rastername:
            aux_dir = rastername.split("\\")[-1]
            aux = aux_dir[-19:-9] + "_" + "_LANDSAT"
        else:
            aux = rastername[-11::] + "_" + dic_date[rastername][0] + "_LANDSAT"

        if flag:
           funtions_aux.savelog("-> Recortando a imagem de fundo...", 1)
           flag = False

        arcpy.management.Clip(rastername, "#", rastername + "_clip", input_date.grade_espelhodagua + "\\" + envelope,'', "ClippingGeometry", "NO_MAINTAIN_EXTENT")

        if arcpy.Exists(rastername):
            arcpy.Rename_management(rastername + "_clip", aux)

    for rastername in lista_end: #Clear the "juncoes"
        if arcpy.Exists(rastername):
            arcpy.Delete_management(rastername)

