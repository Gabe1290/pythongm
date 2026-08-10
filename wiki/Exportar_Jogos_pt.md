# Exportar Jogos

> [English](Exporting-Games) | [Français](Exportation_fr) | [Deutsch](Spiele_Exportieren_de) | [Italiano](Esportare_Giochi_it) | [Español](Exportar_Juegos_es) | [Português](Exportar_Jogos_pt) | [Slovenščina](Izvoz_Iger_sl) | [Українська](Eksport_Ihor_uk) | [Русский](Eksport_Igr_ru)

---

> [Voltar ao Início](Home_pt)

O PyGameMaker pode exportar o seu jogo para várias plataformas. Este guia abrange cada opção de exportação e como utilizá-la.

---

## Visão geral da exportação

| Plataforma | Formato | Requisitos |
|------------|---------|------------|
| **Windows** | .exe | PyInstaller |
| **macOS** | .app | PyInstaller (num Mac) |
| **HTML5** | .html | Navegador moderno |
| **Linux** | Binário | PyInstaller, Python 3.10+ |
| **Kivy / Android** | Código-fonte / .apk | Buildozer |
| **Projeto (.zip)** | .zip | — (partilhar o projeto editável) |

> **Nada é descartado silenciosamente.** Se o seu jogo utilizar uma ação que um
> destino não consegue reproduzir (por exemplo, algumas ações não são suportadas pela
> exportação Kivy/Android), a exportação é bem-sucedida na mesma, mas indica-lhe
> exatamente que ações foram **ignoradas**, para que possa ajustar. Se o seu projeto
> utilizar uma [extensão](Extensions_pt) desativada (por ex. a Vista 3D), o IDE
> avisa-o ao carregar.

---

## Exportação Windows EXE

Crie um executável Windows autónomo que funciona sem Python instalado.

### Como exportar

1. Abra **Ficheiro → Exportar projeto…** (Ctrl+E) e escolha **Windows**
2. Escolha uma pasta de saída
3. Aguarde a conclusão do processo de compilação
4. Encontre o ficheiro .exe na pasta de saída

### O que é criado

```
pasta_saida/
├── MeuJogo.exe       # Executável principal
├── _internal/        # Bibliotecas necessárias
└── assets/           # Recursos do jogo
```

### Requisitos

- PyInstaller (instalado através de `pip install pyinstaller`)
- Sistema Windows para a compilação (a compilação cruzada não é suportada)

### Distribuição

Para partilhar o jogo:
1. Comprima em zip toda a pasta de saída
2. Distribua o ficheiro zip
3. Os utilizadores extraem e executam o .exe

### Resolução de problemas

**DLL em falta:** Certifique-se de que todas as dependências estão incluídas. Verifique a saída do PyInstaller quanto a avisos.

**Alertas de antivírus:** Alguns antivírus assinalam os executáveis do PyInstaller. É um falso positivo. Poderá ter de assinar o seu executável.

---

## Exportação de app macOS

Crie um pacote `.app` nativo para macOS com o PyInstaller.

### Como exportar

1. Abra **Ficheiro → Exportar projeto…** (Ctrl+E) e escolha **macOS**
2. Escolha uma pasta de saída
3. Aguarde a conclusão da compilação
4. Encontre `MeuJogo.app` na pasta de saída

### Requisitos

- Um **Mac** para a compilação (a compilação cruzada a partir de Windows/Linux não é suportada)
- PyInstaller e Kivy instalados no Python de compilação

### Distribuição

Comprima o pacote `.app` em zip para o partilhar. As apps não assinadas acionam o
Gatekeeper noutros Mac — os utilizadores fazem clique com o botão direito → **Abrir**
na primeira vez, ou assina/notariza a app com uma conta Apple Developer.

---

## Exportação HTML5

Crie um único ficheiro HTML que funciona nos navegadores web.

### Como exportar

1. Vá a **Ficheiro → Exportar como HTML5…**
2. Escolha uma localização de saída
3. Selecione as opções (compressão, etc.)
4. Clique em Exportar

### O que é criado

```
pasta_saida/
└── MeuJogo.html      # Jogo de ficheiro único
```

### Características

- Funciona em qualquer navegador moderno (Chrome, Firefox, Edge, Safari)
- Não requer instalação
- Comprimido com gzip para um carregamento rápido
- Compatível com dispositivos móveis com controlos táteis

### Alojar o seu jogo

Carregue o ficheiro HTML para:
- O seu próprio servidor web
- GitHub Pages (gratuito)
- itch.io (alojamento orientado a jogos)
- Qualquer alojamento de ficheiros estáticos

### Compatibilidade de navegadores

| Navegador | Suporte |
|-----------|---------|
| Chrome 80+ | Completo |
| Firefox 75+ | Completo |
| Edge 80+ | Completo |
| Safari 13+ | Completo |
| Chrome móvel | Completo |
| Safari móvel | Completo |

### Limitações

- Algumas funcionalidades podem não funcionar (acesso ao sistema de ficheiros, etc.)
- O áudio pode requerer uma interação do utilizador para iniciar
- O desempenho depende do dispositivo/navegador

