
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

PEÇAS = {
    'I': [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
    'O': [[1,1], [1,1]],
    'T': [[0,1,0], [1,1,1], [0,0,0]],
    'S': [[0,1,1], [1,1,0], [0,0,0]],
    'Z': [[1,1,0], [0,1,1], [0,0,0]],
    'J': [[1,0,0], [1,1,1], [0,0,0]],
    'L': [[0,0,1], [1,1,1], [0,0,0]]
}

def rotacionar_peca(peca):
    return [list(linha)[::-1] for linha in zip(*peca)]

def checar_colisao(tabuleiro, peca, linha_global, coluna_global):
    '''Retorna True se houver colisão entre a peça e o tabuleiro, senão False.'''
    for l_local, linha_peca in enumerate(peca):
        for c_local, bloco in enumerate(linha_peca):
            if bloco != 0:
                l_tab = linha_global + l_local
                c_tab = coluna_global + c_local
                
                # Verificar se a posição está fora das paredes ou do chão
                if c_tab < 0 or c_tab >= 10 or l_tab >= 20:
                    return True
                
                # Ignorar blocos acima do tabuleiro (permite rotação no nascimento)
                if l_tab < 0:
                    continue
                
                # Verificar se há um bloco existente no tabuleiro
                if tabuleiro[l_tab][c_tab] != 0:
                    return True
    return False

def fixar_pecas(tabuleiro, peca, linha_global, coluna_global):
    '''Transforma os blocos de peças ativas em blocos fixos no tabuleiro.'''
    for l_local, linha_peca in enumerate(peca):
        for c_local, bloco in enumerate(linha_peca):
            if bloco != 0:
                l_tab = linha_global + l_local
                c_tab = coluna_global + c_local
                if 0 <= l_tab < 20 and 0 <= c_tab < 10:
                    tabuleiro[l_tab][c_tab] = 1
    
def limpar_linhas(tabuleiro):
    '''Remove linhas completas, adiciona vazias no topo e retorna pontuação.'''
    linhas_limpas = 0
    linhas_novas = []
    
    for linha in tabuleiro:
        if 0 not in linha:
            linhas_limpas += 1
        else:
            linhas_novas.append(linha)
            
    for _ in range(linhas_limpas):
        linha_vazia = [0 for _ in range(10)]
        linhas_novas.insert(0, linha_vazia) 
    
    tabuleiro[:] = linhas_novas
    return linhas_limpas

def pegar_tecla():
    """Captura teclas de forma não-bloqueante no Linux."""
    fd = sys.stdin.fileno()
    config_antiga = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            tecla = sys.stdin.read(1)
            if tecla == '\x1b':
                sequencia = sys.stdin.read(2)
                if sequencia == '[D': return 'esquerda'
                if sequencia == '[C': return 'direita'
                if sequencia == '[B': return 'descer'
                if sequencia == '[A': return 'girar' 
            if tecla == ' ': return 'girar'       
            if tecla in ['q', 'Q']: return 'sair'
            if tecla == 'a': return 'esquerda'
            if tecla == 'd': return 'direita'
            if tecla == 's': return 'descer'
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, config_antiga)

def jogar_tetris():
    tabuleiro = criar_tabuleiro()
    lista_pecas = list(PEÇAS.keys())
    
    peca_atual_nome = random.choice(lista_pecas)
    peca_atual = PEÇAS[peca_atual_nome]
    
    proxima_peca_nome = random.choice(lista_pecas)
    proxima_peca = PEÇAS[proxima_peca_nome]
    
    linha_atual = 0
    coluna_atual = 3
    pontuacao = 0
    jogo_rodando = True
    ultima_queda = time.time()
    velocidade_queda = 0.5 

    # Limpa a tela uma única vez antes de entrar no loop
    os.system('clear')

    while jogo_rodando:
        # 1. RENDERIZAÇÃO
        tabuleiro_exibicao = [linha[:] for linha in tabuleiro]
        fixar_pecas(tabuleiro_exibicao, peca_atual, linha_atual, coluna_atual)
        
        # \033[2J limpa a tela inteira (evita sobreposição)
        # \033[H joga o cursor para a origem (0,0)
        tela_buffer = "\033[2J\033[H"
        
        # Usando \r\n para garantir que a linha comece no canto absoluto
        tela_buffer += "=== TETRIS TERMINAL ===\r\n"
        tela_buffer += " +--------------------+\r\n" 
        
        for i, linha in enumerate(tabuleiro_exibicao):
            linha_visual = "".join(["[]" if bloco == 1 else "  " for bloco in linha])
            print_linha = f" |{linha_visual}|"
            
            # PAINEL LATERAL
            if i == 1:
                print_linha += f"   Por: Rafael Guimarães"
            elif i == 3:
                print_linha += f"   TETRIS RAIZ NO TEMINAL"
            elif i == 4:
                print_linha += f"   Abordagem Orientada a Dados"
            elif i == 6:
                print_linha += f"  ------------+++++++------------"
                
            elif i == 9:
                print_linha += f"   PONTUAÇÃO: {pontuacao}"
            elif i == 10:
                print_linha += f"   PRÓXIMA PEÇA: ({proxima_peca_nome})"
            elif 11 <= i < 11 + len(proxima_peca):
                linha_prox = proxima_peca[i - 11]
                desenho_bruto = "".join(["[]" if b == 1 else "  " for b in linha_prox])
                # Preenchimento dinâmico estabilizado
                espacos_faltando = 4 - len(linha_prox)
                preenchimento = "  " * espacos_faltando
                
                topo_peca_visual = desenho_bruto + preenchimento
                print_linha += f"   {topo_peca_visual}"
                
            tela_buffer += print_linha + "\r\n"
            
        tela_buffer += " +--------------------+\r\n"
        tela_buffer += " Controles: Setas (Mover) | Espaço (Girar) | Q (Sair)\r\n"
        
        sys.stdout.write(tela_buffer)
        sys.stdout.flush()

        # 2. CAPTURA DE ENTRADA
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

        # 3. GRAVIDADE
        agora = time.time()
        if agora - ultima_queda > velocidade_queda:
            if not checar_colisao(tabuleiro, peca_atual, linha_atual + 1, coluna_atual):
                linha_atual += 1
            else:
                fixar_pecas(tabuleiro, peca_atual, linha_atual, coluna_atual)
                
                linhas_limpas = limpar_linhas(tabuleiro)
                pontuacao += linhas_limpas * 10
                
                peca_atual_nome = proxima_peca_nome
                peca_atual = PEÇAS[peca_atual_nome]
                
                proxima_peca_nome = random.choice(lista_pecas)
                proxima_peca = PEÇAS[proxima_peca_nome]
                
                linha_atual = 0
                coluna_atual = 3
                
                if checar_colisao(tabuleiro, peca_atual, linha_atual, coluna_atual):
                    os.system('clear')
                    print("=== GAME OVER ===")
                    print(f"Pontuação Final: {pontuacao}")
                    jogo_rodando = False
            
            ultima_queda = agora   

if __name__ == "__main__":
    jogar_tetris()



