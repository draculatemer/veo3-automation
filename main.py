
import os
import sys
import time
import requests
from dotenv import load_dotenv
from docx import Document
import vertexai
from vertexai.preview.vision_models import Image, ImageToVideoModel

# Carregar variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÕES ---
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_LOCATION")
SEAART_API_KEY = os.getenv("SEAART_API_KEY")
# URL de exemplo (Verifique na documentação da SeaArt a URL exata do Swap Face)
SEAART_ENDPOINT = os.getenv("SEAART_API_URL", "https://api.seaart.ai/v1/tools/face-swap") 

# Configurar Vertex AI (Google)
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- FUNÇÕES UTILITÁRIAS ---

def carregar_prompts_docx(caminho_docx):
    """Lê o arquivo Word e mapeia VEO PROMPT - X para o texto."""
    if not os.path.exists(caminho_docx):
        print(f"[ERRO] Arquivo de prompts não encontrado: {caminho_docx}")
        return {}

    doc = Document(caminho_docx)
    prompts = {}
    current_key = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if text.upper().startswith("VEO PROMPT - "):
            # Extrai a letra (Ex: VEO PROMPT - A -> 'A')
            letra = text.split("-")[-1].strip().upper()
            current_key = letra
        elif current_key and text:
            # Assume que o próximo parágrafo com texto é o prompt
            prompts[current_key] = text
            current_key = None # Reseta para buscar a próxima chave
    
    print(f"[INFO] Prompts carregados para as letras: {list(prompts.keys())}")
    return prompts

def selecionar_rosto():
    """Menu para o usuário escolher qual rosto usar (1-5)."""
    print("\n--- SELEÇÃO DE ROSTO ---")
    files = sorted([f for f in os.listdir("FACE_SOURCE") if f.endswith(('.png', '.jpg'))])
    
    if not files:
        print("[ERRO] Nenhum rosto encontrado em FACE_SOURCE!")
        sys.exit()

    for f in files:
        print(f"Opção encontrada: {f}")

    while True:
        try:
            choice = input(f"\nDigite o número do rosto desejado (1 a 5): ")
            target_file = f"{choice}rosto.png" # Ajuste se suas extensões variarem
            
            full_path = os.path.join("FACE_SOURCE", target_file)
            if os.path.exists(full_path):
                print(f"[OK] Rosto selecionado: {target_file}")
                return full_path
            else:
                print(f"[ERRO] Arquivo {target_file} não existe. Tente novamente.")
        except ValueError:
            print("Entrada inválida.")

def executar_seaart_swap(frame_path, face_path, letter):
    """
    Envia imagens para SeaArt e retorna o caminho da imagem salva com rosto trocado.
    NOTA: A estrutura do payload depende da documentação exata da SeaArt.
    """
    print(f"   [SeaArt] Iniciando Face Swap para frame {letter}...")
    
    # ------------------------------------------------------------------
    # ATENÇÃO: Esta é uma estrutura GENÉRICA. Você precisa confirmar 
    # na doc da SeaArt como eles pedem o upload (Base64 ou URL pública).
    # Muitas APIs exigem que a imagem já esteja hospedada online.
    # ------------------------------------------------------------------
    
    # Exemplo simplificado (verifique a API real):
    headers = {
        "Authorization": f"Bearer {SEAART_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simulação de Payload (AJUSTAR CONFORME DOC SEAART)
    # Normalmente APIs de imagem pedem URLs ou Base64 strings.
    payload = {
        "source_image": "caminho_ou_base64_da_face", # Precisa converter face_path
        "target_image": "caminho_ou_base64_do_frame" # Precisa converter frame_path
    }

    try:
        # response = requests.post(SEAART_ENDPOINT, json=payload, headers=headers)
        # response.raise_for_status()
        # result_url = response.json().get("output_url")
        
        # MOCK TEMPORÁRIO PARA TESTE (Enquanto você não configura a API Real):
        # Ele apenas copia o frame original para a pasta temp.
        # REMOVA ISSO E DESCOMENTE O CÓDIGO ACIMA QUANDO TIVER A DOC.
        import shutil
        output_path = os.path.join("TEMP_FRAMES", f"{letter}_swapped.png")
        shutil.copy(frame_path, output_path)
        time.sleep(1) # Simula processamento
        
        return output_path

    except Exception as e:
        print(f"   [ERRO SeaArt] Falha ao processar: {e}")
        return None

def gerar_video_veo(image_path, prompt_text, letter):
    """Envia imagem + texto para Google VEO (Vertex AI)."""
    print(f"   [Google VEO] Gerando vídeo para {letter}...")
    
    output_file = os.path.join("output", f"video_{letter}.mp4")
    
    if os.path.exists(output_file):
        print(f"   [INFO] Vídeo {output_file} já existe. Pulando.")
        return

    try:
        # Carregar modelo (nome pode variar, ex: "image-to-video", "veo-003")
        model = ImageToVideoModel.from_pretrained("image-to-video") 
        
        # Carregar imagem do disco
        img = Image.load_from_file(image_path)
        
        # Gerar vídeo
        video = model.generate_video(
            video_image=img,
            prompt=prompt_text,
            number_of_videos=1,
            enhancement_mode=False
        )

        # Salvar
        # Nota: O SDK do Vertex pode retornar o vídeo como bytes ou arquivo.
        # Ajuste conforme a resposta do objeto 'video'.
        with open(output_file, "wb") as f:
            f.write(video[0].video_bytes) # Exemplo de como pegar os bytes
            
        print(f"   [SUCESSO] Vídeo salvo: {output_file}")

    except Exception as e:
        print(f"   [ERRO VEO] Falha na geração: {e}")

# --- BLOCO PRINCIPAL ---

def main():
    # 1. Cria pastas necessárias
    os.makedirs("output", exist_ok=True)
    os.makedirs("TEMP_FRAMES", exist_ok=True)
    
    print("=== INICIANDO VEO3 AUTOMATION (MULTI-FACE & WEBP) ===")

    # 2. Selecionar Rosto
    face_path = selecionar_rosto()

    # 3. Carregar Prompts
    prompts_map = carregar_prompts_docx("PROMPTS VEO.DOCX")
    
    # 4. Loop A-Z
    alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    for letra in alfabeto:
        frame_file = os.path.join("FRAME", f"{letra}.webp") # Agora busca .webp
        prompt_text = prompts_map.get(letra)

        if os.path.exists(frame_file) and prompt_text:
            print(f"\n>>> Processando Letra: {letra}")
            
            # Passo A: Face Swap (SeaArt)
            # Resultado vai para TEMP_FRAMES
            swapped_image = executar_seaart_swap(frame_file, face_path, letra)
            
            if swapped_image:
                # Passo B: Video Gen (Google VEO)
                # Usa a imagem trocada e o prompt
                gerar_video_veo(swapped_image, prompt_text, letra)
            else:
                print(f"   [PULADO] Falha no Face Swap para {letra}")
        
        elif not os.path.exists(frame_file):
            # Apenas ignora se não tiver o frame, sem poluir muito o log
            pass 

if __name__ == "__main__":
    main()
