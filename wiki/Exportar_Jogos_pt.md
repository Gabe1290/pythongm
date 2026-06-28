# Exportar Jogos

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

[Voltar ao Inicio](Home_pt)

Aprenda como exportar os seus jogos pyGM para diferentes plataformas.

## Visao geral

O pyGM permite a exportacao para:
- Windows (EXE)
- macOS (APP)
- Linux
- Web (HTML5)

## Preparacao para a exportacao

### Antes de exportar, verifique
1. **Todos os recursos presentes**: Sprites, sons, etc.
2. **Jogo testado**: Sem erros criticos
3. **Configuracoes otimizadas**: Resolucao, ecra inteiro

### Configuracoes do projeto
- **Nome do jogo**: Nome apresentado
- **Versao**: Numero de versao
- **Icone**: Icone da aplicacao
- **Ecra de inicio**: Splash Screen

## Exportacao Windows

### Requisitos
- pyinstaller instalado
- Sistema Windows ou compilacao cruzada

### Passos
1. Va a Ficheiro > Exportar
2. Selecione "Windows Executable"
3. Configure as opcoes:
   - Ficheiro de icone
   - Ocultar janela de consola
   - Ficheiro EXE unico
4. Clique em "Exportar"

### Saida
- Ficheiro EXE unico
- Ou pasta com dependencias

## Exportacao macOS

### Requisitos
- Sistema macOS recomendado
- py2app ou pyinstaller

### Passos
1. Ficheiro > Exportar > macOS
2. Introduza nome do App Bundle
3. Escolha icone (formato ICNS)
4. Exportar

## Exportacao Linux

### Opcoes
- AppImage (recomendado)
- Pacote Debian
- Ficheiro executavel

### Passos
1. Ficheiro > Exportar > Linux
2. Escolha formato
3. Exportar

## Exportacao Web (HTML5)

### Vantagens
- Funciona no navegador
- Facil de partilhar
- Sem instalacao necessaria

### Passos
1. Ficheiro > Exportar > Web
2. Configure:
   - Tamanho do canvas
   - Ecra de carregamento
   - Compressao
3. Exportar

### Saida
- Ficheiro HTML
- Ficheiros JavaScript
- Pasta de recursos

### Alojamento
- Carregue para um servidor web
- Use itch.io
- Use GitHub Pages

## Opcoes de exportacao

### Gerais
- **Compressao**: Reduzir tamanho do ficheiro
- **Modo de depuracao**: Manter para testes
- **Incorporar recursos**: Tudo num ficheiro

### Especificas de plataforma
- **Windows**: Manifesto UAC
- **macOS**: Assinatura de codigo
- **Web**: Versao WebGL

## Resolucao de problemas

### Problemas comuns

**A exportacao falha**
- Verifique as mensagens de erro
- Atualize o pyinstaller

**Faltam recursos**
- Verifique os caminhos
- Volte a incluir os recursos

**O jogo nao inicia**
- Teste em modo de depuracao
- Verifique as dependencias

## Otimizacao

1. **Otimize tamanhos de imagem**: Comprima sprites
2. **Comprima audio**: MP3 em vez de WAV
3. **Remova recursos nao utilizados**
4. **Otimize o codigo**: Melhore a eficiencia

## Ver tambem

- [FAQ](FAQ_pt)
- [Criar o seu primeiro jogo](Primeiro_Jogo_pt)
- [Comecar](Comecar_pt)
