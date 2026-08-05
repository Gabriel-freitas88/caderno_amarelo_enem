"""
Propósito: Dividir as questões por padrão visual e permitir a junção
de questões detectadas separadamente por engano (ex: 23 e 24).
"""

from PIL import Image
import os

def encontrar_faixas_cinzas(imagem, cor_alvo=(189, 188, 188), tolerancia=35, altura_min=40, altura_max=90, offset_corte=45):
    largura, altura = imagem.size
    pixels = imagem.load()
    
    marcas = []
    x_pixels = [largura - 1, largura - 2, largura - 3, largura - 4, largura - 5, largura - 6]
    
    y = 0
    while y <= altura - altura_min:
        faixa_encontrada = False
        altura_detectada = 0
        
        for x in x_pixels:
            contador_altura = 0
            
            while (y + contador_altura) < altura:
                pixel = pixels[x, y + contador_altura]
                r, g, b = pixel[:3]
                
                if (abs(r - cor_alvo[0]) <= tolerancia and 
                    abs(g - cor_alvo[1]) <= tolerancia and 
                    abs(b - cor_alvo[2]) <= tolerancia):
                    contador_altura += 1
                else:
                    break
            
            if altura_min <= contador_altura <= altura_max:
                faixa_encontrada = True
                altura_detectada = contador_altura
                break
                
        if faixa_encontrada:
            y_inicio_faixa = y
            y_corte_superior = max(0, y - offset_corte)
            marcas.append((y_inicio_faixa, y_corte_superior))
            print(f"Marca detectada em y={y_inicio_faixa}")
            
            y += altura_detectada + offset_corte
        else:
            y += 1
            
    return marcas

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo=(189, 188, 188), 
                             corte_topo_extra=0, corte_base_extra=0, juntar_questoes=None):
    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado.")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    marcas = encontrar_faixas_cinzas(imagem, cor_alvo=cor_alvo, offset_corte=45)
    
    if not marcas:
        print("Nenhuma faixa cinza encontrada!")
        return
    
    # Processa as junções de marcas (ex: remover a marca entre a 23 e a 24)
    if juntar_questoes:
        indices_para_remover = set()
        for q1, q2 in juntar_questoes:
            # O índice da marca intermediária a ser removida é (q2 - 1)
            idx_remover = q2 - 1
            if 0 < idx_remover < len(marcas):
                indices_para_remover.add(idx_remover)
                print(f"--> Unindo Questão {q1} e Questão {q2} (ignoring corte intermediate).")
        
        marcas = [m for idx, m in enumerate(marcas) if idx not in indices_para_remover]

    print(f"\nTotal de arquivos finais que serão gerados: {len(marcas)}\n")
    os.makedirs(pasta_saida, exist_ok=True)
    
    for i in range(len(marcas)):
        _, y_corte_superior_atual = marcas[i]
        
        # Ajuste manual do topo
        topo = max(0, y_corte_superior_atual - corte_topo_extra)
        
        # Ajuste manual da base
        if i + 1 < len(marcas):
            base = marcas[i+1][0] + corte_base_extra
        else:
            base = altura
            
        area_corte = (0, topo, largura, base)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} (Topo: {topo} | Base: {base})")

if __name__ == "__main__":
    caminho_imagem = "pagina_enem_4.png"
    pasta_saida = "inteiras_divididas"
    cor_do_padrao = (189, 188, 188)
    
    # =======================================================================
    # 1. JUNÇÃO DE QUESTÕES (MUDANÇA AQUI)
    # Coloque os pares de números de questões que você quer UNIR numa só:
    # =======================================================================
    JUNTORES_QUESTOES = [(23, 24)]  # Junta a questão 23 e a 24 em um único arquivo!
    
    # =======================================================================
    # 2. AJUSTES MANUAIS DE CORTE:
    # =======================================================================
    CORTE_TOPO_EXTRA = -15   # Aumente (ex: 15) para subir o topo / Diminua (ex: -10) para descer
    CORTE_BASE_EXTRA = 0   # Aumente (ex: 15) para descer a base / Diminua (ex: -10) para subir
    
    dividir_imagem_por_faixas(
        caminho_imagem, 
        pasta_saida, 
        cor_do_padrao, 
        corte_topo_extra=CORTE_TOPO_EXTRA, 
        corte_base_extra=CORTE_BASE_EXTRA,
        juntar_questoes=JUNTORES_QUESTOES
    )
    print("\nDivisão concluída com sucesso!")