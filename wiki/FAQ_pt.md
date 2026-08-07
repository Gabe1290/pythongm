# Perguntas Frequentes (FAQ)

> [English](FAQ) | [Français](FAQ_fr) | [Deutsch](FAQ_de) | [Italiano](FAQ_it) | [Español](FAQ_es) | [Português](FAQ_pt) | [Slovenščina](FAQ_sl) | [Українська](FAQ_uk) | [Русский](FAQ_ru)

---

> [Voltar ao Início](Home_pt)

---

## Perguntas Gerais

### O que é o PyGameMaker?

O PyGameMaker é um IDE de desenvolvimento de jogos de código aberto, inspirado no GameMaker 7.0. Permite-lhe criar jogos 2D usando programação visual (Google Blockly) ou um sistema de eventos-ações, sem precisar de escrever código.

### O PyGameMaker é gratuito?

Sim! O PyGameMaker é completamente gratuito e de código aberto — o código-fonte está sob a Licença MIT, e a documentação sob CC BY 4.0.

### Para que plataformas posso exportar?

- Windows (.exe autónomo)
- HTML5 (navegadores web)
- Linux (executável nativo)
- Móvel (iOS/Android através do Kivy)

### Preciso de experiência em programação?

Não! O PyGameMaker foi desenhado para iniciantes. Pode criar jogos usando:
- Blocos Blockly de arrastar e soltar
- Sistema de eventos/ações point-and-click
- Sem qualquer código

### É compatível com ficheiros do GameMaker?

O PyGameMaker é inspirado no GameMaker 7.0 mas usa o seu próprio formato de projeto. Não pode importar ficheiros do GameMaker diretamente, mas os conceitos e o fluxo de trabalho são semelhantes.

---

## Instalação

### Quais são os requisitos do sistema?

- Python 3.10 ou superior
- Windows, Linux ou macOS
- Mínimo 4 GB de RAM (8 GB recomendados)
- ~500 MB de espaço em disco

### Como instalo o PyGameMaker?

Veja [[Comecar_pt]] para instruções de instalação detalhadas. Versão resumida:

```bash
git clone https://github.com/Gabe1290/pythongm.git
cd pythongm
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
python main.py
```

### O Python não é reconhecido / não é encontrado

Certifique-se de que o Python está instalado e adicionado ao PATH do sistema. Verifique executando:

```bash
python --version
```

Se isto falhar, reinstale o Python e ative "Add Python to PATH" durante a instalação.

### Recebo erros de importação ao iniciar

Tente reinstalar as dependências:

```bash
pip install -r requirements.txt --force-reinstall
```

---

## Projetos

### Onde são guardados os meus projetos?

Os projetos são guardados em pastas que você escolhe. Cada projeto contém:
- `project.json` - O ficheiro principal do projeto
- Pastas para sprites, sons, objetos, salas, etc.

### Posso ter vários projetos abertos ao mesmo tempo?

Atualmente, o PyGameMaker abre um projeto de cada vez. Use **File > Open Project** para alternar entre projetos.

### Como faço uma cópia de segurança do meu projeto?

Basta copiar toda a pasta do projeto. Todos os recursos e configurações estão contidos nela. Considere também usar o git para controlo de versões:

```bash
cd meu_projeto
git init
git add .
git commit -m "Cópia de segurança inicial"
```

### O meu projeto não abre / está corrompido

Tente estes passos:
1. Verifique se `project.json` existe e não está vazio
2. Abra `project.json` num editor de texto para procurar erros JSON
3. Restaure a partir de uma cópia de segurança, se disponível
4. Verifique a saída da consola para mensagens de erro específicas

---

## Objetos e Eventos

### Qual é a diferença entre um objeto e uma instância?

- **Objeto**: Um modelo/molde que define o comportamento
- **Instância**: Uma cópia específica de um objeto colocada numa sala

Por exemplo, `obj_inimigo` é um objeto. Colocar 5 inimigos numa sala cria 5 instâncias de `obj_inimigo`.

### Porque não dispara o meu evento?

Causas comuns:
1. **Tipo de evento errado**: Certifique-se de usar o evento correto (ex. "Key Press" em vez de "Keyboard")
2. **Sem instâncias**: O objeto tem de ter instâncias na sala
3. **Objeto não visível**: Verifique a propriedade visible
4. **Ordem de execução**: Alguns eventos executam antes de outros

### Como faço os objetos interagirem?

Use eventos de colisão:
1. Abra o objeto que deve detetar a colisão
2. Adicione o evento **Collision with [outro_objeto]**
3. Adicione ações para o que acontece na colisão

### Qual é a diferença entre os eventos "Keyboard" e "Key Press"?

- **Keyboard [tecla]**: Dispara a cada quadro enquanto a tecla está pressionada
- **Key Press [tecla]**: Dispara uma vez quando a tecla é pressionada pela primeira vez
- **Key Release [tecla]**: Dispara uma vez quando a tecla é solta

---

## Salas

### Qual sala carrega primeiro?

