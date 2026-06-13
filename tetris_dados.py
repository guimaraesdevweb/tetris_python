

import random
import os
import time
import sys
import select
import tty
import termios

def criar_tabuleiro():
    linhas = 20
    colunas = 10
    
    tabuleiro = [[0 for _ in range(colunas)] for _ in range(linhas)]
    return tabuleiro

# Testando a criação de tabuleiros

tabuleiro_teste = criar_tabuleiro()
print(f"Total de linhas: {len(tabuleiro_teste)}")
print(f"Total de colunas na linha 0: {len(tabuleiro_teste[0])}")

#Criando um dicionário contendo as formas

PEÇAS = {
    'I':[
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
        
    ],
    'O':[
        [1,1],
        [1,1]
    ],
    'T':[
        [0,1,0],
        [1,1,1],
        [0,0,0]
        
    ],
    'S': [
        [0,1,1],
        [1,1,0],
        [0,0,0]
    ],
    'Z': [
        [1,1,0],
        [0,1,1],
        [0,0,0]
    ],
    'J':[
        [1,0,0],
        [1,1,1],
        [0,0,0]
        
    ],
    'L':[
        [0,0,1],
        [1,1,1],
        [0,0,0]
        
    ]
}

def rotacionar_peca(peca):
    return [list(linha)[::-1] for linha in zip(*peca) ]



def checar_colisao(tabuleiro, peca, linha_global, coluna_global):
    '''
    Retorna True se houver colisão entre a peça e o tabuleiro, caso contrário, retorna False.
    '''
    for l_local, linha_peca in enumerate(peca):
        for c_local, bloco in enumerate(linha_peca):
            # Só nos importamos com os blocos reais da peça (valor 1)
            if bloco != 0:
                l_tab = linha_global + l_local
                c_tab = coluna_global + c_local

                # Verificar se a posição está fora dos limites do tabuleiro
                if c_tab <0 or c_tab >= 10 or l_tab>=20:
                    return True
                
                if l_tab < 0:
                    return True
                # Ignorar blocos acima do tabuleiro (permitido durante a queda)

                # Verificar se há um bloco existente no tabuleiro
                if tabuleiro[l_tab][c_tab] != 0:
                    return True
    return False

def fixar_pecas(tabuleiro, peca, linha_global, coluna_global):
    '''
    Transforma os blocos de peças ativas em blocos fixos no tabuleiro.
'''
    for l_local, linha_peca in enumerate(peca):
        for c_local, bloco in enumerate(linha_peca):
            if bloco != 0:
                l_tab = linha_global + l_local
                c_tab = coluna_global + c_local
                if 0 <= l_tab < 20 and 0 <= c_tab < 10:
                    tabuleiro[l_tab][c_tab] = 1
    
def limpar_linhas(tabuleiro):
    '''
    Remove as linhaas completas do tabuleiro e adiciona linhas vazias
    Retorna o número de linhas que foram limpas (útil a pontuação) 
    '''
    linhas_limpas = 0
    linhas_novas = []
    
    for linha in tabuleiro:
        # Senão houver o número 0 na linha, ela está completa
        if 0 not in linha:
            linhas_limpas +=1
        else:
            #Se não estiver cheia, mantemos a linha da nossa lista temporária
            linhas_novas.append(linha)
    # Se limpamos linhas, precisamos adicionar novas linhas vazias no topo do tabuleiro
    for _ in range(linhas_limpas):
        linha_vazia = [0 for _ in range(10)]
        linhas_novas.insert(0, linha_vazia)  # Insere no topo (índice 0)
    
    # Atualizamos o tabuleiro com as novas linhas
    # Usamos o fatiamento [:] para modificar a lista original em vez de criar uma nova
    tabuleiro[:] = linhas_novas
    
    #tabuleiro[:] = [list(l) for l in linhas_novas] if 'rows_novas' in locals() else [list(l) for l in linhas_novas]  # Garantindo que cada linha seja uma nova lista (cópia)
    
    
    return linhas_limpas


def desenhar_tabuleiro_teste(tabuleiro, mensagem):
    # Limpa o terminal para dar efeito de animação
    os.system('clear')
    print(f"=== {mensagem} ===")
    print("-" * 22)
    for linha in tabuleiro:
        # Para ficar mais bonito visualmente no terminal:
        # Se for 0, desenha um ponto '.', se for 1, desenha '[]'
        linha_visual = "".join(["[]" if bloco == 1 else " ." for bloco in linha])
        print(f"|{linha_visual}|")
    print("-" * 22)
    print("\n")


