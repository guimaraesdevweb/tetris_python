# Tetris Terminal 🕹️

Um clone do clássico Tetris desenvolvido em Python para rodar diretamente no terminal Linux (Ubuntu). Este projeto foi construído do zero adotando uma **Abordagem Orientada a Dados**, com o objetivo de estudar arquitetura de software, gerenciamento de estados e detecção de colisões matemáticas em jogos.

---

## 🧠 Sobre a Arquitetura (Por trás dos panos)

Diferente da maioria das abordagens que misturam a parte visual com as regras do jogo, este projeto foi estruturado separando estritamente a **Lógica de Dados** da **Camada de Visualização**:

* **Engine Pura de Dados:** O tabuleiro e as peças (tetraminós) são gerenciados puramente como matrizes e listas na memória. Toda a física do jogo — como a rotação de 90° no sentido horário e a gravidade — funciona através de álgebra linear e manipulação de índices de matrizes.
* **Detecção de Colisão Matemática:** Antes de qualquer bloco se mover na tela, o sistema faz uma varredura preditiva cruzando as coordenadas locais da peça com o estado atual do tabuleiro global para validar o movimento.
* **Renderização Anti-Flicker:** Para evitar o incômodo efeito de "piscado" comum em jogos de terminal, o projeto utiliza códigos de escape ANSI (`\033[H`). Em vez de apagar a tela a cada frame, o cursor volta ao topo e sobrescreve o buffer em uma única string compacta, garantindo uma taxa de quadros extremamente fluida.

---

## 🛠️ Tecnologias e Recursos Utilizados

* **Linguagem:** Python 3
* **Interface:** Modo texto (Terminal ASCII / Unicode)
* **Módulos Nativos:** * `os` e `sys` (controle do sistema e fluxo de saída)
    * `time` (gerenciamento do tempo da gravidade)
    * `random` (sorteio pseudo-aleatório das peças)
    * `select`, `tty`, `termios` (captura de teclado assíncrona e não-bloqueante no Linux)

---

## 🎮 Funcionalidades Completas

- [x] Matriz de tabuleiro clássica ($20 \times 10$).
- [x] Todos os 7 tetraminós clássicos (I, O, T, S, Z, J, L).
- [x] Sistema de rotação horária precisa.
- [x] Painel lateral dinâmico exibindo a próxima peça com largura fixa (alinhamento simétrico).
- [x] Marcador de pontuação em tempo real.
- [x] Algoritmo de varredura e eliminação de linhas cheias com descida de blocos.
- [x] Tela de Game Over com validação de colisão no topo.

---

## 🕹️ Controles do Jogo

O jogo foi otimizado para uma jogabilidade ergonômica utilizando as setas do teclado (ou o teclado numérico com o Num Lock desativado) e a barra de espaço:

* **Seta para Esquerda:** Move a peça para a esquerda.
* **Seta para Direita:** Move a peça para a direita.
* **Seta para Baixo:** Força a descida rápida da peça (Soft Drop).
* **Barra de Espaço / Seta para Cima:** Rotaciona a peça em 90°.
* **Tecla Q:** Sai do jogo a qualquer momento de forma limpa, restaurando as configurações do terminal.

---

## 🚀 Como Executar o Projeto

Como o sistema de captura de teclado utiliza os recursos nativos do subsistema UNIX (`termios`), o jogo é totalmente compatível com distribuições Linux (como Ubuntu).

1. Clone o repositório:
   ```bash
   [git clone [(https://github.com/guimaraesdevweb/tetris_python)]](https://github.com/guimaraesdevweb/tetris_python.git)
