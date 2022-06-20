import arcpy
import input_date
import os
import landsat_sentinel_module
import rapideye_planet_module
import funtions_aux
import glob

def ajust_images(dirpath, filess, list_dir, sensor):
    flag_sentinel = 0
    jp2_flag = 0
    list_delete = []
    rasters = []
    filess_list = []

    list_dir_sorted = sorted(list_dir) #Ordernar a lista de arquivos
    number_img = len(list_dir_sorted)

    for filenames in list_dir_sorted:
        # Filtro caso houver
        if not "*" in input_date.barragem_filtro:    #Filtro por barragem
            filter_barragem = filenames.split("\\")[-4]
            if not input_date.barragem_filtro in filter_barragem:
                return
        if not "*" in input_date.filter_year:       #filtro por ano e quadrante
            filter_ = filenames.split("\\")[-3]
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

        flag_sentinel = 0
        filess_list = []
        rasters = []
        sufix = ""
        for x in glob.glob(filenames + "\\*.tif"):
            filess_list.append(x)
        for x in glob.glob(filenames + "\\*.jp2"):
            filess_list.append(x)

        for filename in filess_list:
            if 'B02' in filename or 'B03' in filename or 'B04' in filename or 'B08' in filename:
                sufix_aux = os.path.basename(filename).split('\\')[-1]
                sufix = sufix_aux.split("_")[0]
                if sufix=="000": continue
                ext = os.path.basename(filename).split('.')[-1].lower()
                title = os.path.basename(filename).split('.')[0]
                if ext == "jp2":
                    arcpy.conversion.RasterToOtherFormat(os.path.join(filenames, filename),input_date.GDB_AUX, "TIFF")
                    arcpy.management.CopyRaster(input_date.GDB_AUX + "\\" + title, os.path.join(filenames, title) + ".tif", '', None, "65535", "NONE", "NONE", '', "NONE", "NONE", "TIFF", "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
                    list_delete.append(input_date.GDB_AUX + "\\" + title) #auxiliar dentro do banco
                    input_date.list_jp2_to_tif.append(os.path.join(filenames, title) + ".tif")
                    input_date.list_jp2_to_tif.append(os.path.join(filenames, title) + ".tif.xml")
                    input_date.list_jp2_to_tif.append(os.path.join(filenames, title) + ".tif.aux.xml")
                    input_date.list_jp2_to_tif.append(os.path.join(filenames, title) + ".tfw")
                    input_date.list_jp2_to_tif.append(os.path.join(filenames, title) + ".tif.ovr")
                    rasters.append(os.path.join(filenames, title) + ".tif")
                    jp2_flag = 1
                    flag_sentinel+=1
                else:
                    rasters.append(os.path.join(filenames, filename))
                    flag_sentinel+=1
                #flag_sentinel+=1
            else: #Se for uma banda só
                raster = os.path.join(filenames, filename)
                desc = arcpy.Describe(raster)
                if (desc.bandCount) == 4:
                    subfolders = filenames.split("\\")
                    rastername = subfolders[-4] + "_" + subfolders[-3] + "_" + subfolders[-1]
                    landsat_sentinel_module.ajust_images_special(raster, rastername, sensor)
                    return

        if flag_sentinel == 4:
            if number_img == 1: # Se for apenas um diretório
                subfolders = filenames.split("\\")
                rastername = subfolders[-4] + "_" + subfolders[-3] + "_" + subfolders[-1]
                if arcpy.Exists(rastername): continue  #Já existe
                else: landsat_sentinel_module.ajust_images(rasters, rastername, sensor)
            else:
                #input_date.sentinel_multi = 1
                subfolders = filenames.split("\\")
                rastername = subfolders[-4] + "_" + subfolders[-3] + "_" + subfolders[-1] + "_COMP_" + sufix
                make_composite(rasters, rastername, flag_sentinel)

        elif flag_sentinel > 4:
            #input_date.sentinel_multi = 1
            subfolders = filenames.split("\\")
            rastername = subfolders[-4] + "_" + subfolders[-3] + "_" + subfolders[-1] + "_COMP_" + sufix
            make_composite(rasters, rastername, flag_sentinel)

        if flag_sentinel:
            if input_date.delete_temp and jp2_flag:
                funtions_aux.savelog (u"Apagando arquivos temporários...", 1)
                for rastername_delete in list_delete: #Clear
                    if arcpy.Exists(rastername_delete):
                        arcpy.Delete_management(rastername_delete)
            continue

    if number_img > 1:
        ajust_images2(input_date.lista_imagens_sentinel, sensor)


def make_composite(rasters, rastername, number_img):

    imagens = number_img//4 # pega parte inteira

    lista = [[] for _ in range(imagens)]

    banda = item = 0

    for ima in rasters:
        #print (ima)
        if   "B02" in ima:
            lista[item].append(ima)
            banda+=1

        elif "B03" in ima:
            lista[item].append(ima)
            banda+=1

        elif "B04" in ima:
            lista[item].append(ima)
            banda+=1

        elif "B08" in ima:
            lista[item].append(ima)
            banda+=1

        if banda == 4:
            banda = 0
            item +=1

    funtions_aux.savelog("-> Fazendo o Composite...", 1)

    for item1 in range(imagens):
        name = input_date.GDB_AUX + "\\" + rastername + "_" + str(item1)
        arcpy.env.compression = "JPEG2000 100"
        arcpy.CompositeBands_management(lista[item1], name)
        input_date.list_jp2_to_tif.append(name)
        input_date.lista_imagens_sentinel.append(name)

    funtions_aux.savelog(u"-> Composite finalizado! Verificando a projeção da imagem...", 1)

# -------------------- Algoritmo para imagens SENTINEL

def build_rasters(dirpath_images_original, sensor):

    arcpy.env.workspace = input_date.IMA_RESERVATORIOS_GDB

    rasters_dict = {}

    #print ("Originais:")
    #print (dirpath_images_original)

    UHEfc_aux1 = dirpath_images_original[0].split("\\")[-1]
    UHEfc_aux = '_'.join(UHEfc_aux1.split("_")[:-3]) #-2
    UHEfc = UHEfc_aux.split("_")[-6]

    for raster in dirpath_images_original:

        date_key_aux1 = raster.split("\\")[-1]
        #date_key_aux = '_'.join(date_key_aux1.split("_")[:-3]) #-2
        date_key = '_'.join(date_key_aux1.split("_")[-6:-3]) #:

        if date_key not in rasters_dict:
            rasters_dict[date_key] = []
        rasters_dict[date_key].append(raster)
    rasters_ = []

    for key, value in sorted(rasters_dict.items(), reverse=True):
        rasters_ += value

    rasters = sorted(rasters_) #Ordernar a lista

    #print ("Ordenados:")
    #print (rasters)

    if len(rasters) > 0:
        date_filename_first_1 = rasters[0].split("\\")[-1]
        date_filename_first_2 = date_filename_first_1.split("_")[:-3] #4
        date_filename_first = date_filename_first_2[-1] + "_" + date_filename_first_2[-2] + "_" + date_filename_first_2[-3]

        date_filename_last_1 = rasters[-1].split("\\")[-1]
        date_filename_last_2 = date_filename_last_1.split("_")[:-3] #4
        date_filename_last = date_filename_last_2[-1] + "_" + date_filename_last_2[-2] + "_" + date_filename_last_2[-3]

        #year_quad = rasters[0].split("\\")[-4]
        year_quad_aux = date_filename_first_1.split("_")[-8:-6] #-5,-3
        year_quad = year_quad_aux[-1] + "_" + year_quad_aux[-2] #Inverter

        if UHEfc == "CAC" or UHEfc == "EUC" or UHEfc == "LMO" or UHEfc == "MOG":
                prj = input_date.prj_23
        else: prj = input_date.prj_22

        #Para não haver repetição de datas
        if date_filename_first == date_filename_last:
            data = date_filename_first
        else:
            data = date_filename_first + '_' + date_filename_last

        mosaic_name = (UHEfc + '_' + year_quad + '_' + data + sensor).upper() #Letras maiusculas com data

        funtions_aux.savelog("-> Gerando o Mosaico Dataset...", 1)
        dataset_name = mosaic_name + "_dataset"
        arcpy.management.CreateMosaicDataset(arcpy.env.workspace, dataset_name, prj , None, '', "NONE", None)
        arcpy.management.AddRastersToMosaicDataset( arcpy.env.workspace + "\\" + dataset_name, "Raster Dataset", rasters)
        #, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", None) #, r"C:\Users\optimus\AppData\Local\ESRI\rasterproxies\\" + dataset_name)

        #Colocar ZOrder em ordem crescente
        fc = arcpy.env.workspace + "\\" + dataset_name
        with arcpy.da.UpdateCursor(fc, ["Name","ZOrder"]) as cursor:
            for row in cursor:
                name = row[0]
                prefix_name = name.split("_")[-2] #0
                if prefix_name.isdigit():
                    digital = int(prefix_name) #name[0:3])
                else:
                    digital = 999
                row[1]  = digital
                cursor.updateRow(row)
        #arcpy.management.CalculateField(fc, "ZOrder", "!Name![0:3]", "PYTHON3", '', "TEXT")
        arcpy.management.BuildFootprints(arcpy.env.workspace + "\\" + dataset_name, '', "RADIOMETRY", 1, 65534, -1, 0, "NO_MAINTAIN_EDGES", "SKIP_DERIVED_IMAGES", "UPDATE_BOUNDARY", 2000, 100, "NONE", None, 20, 0.05)
        arcpy.SetMosaicDatasetProperties_management(arcpy.env.workspace + "\\" + dataset_name, default_mosaic_method = "ByAttribute", allowed_mosaic_methods = "ByAttribute", order_field = "ZOrder", order_base = "0")
        arcpy.management.CopyRaster(arcpy.env.workspace + "\\" + dataset_name, mosaic_name, '', None, '', "NONE", "NONE", '', "NONE", "NONE", '', "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")

        if input_date.delete_temp_global:
            if arcpy.Exists(arcpy.env.workspace + "\\" + dataset_name):
                arcpy.Delete_management(arcpy.env.workspace + "\\" + dataset_name)

        funtions_aux.savelog("-> Mosaico Finalizado!", 1) # Calculando o NDVI...")

        funtions_aux.savelog("Arquivo: " + str(mosaic_name) + "-> Finalizado", 1)

        print("...")

# --------------------------------------------

def ajust_images2(filename_list, sensor):

    flag = 1
    filename_list_filter  = []
    list_shapes           = []
    list_delete           = []
    parts = 0

    filename_list = sorted(filename_list) #Ordernar a lista de arquivos

    for raster_ in filename_list:

        filename = raster_.split("\\")[-1]
    
        input_date.list_ima_original.append(raster_)

        funtions_aux.savelog(u"-> Verificando a projeção da imagem...", 1)

        filename_list_filter.append(raster_)

        funtions_aux.verify_name_projetion(raster_) # Verifica e arruma nomes errados de projeção

        proj = funtions_aux.verify_projetion(raster_) # Reprojeta

        if proj == 1:
            funtions_aux.savelog("-> Imagem foi Reprojetada.", 1)
        elif proj == 0:
            sys.exit() # Finaliza o programa
        else:
            funtions_aux.savelog(u"-> Imagem com projeção correta!", 1)

        # Process: Calculate Statistics
        if flag:
            funtions_aux.savelog (u"-> Calculando Estatísticas...", 1)
            flag = 0
        arcpy.CalculateStatistics_management(in_raster_dataset=raster_, x_skip_factor="1", y_skip_factor="1", ignore_values="", skip_existing="OVERWRITE")
        funtions_aux.savelog ("Processando...", 1)
        funtions_aux.savelog ("-> Set Null...", 0)
        # Process: Set Null
        n_max = arcpy.Raster(raster_).maximum
        raster_temp = input_date.GDB_AUX + "\\" + filename + "_temp"
        if n_max == 65535:
            arcpy.gp.SetNull_sa(raster_, "1", raster_temp, "VALUE = 65535")
        else:
            arcpy.gp.SetNull_sa(raster_, "1", raster_temp, "VALUE = 0")

        # Process: Raster to Polygon
        funtions_aux.savelog ("-> Raster to polygon...", 0)
        arcpy.RasterToPolygon_conversion(in_raster= raster_temp, out_polygon_features= raster_temp + "_Raster2poly" + sensor, simplify="NO_SIMPLIFY", raster_field="Value", create_multipart_features="SINGLE_OUTER_PART", max_vertices_per_feature="")
        funtions_aux.savelog ("-> Dissolve...", 0)
        arcpy.Dissolve_management(raster_temp + "_Raster2poly" + sensor, raster_temp + "_Raster2poly" + sensor + "_Dissolve"+ "_" + str(parts), multi_part = "MULTI_PART")

        arcpy.AddField_management(raster_temp + "_Raster2poly" + sensor + "_Dissolve" + "_" + str(parts), field_name="File", field_type="TEXT", field_precision="", field_scale="", field_length="", field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
        calculateFieldExpression  = "'"+filename+"'"
        arcpy.CalculateField_management(raster_temp + "_Raster2poly" + sensor + "_Dissolve"+ "_" + str(parts), field="File", expression=calculateFieldExpression  , expression_type="PYTHON3", code_block="")

        list_shapes.append(os.path.join(raster_temp + "_Raster2poly" + sensor + "_Dissolve" + "_" + str(parts)))
        list_delete.append(os.path.join(raster_temp + "_Raster2poly" + sensor + "_Dissolve" + "_" + str(parts)))
        list_delete.append(raster_temp)
        list_delete.append(raster_temp + "_Raster2poly" + sensor)

        parts+=1

    if len (filename_list_filter) > 0:
        #mosaic_name = filename_list_filter[0].split("\\")[-5] + "_" + filename_list_filter[0].split("\\")[-4]
        mosaic_name_aux1 = filename_list_filter[0].split("\\")[-1]
        mosaic_name_aux = '_'.join(mosaic_name_aux1.split("_")[:-3]) #-2
        mosaic_name = mosaic_name_aux.split("_")[-6] + "_" + mosaic_name_aux.split("_")[-5] + "_" + mosaic_name_aux.split("_")[-4]
        arcpy.Merge_management(list_shapes, input_date.CLASSIFY_GDB + "\\" + mosaic_name + "_Masc")
        funtions_aux.savelog (u"Apagando arquivos temporários...", 1)
        if input_date.delete_temp:
            for rastername_delete in list_delete: #Clear
                if arcpy.Exists(rastername_delete):
                    arcpy.Delete_management(rastername_delete)

        build_rasters(filename_list_filter, sensor)

#---------------------------------------------------------------