A primeira sala na árvore de recursos (no topo da lista) carrega ao iniciar o jogo. Arraste as salas para as reordenar.

### Como mudo de sala?

Use as ações de sala:
- **Next Room**: Vai para a próxima sala em ordem
- **Previous Room**: Vai para a sala anterior
- **Go to Room**: Salta para uma sala específica

### Os objetos desaparecem quando mudo de sala

Os objetos são destruídos ao sair de uma sala, a menos que estejam marcados como **Persistent** nas suas propriedades.

### A minha sala é demasiado grande/pequena no ecrã

O tamanho da janela do jogo corresponde às dimensões da primeira sala. Pode:
- Alterar o tamanho da sala para corresponder ao tamanho de janela desejado
- Usar Views para mostrar apenas parte da sala

---

## Gráficos e Sprites

### Que formatos de imagem são suportados?

- PNG (recomendado, suporta transparência)
- JPEG/JPG
- BMP
- GIF (apenas o primeiro quadro)

### O meu sprite aparece na posição errada

Verifique a definição **Origin** no editor de sprites. A origem é o ponto de ancoragem para o posicionamento. Definições comuns:
- Superior esquerdo (0, 0): Padrão
- Centro: Bom para objetos rotativos
- Centro inferior: Bom para personagens

### Como animo um sprite?

1. Crie um sprite com vários quadros (tira horizontal)
2. Defina **Number of Frames** nas propriedades do sprite
3. Ajuste a **Animation Speed** (quadros por segundo)

### Os sprites estão desfocados

Isto acontece ao redimensionar sprites. Para pixel art, desative a interpolação/suavização nas definições do jogo, se disponível.

---

## Som e Música

### Que formatos de áudio são suportados?

- WAV (não comprimido)
- OGG (recomendado para música)
- MP3

### O som não é reproduzido

Verifique:
1. Se o ficheiro de áudio existe na pasta sounds
2. Se o formato do ficheiro é suportado
3. Se está a usar o nome de som correto nas ações
4. O navegador pode exigir interação do utilizador (para HTML5)

### Como faço a música de fundo repetir em loop?

Use a ação **Play Music** com a opção de loop ativada, ou **Play Sound** com o parâmetro loop definido como verdadeiro.

---

## Exportação

### O meu jogo exportado não funciona

Problemas comuns:
- **Windows**: DLLs em falta — certifique-se de que toda a pasta de saída está incluída
- **HTML5**: O navegador bloqueia ficheiros locais — aloje num servidor
- **Recursos em falta**: Verifique se todos os ficheiros estão incluídos

### O ficheiro exportado é enorme

O tamanho do jogo inclui o Python e todas as bibliotecas. Para o reduzir:
- Remova recursos não usados
- Comprima imagens e áudio
- Use formatos apropriados (OGG em vez de WAV)
- Ative a compressão UPX para builds de Windows

### Posso vender jogos feitos com o PyGameMaker?

Sim! Os jogos que criar são inteiramente seus e podem ser vendidos. O código-fonte do PyGameMaker está sob a permissiva Licença MIT, por isso pode usá-lo livremente em projetos comerciais — e, ao contrário das licenças copyleft, não é obrigado a tornar open-source as suas próprias modificações.

---

## Blockly / Programação Visual

### Onde encontro o editor Blockly?

1. Abra um objeto
2. Clique na aba **Blockly** no editor de objetos
3. Aparece a área de trabalho de programação visual

### Como alterno entre o Blockly e os eventos?

Ambos os sistemas trabalham sobre o mesmo objeto. A aba Blockly e a aba Events mostram vistas diferentes da mesma lógica. As alterações num refletem-se no outro.

### Os meus blocos de Blockly desapareceram

Verifique:
1. Se está a ver o objeto correto
2. Percorra a área de trabalho (os blocos podem estar fora do ecrã)
3. Verifique o nível de zoom

---

## Desempenho

### O meu jogo está lento

Dicas para melhor desempenho:
1. Reduza o número de instâncias
2. Evite cálculos pesados nos eventos Step
3. Use alarmes em vez de contar quadros
4. Otimize os tamanhos dos sprites
5. Destrua as instâncias que saem da sala

### O evento Step executa com demasiada frequência

O evento Step executa a cada quadro (60 vezes por segundo por defeito). Use:
- Alarmes para ações atrasadas
- Condições a verificar antes de operações pesadas
- Uma velocidade de sala mais baixa, se apropriado

---

## Obter Ajuda

### Onde posso reportar bugs?

Reporte bugs na página [GitHub Issues](https://github.com/Gabe1290/pythongm/issues). Inclua:
- O que esperava que acontecesse
- O que realmente aconteceu
- Passos para reproduzir o problema
- O seu sistema operativo e versão de Python

### Onde posso aprender mais?

- [[Comecar_pt]] - Instalação e fundamentos
- [[Primeiro_Jogo_pt]] - Tutorial passo a passo
- [[Eventos_e_Acoes_pt]] - Referência completa
- [[Programacao_Visual_pt]] - Guia do Blockly
