# Perguntas Frequentes (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Voltar ao Inicio](Home_pt)

Respostas a perguntas comuns sobre o pyGM.

## Perguntas gerais

### O que e o pyGM?
O pyGM e um editor visual de desenvolvimento de jogos para Python. Permite criar jogos 2D sem conhecimentos extensos de programacao.

### O pyGM e gratuito?
Sim, o pyGM e de codigo aberto e completamente gratuito.

### Que linguagem de programacao e usada?
O pyGM e baseado em Python. Pode usar programacao visual ou escrever codigo Python diretamente.

### Para que plataformas posso desenvolver?
- Windows
- macOS
- Linux
- Web (HTML5)

## Instalacao

### Como instalo o pyGM?
```bash
pip install pygm
```

### Que versao de Python preciso?
Python 3.8 ou superior.

### O pyGM nao inicia. O que faco?
1. Verifique a versao de Python
2. Reinstale as dependencias
3. Inicie a partir da linha de comandos para ver erros

## Desenvolvimento

### Como crio um novo projeto?
Inicie o pyGM e selecione "Novo Projeto" ou use Ficheiro > Novo.

### Como adiciono sprites?
1. Clique direito em "Sprites" na arvore de recursos
2. Selecione "Novo Sprite"
3. Importe uma imagem ou crie uma

### Como crio animacoes?
1. Abra um sprite
2. Adicione varios frames
3. Configure a velocidade da animacao

### Como programo o comportamento dos objetos?
1. Abra um objeto
2. Adicione eventos (ex. Create, Step)
3. Adicione acoes aos eventos
4. Ou use o editor visual Blockly

## Recursos

### Que formatos de imagem sao suportados?
- PNG (recomendado)
- JPG
- GIF
- BMP

### Que formatos de audio sao suportados?
- WAV
- MP3
- OGG

### Como otimizo os meus recursos?
- Use tamanhos de imagem apropriados
- Comprima ficheiros de audio
- Remova recursos nao utilizados

## Gameplay

### Como implemento a detecao de colisoes?
1. Crie um evento de colisao no objeto
2. Selecione o outro objeto
3. Adicione acoes para a reacao

### Como crio multiplos niveis?
1. Crie varias salas
2. Use a acao "Ir para sala"
3. Ou "Ir para a proxima sala"

### Como guardo o progresso do jogo?
Use as funcoes de gravacao integradas:
- `save_game()`: Guardar jogo
- `load_game()`: Carregar jogo

## Exportacao

### Como exporto o meu jogo?
1. Va a Ficheiro > Exportar
2. Selecione a plataforma de destino
3. Configure as opcoes
4. Clique em "Exportar"

### Porque e que o ficheiro exportado e tao grande?
- Inclui o runtime de Python
- Todos os recursos incorporados
- Dica: Otimize os recursos

### Posso exportar para dispositivos moveis?
Atualmente nao e suportado diretamente. A exportacao web funciona em navegadores moveis.

## Resolucao de problemas

### O meu jogo esta lento
- Reduza o codigo nos eventos Step
- Otimize os tamanhos dos sprites
- Evite demasiadas instancias

### Os sprites nao sao apresentados
- Verifique o caminho do sprite
- Certifique-se de que Visivel=true
- Verifique a ordem de desenho (profundidade)

### As colisoes nao funcionam
- Verifique as mascaras de colisao
- Certifique-se de que os objetos sao solidos (se necessario)
- Verifique a configuracao dos eventos

## Comunidade

### Onde encontro ajuda?
- Documentacao oficial
- GitHub Issues
- Foruns da comunidade

### Como posso contribuir?
- Reporte bugs no GitHub
- Envie Pull Requests
- Melhore a documentacao

## Ver tambem

- [Comecar](Comecar_pt)
- [Criar o seu primeiro jogo](Primeiro_Jogo_pt)
- [Eventos e Acoes](Eventos_e_Acoes_pt)
