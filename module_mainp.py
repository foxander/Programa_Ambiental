import input_date
import funtions_aux
import classify_module
import enveloped
import statis
import walk_rasters

def mainp():
    funtions_aux.savelog(u"Pré-Processamento...", 1)

    if "Arquivos" in input_date.type_classify:
        funtions_aux.savelog("Iniciando o processo", 1)
        funtions_aux.savelog("Fase 1 - Fazendo Composite, Reprojetando e Recortando as Imagens.", 1)
        walk_rasters.walk_rasters()
        funtions_aux.savelog("Fase 1 - Finalizada", 1)
        funtions_aux.savelog('\n', 1)
    else:
        funtions_aux.savelog("Iniciando o processo", 1)
        funtions_aux.savelog("Etapa Tratamento das Imagens - Finalizada", 1)
        funtions_aux.savelog('\n', 1)

    funtions_aux.savelog("Fase 3 - Iniciando o processo de recorte dos espelhos d´água e reclassificando.", 1)
    classify_module.classify_module()
    funtions_aux.savelog("Fase 3 - Finalizada", 1)
    funtions_aux.savelog('\n', 1)

    funtions_aux.savelog("Fase 4 - Analisando os resultados e calculando as estatísticas.", 1)
    statis.analise_barragens()
    funtions_aux.savelog("Fase 4  - Finalizada", 1)
    funtions_aux.savelog('\n', 1)

    funtions_aux.free_memory()

    funtions_aux.savelog("Processo Finalizado!", 1)
