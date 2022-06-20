# -*- coding: utf-8 -*-

import arcpy
import os

uhes = {
    "Água Vermelha"    : "AGV",
    "Caconde"          : "CAC",
    "Barra Bonita"     : "BAB",
    "Bariri"           : "BAR",
    "Ibitinga"         : "IBI",
    "Nova Avanhandava" : "NAV",
    "Promissão"        : "PRO",
    "Limoeiro"         : "LMO",
    "Mogi Guaçu"       : "MOG",
    "Euclides da Cunha": "EUC",
    "Todas"            : "*"
}


def get_classification_fatures(input_folder, uhe, filter_year_q):
    try:
        arcpy.AddMessage("Iniciando a seleção de Feature Classes de classificação")
        old_workspace = arcpy.env.workspace

        classific_features = []
        gdb = "{0}\\{1}\\{1}_classificacao.gdb".format(input_folder, uhe)
        arcpy.env.workspace = gdb
        for fc in arcpy.ListFeatureClasses():
            if filter_year_q == "*":
                classific_features.append("{0}\\{1}".format(gdb, fc))
            elif filter_year_q in fc:
                classific_features.append("{0}\\{1}".format(gdb, fc))

        arcpy.env.workspace = old_workspace

        arcpy.AddMessage("Fim da seleção de Feature Classes de classificação")

        return classific_features
    except Exception as e:
        arcpy.AddError("Não foi possível listar as Feature Classes de classificação")
        arcpy.AddError(e)
        return []

def get_imageamento_date(feature_source):
    date_imageamento = [row[0] for row in arcpy.da.SearchCursor(feature_source, "Date")][0]
    if len(date_imageamento) > 10:
        imageamento = "{0} a {1}".format(date_imageamento[:10].replace('_', '/'), date_imageamento[11:].replace('_', '/'))
    else:
        imageamento = date_imageamento[:10].replace('_', '/')
    return imageamento


def generate_map_layout(aprx, uhe, resolution, feature_source, water_mirrors, output_folder):
    try:
        arcpy.AddMessage("Iniciando as configuraçãos para exportação do Layout de mapa geral")
        for m in aprx.listMaps(uhe):
            print("Map: " + m.name)

            # Classificacao
            lyr = m.listLayers("*_Q*")[0]
            properties = lyr.connectionProperties
            properties['connection_info']['database'] = os.path.dirname(feature_source)
            properties['dataset'] = os.path.basename(feature_source)
            lyr.updateConnectionProperties(lyr.connectionProperties, properties)

            true_name = lyr.dataSource[-7:]
            lyr.name = true_name

            imageamento = get_imageamento_date(feature_source)

            # Espelhos dagua Reservatorios
            lyr_masc = m.listLayers("*_MASC_MAX")[0]

            feature_dataset = os.path.dirname(water_mirrors[uhe])
            gdb = os.path.dirname(feature_dataset)
            fc = os.path.basename(water_mirrors[uhe])

            properties = lyr_masc.connectionProperties
            
            properties['connection_info']['database'] = gdb
            properties['dataset'] = fc
            lyr_masc.updateConnectionProperties(lyr_masc.connectionProperties, properties)

        arcpy.AddMessage("Fim das configuraçãos para exportação do Layout de mapa geral")
 
        arcpy.AddMessage("Iniciando a exportação do Layout de mapa geral para JPEG")

        elm_period = "FC_corrente"
        txt_imageamento = "Text_Imageamento"
        for lyt in aprx.listLayouts(uhe + "_L"):
            for elm in lyt.listElements("TEXT_ELEMENT"):
                if elm.name == elm_period:
                    elm.text = true_name       
                if elm.name == txt_imageamento:
                    elm.text = "Imageamento: " + imageamento

        lyt.exportToJPEG("{0}\\{1}".format(output_folder, uhe + "_" + true_name + "_Mp_Geral.jpg"), resolution)

        arcpy.AddMessage("Exportado para: {0}\\{1}".format(output_folder, uhe + "_" + true_name + "_Mp_Geral.jpg"))

        arcpy.AddMessage("Fim da exportação do Layout de mapa geral para JPEG")

    except Exception as e:
        arcpy.AddError("Não foi possível exportar os Layouts de mapa geral para JPEG")
        arcpy.AddError(e)