---

## Exportação Linux

Crie um executável Linux nativo.

### Como exportar

1. Abra **Ficheiro → Exportar projeto…** (Ctrl+E) e escolha **Linux**
2. Escolha uma pasta de saída
3. Aguarde o processo de compilação

### Requisitos

- Sistema Linux para a compilação
- Python 3.10+
- PyInstaller

### Distribuição

```bash
# Tornar o ficheiro executável
chmod +x MeuJogo

# Executar o jogo
./MeuJogo
```

Distribua como arquivo .tar.gz:
```bash
tar -czvf MeuJogo-linux.tar.gz MeuJogo/
```

---

## Exportação Kivy (móvel)

Crie apps móveis para iOS e Android utilizando o framework Kivy.

### Como exportar

1. Vá a **Ficheiro → Exportar para Kivy…**
2. Escolha uma pasta de saída
3. Configure as definições móveis
4. Exporte o projeto Kivy

### Compilar para Android

O projeto Kivy exportado utiliza o Buildozer para criar os APK:

```bash
cd projeto_exportado
pip install buildozer
buildozer init
buildozer android debug
```

### Compilar para iOS

Requer um Mac com Xcode:

```bash
cd projeto_exportado
pip install kivy-ios
toolchain build python3 kivy
toolchain create MeuJogo ~/projeto_ios
```

### Considerações móveis

- Os controlos táteis são mapeados automaticamente
- O redimensionamento do ecrã é gerido automaticamente
- Teste em vários tamanhos de ecrã
- Otimize os tamanhos dos recursos para móvel

---

## Exportação do projeto (.zip)

Partilhe o próprio **projeto editável** (não um jogo compilado): utilize
**Ficheiro → Exportar projeto…** (Ctrl+E) para criar um arquivo `.zip` que outra
pessoa pode reabrir no PyGameMaker. Ideal para a colaboração, cópias de segurança ou
a entrega de trabalhos escolares.

---

## Opções de exportação

### Definições gerais

| Definição | Descrição |
|-----------|-----------|
| **Nome do jogo** | Nome apresentado na barra de título/app |
| **Ícone** | Ícone da aplicação (Windows/móvel) |
| **Versão** | Número de versão (1.0.0) |
| **Autor** | Nome do programador |

### Definições do Windows

| Definição | Descrição |
|-----------|-----------|
| **Consola** | Mostrar a janela da consola (para depuração) |
| **Ficheiro único** | Um só .exe vs. pasta com _internal |
| **UPX** | Comprimir com UPX (tamanho reduzido) |

### Definições do HTML5

| Definição | Descrição |
|-----------|-----------|
| **Compressão** | Ativar a compressão gzip |
| **Ecrã inteiro** | Iniciar em modo de ecrã inteiro |
| **Controlos táteis** | Mostrar os controlos no ecrã |

---

## Lista de verificação antes de exportar

Antes de exportar, verifique:

- [ ] Todos os recursos estão incluídos no projeto
- [ ] O jogo funciona corretamente no IDE
- [ ] Sem mensagens de depuração ou código de teste
- [ ] A ordem das salas está correta (sala inicial primeiro)
- [ ] Os ficheiros de áudio estão em formatos suportados
- [ ] Os sprites estão otimizados por tamanho de ficheiro

---

## Otimizar o tamanho dos ficheiros

### Sprites
- Utilize dimensões apropriadas (não sobredimensionadas)
- Comprima os ficheiros PNG
- Considere o JPEG para imagens sem transparência

### Áudio
- Utilize OGG/MP3 para a música (não WAV)
- Mantenha curtos os efeitos sonoros
- Frequências de amostragem mais baixas para sons simples

### Geral
- Remova os recursos não utilizados
- Minimize os tamanhos das salas
- Teste nas plataformas de destino

---

## Testar as exportações

Teste sempre o seu jogo exportado:

1. **Windows:** Teste num PC limpo sem Python
2. **HTML5:** Teste em vários navegadores
3. **Linux:** Se possível, teste em diferentes distribuições
4. **Móvel:** Teste em dispositivos reais, não apenas em emuladores

---

## Plataformas de distribuição

### itch.io
- Alojamento gratuito para jogos indie
- Suporta HTML5, Windows, Linux, Mac
- Sistema de pagamento integrado

### Steam
- Requer a integração do SDK Steamworks
- Utilize o PyInstaller com a API Steam
- Taxa de publicação paga

### Google Play (Android)
- Requer uma conta de programador (25 $)
- Compile um APK assinado com o Buildozer
- Siga as diretrizes de conteúdo

### App Store (iOS)
- Requer uma conta Apple Developer (99 $/ano)
- Compile com o kivy-ios
- Submeta através do App Store Connect

---

## Próximos passos

- [[Comecar_pt]] - Rever os conceitos básicos
- [[Troubleshooting_pt|Resolução de Problemas]] - Erros de dependências em falta e outros problemas de exportação
- [[FAQ_pt]] - Perguntas comuns sobre a exportação
- [GitHub Issues](https://github.com/Gabe1290/pythongm/issues) - Reportar problemas de exportação
