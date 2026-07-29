# Perguntas Frequentes (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

[Voltar ao Inicio](Home_pt)

Respostas a perguntas comuns sobre o pyGM.

## Perguntas gerais

### O que é o pyGM?
O pyGM é um editor visual de desenvolvimento de jogos para Python. Permite criar jogos 2D sem conhecimentos extensos de programação.

### O pyGM é gratuito?
Sim, o pyGM é de código aberto e completamente gratuito.

### Que linguagem de programação é usada?
O pyGM é baseado em Python. Pode usar programação visual ou escrever código Python diretamente.

### Para que plataformas posso desenvolver?
- Windows
- macOS
- Linux
- Web (HTML5)
- Móvel (Kivy/Android)

## Instalação

### Como instalo o pyGM?
```bash
pip install pygm
```

### Que versão de Python preciso?
Python 3.10 ou superior.

### O pyGM não inicia. O que faco?
1. Verifique a versão de Python
2. Reinstale as dependencias
3. Inicie a partir da linha de comandos para ver erros

## Desenvolvimento

### Como crio um novo projeto?
Inicie o pyGM é selecione "Novo Projeto" ou use Ficheiro > Novo.

### Como adiciono sprites?
1. Clique direito em "Sprites" na arvore de recursos
2. Selecione "Novo Sprite"
3. Importe uma imagem ou crie uma

### Como crio animações?
1. Abra um sprite
2. Adicione vários frames
3. Configure a velocidade da animação

### Como programo o comportamento dos objetos?
1. Abra um objeto
2. Adicione eventos (ex. Create, Step)
3. Adicione ações aos eventos
4. Ou use o editor visual Blockly

## Recursos

### Que formatos de imagem são suportados?
- PNG (recomendado)
- JPG
- GIF
- BMP

### Que formatos de áudio são suportados?
- WAV
- MP3
- OGG

### Como otimizo os meus recursos?
- Use tamanhos de imagem apropriados
- Comprima ficheiros de áudio
- Remova recursos não utilizados

## Gameplay

### Como implemento a deteção de colisões?
1. Crie um evento de colisão no objeto
2. Selecione o outro objeto
3. Adicione ações para a reação

### Como crio multiplos níveis?
1. Crie várias salas
2. Use a acao "Ir para sala"
3. Ou "Ir para a proxima sala"

### Como guardo o progresso do jogo?
Use as funções de gravação integradas:
- `save_game()`: Guardar jogo
- `load_game()`: Carregar jogo

## Exportação

### Como exporto o meu jogo?
1. Vá a Ficheiro → Exportar projeto…
2. Selecione a plataforma de destino
3. Configure as opções
4. Clique em "Exportar"

### Porque e que o ficheiro exportado e tao grande?
- Inclui o runtime de Python
- Todos os recursos incorporados
- Dica: Otimize os recursos

### Posso exportar para dispositivos móveis?
Sim, através da exportação Kivy/Android. A exportação web também funciona em navegadores móveis.

## Resolução de problemas

### O meu jogo esta lento
- Reduza o código nos eventos Step
- Otimize os tamanhos dos sprites
- Evite demasiadas instâncias

### Os sprites não são apresentados
- Verifique o caminho do sprite
- Certifique-se de que Visivel=true
- Verifique a ordem de desenho (profundidade)

### As colisões não funcionam
- Verifique as mascaras de colisão
- Certifique-se de que os objetos são sólidos (se necessario)
- Verifique a configuração dos eventos

## Comunidade

### Onde encontro ajuda?
- Documentação oficial
- GitHub Issues
- Foruns da comunidade

### Como posso contribuir?
- Reporte bugs no GitHub
- Envie Pull Requests
- Melhore a documentação

## Ver também

- [Começar](Comecar_pt)
- [Criar o seu primeiro jogo](Primeiro_Jogo_pt)
- [Eventos e Ações](Eventos_e_Acoes_pt)