def pegar_tecla():
    """
    Função atualizada para capturar Letras, Espaço e as Setas no Linux.
    Retorna strings amigáveis como 'esquerda', 'direita', 'girar', 'descer' ou 'sair'.
    """
    fd = sys.stdin.fileno()
    config_antiga = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        # Checa se há alguma tecla no buffer por até 0.1 segundos
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            tecla = sys.stdin.read(1)
            
            # Se for o caractere de escape, indica que uma seta foi pressionada
            if tecla == '\x1b':
                # Lê os próximos dois caracteres da sequência (ex: '[A')
                sequencia = sys.stdin.read(2)
                if sequencia == '[D': return 'esquerda'
                if sequencia == '[C': return 'direita'
                if sequencia == '[B': return 'descer'
                if sequencia == '[A': return 'girar' # Seta para cima também pode girar
            
            # Mapeamento das teclas normais
            if tecla == ' ': return 'girar'       # Barra de espaço
            if tecla == 'q' or tecla == 'Q': return 'sair'
            
            # Mantendo suporte opcional para quem prefere letras
            if tecla == 'a': return 'esquerda'
            if tecla == 'd': return 'direita'
            if tecla == 's': return 'descer'
            
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, config_antiga)
        
def jogar_tetris():
    tabuleiro = criar_tabuleiro()
    lista_pecas = list(PEÇAS.keys())
    
    # Estado inicial do jogo
    peca_atual_nome = random.choice(lista_pecas)
    peca_atual = PEÇAS[peca_atual_nome]
    
    proxima_peca_nome = random.choice(lista_pecas)
    proxima_peca = PEÇAS[proxima_peca_nome]
    
    # Posição inicial (topo central)
    linha_atual = 0
    coluna_atual = 3
    
    pontuacao = 0
    jogo_rodando = True
    ultima_queda = time.time()
    velocidade_queda = 0.6 

    # Limpa a tela uma única vez antes de começar o jogo de fato
    os.system('clear')

    while jogo_rodando:
        # 1. RENDERIZAÇÃO OTIMIZADA (SEM PISCAR)
        tabuleiro_exibicao = [linha[:] for linha in tabuleiro]
        fixar_pecas(tabuleiro_exibicao, peca_atual, linha_atual, coluna_atual)
        
        # \033[H joga o cursor para o topo do terminal sem apagar nada
        tela_buffer = "\033[H"
        
        # Cabeçalho com espaço para a peça não nascer esmagada
        tela_buffer += "=== TETRIS TERMINAL ===\n"
        tela_buffer += " +--------------------+\n" # Topo da moldura (20 hífens)
        
        for i, linha in enumerate(tabuleiro_exibicao):
            # Monta os blocos da linha do tabuleiro
            linha_visual = "".join(["[]" if bloco == 1 else " ." for bloco in linha])
            print_linha = f" |{linha_visual}|"
            
            # --- PAINEL LATERAL ---
            if i == 1:
                print_linha += f"   PONTUAÇÃO: {pontuacao}"
            elif i == 3:
                print_linha += f"   PRÓXIMA PEÇA: ({proxima_peca_nome})"
            elif 4 <= i < 4 + len(proxima_peca):
                linha_prox = proxima_peca[i - 4]
                
                
                topo_peca_visual = "".join(["[]" if b == 1 else "  " for b in linha_prox])
                espacos_faltando = 4 - len(linha_prox)
                
                topo_peca_visual += "  " * espacos_faltando
                
                print_linha += f"   {topo_peca_visual}"
                
                # topo_peca_visual = "".join(["[]" if b == 1 else "  " for b in linha_prox])
                
                # print_linha += f"   {topo_peca_visual}"
                
            tela_buffer += print_linha + "\n"
            
        # Fundo da moldura
        tela_buffer += " +--------------------+\n"
        tela_buffer += " Controles: Setas (Mover) | Espaço (Girar) | Q (Sair)\n"
        
        # Envia toda a interface acumulada para o terminal de uma vez só
        sys.stdout.write(tela_buffer)
        sys.stdout.flush()

        # 2. CAPTURA DE ENTRADA (INPUT)
        comando = pegar_tecla()
        if comando == 'sair':
            jogo_rodando = False
            break
        elif comando == 'esquerda':
            if not checar_colisao(tabuleiro, peca_atual, linha_atual, coluna_atual - 1):
                coluna_atual -= 1
        elif comando == 'direita':
            if not checar_colisao(tabuleiro, peca_atual, linha_atual, coluna_atual + 1):
                coluna_atual += 1
        elif comando == 'girar':
            peca_rotacionada = rotacionar_peca(peca_atual)
            if not checar_colisao(tabuleiro, peca_rotacionada, linha_atual, coluna_atual):
                peca_atual = peca_rotacionada
        elif comando == 'descer':
            if not checar_colisao(tabuleiro, peca_atual, linha_atual + 1, coluna_atual):
                linha_atual += 1

        # 3. ATUALIZAÇÃO DA GRAVIDADE (UPDATE)
        agora = time.time()
        if agora - ultima_queda > velocidade_queda:
            if not checar_colisao(tabuleiro, peca_atual, linha_atual + 1, coluna_atual):
                linha_atual += 1
            else:
                fixar_pecas(tabuleiro, peca_atual, linha_atual, coluna_atual)
                
                linhas_limpas = limpar_linhas(tabuleiro)
                pontuacao += linhas_limpas * 100
                
                peca_atual_nome = proxima_peca_nome
                peca_atual = PEÇAS[peca_atual_nome]
                
                proxima_peca_nome = random.choice(lista_pecas)
                proxima_peca = PEÇAS[proxima_peca_nome]
                
                linha_atual = 0
                coluna_atual = 3
                
                if checar_colisao(tabuleiro, peca_atual, linha_atual, coluna_atual):
                    # Força uma última impressão para mostrar o tabuleiro lotado no Game Over
                    os.system('clear')
                    print("=== GAME OVER ===")
                    print(f"Pontuação Final: {pontuacao}")
                    jogo_rodando = False
            
            ultima_queda = agora   
        
        
