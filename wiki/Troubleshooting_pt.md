# Resolução de Problemas

> [English](Troubleshooting) | [Français](Troubleshooting_fr) | [Deutsch](Troubleshooting_de) | [Italiano](Troubleshooting_it) | [Español](Troubleshooting_es) | [Português](Troubleshooting_pt)

---

> [Voltar ao Início](Home_pt)

Problemas comuns e onde procurar. Para problemas específicos da
instalação (Python não encontrado, dependências em falta, bibliotecas
de visualização Linux), veja primeiro a secção Resolução de Problemas de
[[Comecar_pt|Primeiros Passos]] — esta página cobre problemas que
surgem quando o PyGameMaker já está em execução.

---

## O meu jogo bloqueia ou fecha imediatamente quando carrego em Testar Jogo (F5)

**Inicie o IDE a partir de um terminal, não de um atalho do ambiente de
trabalho, para ver o erro.** O traceback de um subprocesso de teste de
jogo que bloqueia é registado na saída da consola do próprio IDE
(`python main.py` num terminal) — se iniciou o IDE sem uma consola
visível (por exemplo, um atalho do Windows), essa mensagem não tem onde
aparecer. Reinicie a partir de um terminal e reproduza o bloqueio para
ver o verdadeiro traceback Python.

Causas comuns:
- Uma ação **Executar Código** ou código personalizado no Editor de
  Código com um erro de sintaxe ou um erro de digitação numa chamada
  `game.*`/`self.*`
- Uma ação de colisão ou comparação que referencia um objeto que
  entretanto foi renomeado ou eliminado

---

## O próprio IDE bloqueou quando tentei abrir um editor

Verifique **`~/pygamemaker_crash.log`** (na sua pasta pessoal) — os
bloqueios do editor de objetos/salas/sprites são escritos ali
especificamente para ficarem visíveis mesmo quando o IDE foi iniciado
sem uma janela de consola. Inclua a secção relevante desse ficheiro se
reportar o erro.

---

## A exportação diz "X não encontrado" / falta uma dependência

As exportações de desktop e móvel (.exe Windows, .app macOS, binário
Linux, Kivy/Android/iOS) incluem um runtime através do PyInstaller ou
Buildozer, e essas ferramentas têm de estar instaladas no **mesmo Python
que executa o IDE** — uma instalação a nível de sistema noutro sítio na
máquina não conta. A mensagem de erro da caixa de diálogo de exportação
dá a solução exata, mas resumidamente:

- **Não são necessários direitos de administrador.** Ative o seu
  ambiente virtual e execute `pip install <pacote>`, ou instale na sua
  própria conta com `pip install --user <pacote>` — ambos funcionam sem
  direitos de admin.
- Instalar tudo de uma vez: `pip install -r requirements.txt`
- **Não quer nenhuma instalação?** Use antes a exportação **HTML5
  (Navegador Web)** — não precisa de nada instalado localmente e o
  resultado funciona em qualquer navegador. (Note que isto só se aplica
  à *construção* da exportação — um `.exe`/`.app` terminado não precisa
  de nada instalado na máquina que apenas o *executa*.)

---

## Recebi um aviso antes da Exportação ("X usa Y mas não há Z")

A exportação corre primeiro uma validação do projeto e mostra tudo o
que encontra antes de a caixa de diálogo de Exportação aparecer — por
exemplo, um objeto que usa **Próxima Sala** num projeto com apenas uma
sala, o que não teria qualquer efeito. Estes são **avisos, não erros**:
clique OK e a exportação continua; apontam para lógica que
provavelmente não faz o que espera, sem o impedir de publicar.

---

## Um sprite mostra um selo vermelho "(não importado)" na árvore de recursos

Isto significa que o ficheiro de imagem do sprite está em falta no
disco (geralmente porque um projeto foi copiado ou partilhado sem a sua
pasta `sprites/`). É puramente informativo — a execução e a exportação
ignoram-no — e **corrige-se automaticamente na próxima gravação**,
assim que o ficheiro estiver realmente presente de novo. Não é
necessária qualquer correção manual para além de garantir que o
ficheiro de imagem está onde o sprite o espera.

---

## Outra coisa está errada

- Consulte a [[FAQ_pt|FAQ]] para perguntas comuns
- Reporte erros no [Rastreador de Problemas do GitHub](https://github.com/Gabe1290/pythongm/issues) — inclua o seu sistema operativo, a sua versão de Python, e (se relevante) a saída da consola ou `~/pygamemaker_crash.log`

---

## Próximos Passos

- [[Comecar_pt|Primeiros Passos]] - Resolução de problemas de instalação
- [[Exportar_Jogos_pt|Exportar Jogos]] - Referência completa de exportação
- [[FAQ_pt|FAQ]] - Perguntas frequentes
