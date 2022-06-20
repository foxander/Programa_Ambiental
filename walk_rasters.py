import arcpy
import os
import input_date
import rapideye_planet_module
import landsat_sentinel_module
import sentinel_module
import glob
import enveloped
import funtions_aux

# --------------------------------------------
# Busca as Imagens no diretório Landasat, Sentinel, RapidEyes and Planet

def walk_rasters():
    walk = arcpy.da.Walk(input_date.workspace, datatype="RasterDataset",type=['TIF', 'JP2'])
    rasters = []
    dir_control =[]
    ima_landasat_ = False
    for dirpath, dirnames, filenames in walk:
        rasters.clear()
        list_dir = []
        if "Landsat" in dirpath:
            for filename in filenames:
                if 'LT05' in filename or 'LE07' in filename: #Para imagens LandSat 5 e 7 (8 Bits)
                    if 'B1' in filename or 'B2' in filename or 'B3' in filename or 'B4' in filename:
                        rasters.append(os.path.join(dirpath, filename))
                    else: continue

                    if len(rasters) == 4:
                        subfolders = dirpath.split("\\")
                        rastername = subfolders[-5] + '_' + subfolders[-4] + "_" + subfolders[-2] + "_" + subfolders[-1]

                        if arcpy.Exists(rastername): continue  #Já existe
                        else: landsat_sentinel_module.ajust_images(rasters, rastername, "_LANDSAT")
                        ima_landasat_ = True
                        break

                if 'LC08' in filename or 'LO08' in filename: #Para LandSat 8 (16 Bits)
                    if 'B2' in filename or 'B3' in filename or 'B4' in filename or 'B5' in filename:
                        rasters.append(os.path.join(dirpath, filename))
                    else: continue

                    if len(rasters) == 4:
                        subfolders = dirpath.split("\\")
                        rastername = subfolders[-5] + '_' + subfolders[-4] + "_" + subfolders[-2] + "_" + subfolders[-1]

                        if arcpy.Exists(rastername): continue  #Já existe
                        else: landsat_sentinel_module.ajust_images(rasters, rastername, "_LANDSAT")
                        ima_landasat_ = True
                        break

        elif "Sentinel" in dirpath:
            if filenames:
                dirp1 = dirpath.split('\\')[0:-1]
                dirp = "\\".join(dirp1)
                if dirp in dir_control:
                    continue
                dir_control.append(dirp)
                for i in glob.glob(dirp + "\\*"):
                    list_dir.append(i)
                sentinel_module.ajust_images(dirpath, filenames, list_dir, "_SENTINEL" )

        else: continue

    if ima_landasat_: #Só faz se tiver imagens Landasat
        funtions_aux.savelog("Processando Imagens de fundo...", 1)
        enveloped.image_recorte()
        funtions_aux.savelog("Finalizada", 1)
        funtions_aux.savelog('\n', 1)