def export_macrofita_layout(aprx, uhe, resolution, feature_source, water_mirrors, outline_width_emersa, outline_width_flutuante, output_folder):
    try:
        arcpy.AddMessage("Iniciando as configuraçãos para exportação do Layout de macrofita")
        for m in aprx.listMaps(uhe):
            print("Map: " + m.name)

            # Classificacao
            lyr = m.listLayers("*_Q*")[0]
            properties = lyr.connectionProperties
            properties['connection_info']['database'] = os.path.dirname(feature_source)
            properties['dataset'] = os.path.basename(feature_source)
            lyr.updateConnectionProperties(lyr.connectionProperties, properties)

            true_name = lyr.dataSource[-7:]
            lyr.name = true_name

            imageamento = get_imageamento_date(feature_source)

            sym = lyr.symbology
            sym.updateRenderer('UniqueValueRenderer')
            for grp in sym.renderer.groups:
                grp.items[0].symbol.size = outline_width_emersa
                grp.items[1].symbol.size = outline_width_flutuante

            lyr.symbology = sym

            # Espelhos dagua Reservatorios
            lyr_masc = m.listLayers("*_MASC_MAX")[0]

            feature_dataset = os.path.dirname(water_mirrors[uhe])
            gdb = os.path.dirname(feature_dataset)
            fc = os.path.basename(water_mirrors[uhe])

            properties = lyr_masc.connectionProperties  
            properties['connection_info']['database'] = gdb
            properties['dataset'] = fc
            lyr_masc.updateConnectionProperties(lyr_masc.connectionProperties, properties)

        arcpy.AddMessage("Fim das configuraçãos para exportação do Layout de macrofita")

        arcpy.AddMessage("Iniciando a exportação do Layout de macrofita para JPEG")

        elm_period = "FC_corrente"
        txt_imageamento = "Text_Imageamento"
        for lyt in aprx.listLayouts(uhe + "_L"):
            for elm in lyt.listElements("TEXT_ELEMENT"):
                if elm.name == elm_period:
                    elm.text = true_name       
                if elm.name == txt_imageamento:
                    elm.text = "Imageamento: " + imageamento

        lyt.exportToJPEG("{0}\\{1}".format(output_folder, uhe + "_" + true_name + "_Macrofita.jpg"), resolution)

        arcpy.AddMessage("Exportado para: {0}\\{1}".format(output_folder, uhe + "_" + true_name + "_Macrofita.jpg"))

        arcpy.AddMessage("Fim da exportação do Layout de macrofita para JPEG")

    except Exception as e:
        arcpy.AddError("Não foi possível exportar os Layouts de macrofita para JPEG")
        arcpy.AddError(e)


if __name__ == '__main__':
    script_folder = os.path.dirname(os.path.realpath(__file__))

    input_folder = arcpy.GetParameterAsText(0)
    
    general_map_layout = arcpy.GetParameter(1) #True or False
    macrofita_layout = arcpy.GetParameter(2) #True or False

    uhe_name = arcpy.GetParameterAsText(3)

    uhe_list = [uhes[uhe_name]] if uhes[uhe_name] != "*" else ["EUC", "LMO", "AGV", "CAC", "BAB", "BAR", "IBI", "NAV", "PRO", "MOG"]

    filter_year_q = arcpy.GetParameterAsText(4).upper()

    resolution = int(arcpy.GetParameterAsText(5))

    outline_width_emersa = int(arcpy.GetParameterAsText(6))
    outline_width_flutuante = int(arcpy.GetParameterAsText(7))

    output_folder = arcpy.GetParameterAsText(8)

    layout_folder = '{0}\\Templates'.format(script_folder)

    water_mirrors = {
        "EUC": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM23\\EUC_MASC_MAX".format(script_folder),
        "LMO": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM23\\LMO_MASC_MAX".format(script_folder),
        "MOG": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM23\\MOG_MASC_MAX".format(script_folder),
        "CAC": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM23\\CAC_MASC_MAX".format(script_folder),
        "AGV": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM22\\AGV_MASC_MAX".format(script_folder),
        "BAB": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM22\\BAB_MASC_MAX".format(script_folder),
        "IBI": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM22\\IBI_MASC_MAX".format(script_folder),
        "NAV": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM22\\NAV_MASC_MAX".format(script_folder),
        "PRO": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM22\\PRO_MASC_MAX".format(script_folder),
        "BAR": "{0}\\Aes_dados_apoio.gdb\\EspelhoDagua_Reservatorios_UTM22\\BAR_MASC_MAX".format(script_folder)
    }

    if general_map_layout:
        for uhe in uhe_list:
            

            classific_features = get_classification_fatures(input_folder, uhe, filter_year_q)

            if classific_features == []:
                arcpy.AddError("Não foi possível exportar o layout de mapa geral")
                arcpy.AddError("Não foi encontrado dados para UHE: {0} e Período: {1}".format(uhe, filter_year_q))
                continue

            for feature in classific_features:
                aprx = arcpy.mp.ArcGISProject("{0}\\Layout_Mapa_Geral_{1}.aprx".format(layout_folder, uhe))
                generate_map_layout(aprx, uhe, resolution, feature, water_mirrors, output_folder)

    if macrofita_layout:
        for uhe in uhe_list:
            

            classific_features = get_classification_fatures(input_folder, uhe, filter_year_q)

            if classific_features == []:
                arcpy.AddError("Não foi possível exportar o layout de macrofita")
                arcpy.AddError("Não foi encontrado dados para UHE: {0} e Período: {1}".format(uhe, filter_year_q))
                continue
            
            for feature in classific_features:
                aprx = arcpy.mp.ArcGISProject("{0}\\Layout_Macrofita.aprx".format(layout_folder))
                export_macrofita_layout(aprx, uhe, resolution, feature, water_mirrors, outline_width_emersa, outline_width_flutuante, output_folder)