'''
def jogar_tetris():
    tabuleiro = criar_tabuleiro()
    lista_pecas = list(PEÇAS.keys())
    
    # Estado inicial do jogo
    peca_atual_nome = random.choice(lista_pecas)
    peca_atual = PEÇAS[peca_atual_nome]
    
    proxima_peca_nome = random.choice(lista_pecas)
    proxima_peca = PEÇAS[proxima_peca_nome]
    
    
    # Posição inicial (topo central)
    linha_atual = 0
    coluna_atual = 3
    
    pontuacao = 0
    jogo_rodando = True
    ultima_queda = time.time()
    velocidade_queda = 0.6 # A peça cai a cada 0.6 segundos

    print("Controles: Setas (Mover) | Espaço (Girar) | Q (Sair)")
    time.sleep(2)

    while jogo_rodando:
        # 1. RENDERIZAÇÃO: Desenha o estado atual
        # Para desenhar a peça EM MOVIMENTO sem alterar o tabuleiro definitivo,
        # criamos uma cópia temporária do tabuleiro para exibição
        tabuleiro_exibicao = [linha[:] for linha in tabuleiro]
        fixar_pecas(tabuleiro_exibicao, peca_atual, linha_atual, coluna_atual)
        
        # Desenha na tela (usando a mesma lógica que testamos antes)
        import os
        os.system('clear')
        
        # Topo da moldura (exatamente 22 caracteres para cobrir o grid)
        print(" ____________________ ") 
        
        for i, linha in enumerate(tabuleiro_exibicao):
            # CORREÇÃO: Usamos APENAS a linha real do tabuleiro
            linha_visual = "".join(["[]" if bloco == 1 else " ." for bloco in linha])
            print_linha = f"|{linha_visual}|"
            
            # --- PAINEL LATERAL ---
            if i == 1:
                print_linha += f"   PONTUAÇÃO: {pontuacao}"
            elif i == 3:
                print_linha += f"   PRÓXIMA PEÇA: ({proxima_peca_nome})"
            elif 4 <= i < 4 + len(proxima_peca):
                linha_prox = proxima_peca[i - 4]
                topo_peca_visual = "".join(["[]" if b == 1 else "  " for b in linha_prox])
                print_linha += f"   {topo_peca_visual}"
                
            print(print_linha)
            
        # Fundo da moldura
        print(" ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ ")

        # 2. CAPTURA DE ENTRADA (INPUT)
        comando = pegar_tecla()
        if comando == 'sair':
            jogo_rodando = False
            break
        elif comando == 'esquerda':
            if not checar_colisao(tabuleiro, peca_atual, linha_atual, coluna_atual - 1):
                coluna_atual -= 1
        elif comando == 'direita':
            if not checar_colisao(tabuleiro, peca_atual, linha_atual, coluna_atual + 1):
                coluna_atual += 1
        elif comando == 'girar':
            peca_rotacionada = rotacionar_peca(peca_atual)
            if not checar_colisao(tabuleiro, peca_rotacionada, linha_atual, coluna_atual):
                peca_atual = peca_rotacionada
        elif comando == 'descer':
            if not checar_colisao(tabuleiro, peca_atual, linha_atual + 1, coluna_atual):
                linha_atual += 1

        # 3. ATUALIZAÇÃO DA GRAVIDADE (UPDATE)
        agora = time.time()
        if agora - ultima_queda > velocidade_queda:
            if not checar_colisao(tabuleiro, peca_atual, linha_atual + 1, coluna_atual):
                linha_atual += 1
            else:
                # ATUALIZAÇÃO: Nome no plural fixado aqui também
                fixar_pecas(tabuleiro, peca_atual, linha_atual, coluna_atual)
                
                linhas_limpas = limpar_linhas(tabuleiro)
                pontuacao += linhas_limpas * 100
                
                # O ciclo de peças avança: a próxima vira a atual, e geramos uma nova próxima
                peca_atual_nome = proxima_peca_nome
                peca_atual = PEÇAS[peca_atual_nome]
                
                proxima_peca_nome = random.choice(lista_pecas)
                proxima_peca = PEÇAS[proxima_peca_nome]
                
                linha_atual = 0
                coluna_atual = 3
                
                if checar_colisao(tabuleiro, peca_atual, linha_atual, coluna_atual):
                    print("=== GAME OVER ===")
                    jogo_rodando = False
            
            ultima_queda = agora
'''
if __name__ == "__main__":
    jogar_tetris()



