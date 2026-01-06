# 🎬 VEO3 AutoGenerator: Multi-Face & WebP Pipeline

Este projeto automatiza a criação de vídeos de 8 segundos integrando **SeaArt (Face Swap)** e **Google VEO3 (Video Generation)**. O sistema permite escolher entre múltiplos rostos pré-definidos para aplicar em frames base (`.webp`), gerando vídeos em massa com base em prompts sequenciais (A-Z).

## 📋 Funcionalidades

* **Suporte a WebP:** Otimizado para usar frames iniciais leves em formato `.webp`.
* **Multi-Face Selector:** Possui uma biblioteca de 5 rostos (`1rosto` a `5rosto`). Ao iniciar o script, você escolhe qual rosto aplicar em todo o lote de vídeos.
* **Automação A-Z:** Processa automaticamente a sequência de arquivos `A.webp` + `Prompt A` até o final.

## 📂 Estrutura Obrigatória

Para o funcionamento correto, organize os arquivos desta forma:

veo3-automation/
│
├── FACE_SOURCE/            # Banco de rostos (PNG ou JPG)
│   ├── 1rosto.png          # Opção de rosto 1
│   ├── 2rosto.png          # Opção de rosto 2
│   ├── ...
│   └── 5rosto.png          # Até a opção 5
│
├── FRAME/                  # Frames iniciais do vídeo (Formato .webp)
│   ├── A.webp
│   ├── B.webp
│   └── ... Z.webp
│
├── TEMP_FRAMES/            # Pasta temporária (criada automaticamente)
│                           # Armazena o frame após o Face Swap
│
├── PROMPTS VEO.DOCX        # Arquivo Word com os textos (VEO PROMPT - A...)
├── output/                 # Vídeos gerados (video_A.mp4...)
├── .env                    # Chaves de API (Google & SeaArt)
└── main.py                 # Script Principal
