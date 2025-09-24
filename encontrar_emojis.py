#!/usr/bin/env python3
import re

def encontrar_emojis_no_arquivo(arquivo):
    """Encontra todos os emojis em um arquivo específico"""
    
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
            
        print(f"🔍 Analisando arquivo: {arquivo}")
        emojis_encontrados = []
        
        for i, linha in enumerate(linhas, 1):
            emojis = emoji_pattern.findall(linha)
            if emojis:
                print(f"Linha {i}: {linha.strip()}")
                for emoji in emojis:
                    print(f"  ➤ Emoji encontrado: {emoji}")
                    emojis_encontrados.extend(emojis)
                print()
        
        print(f"Total de emojis encontrados: {len(emojis_encontrados)}")
        return len(emojis_encontrados)
        
    except Exception as e:
        print(f"Erro ao ler arquivo {arquivo}: {e}")
        return 0

if __name__ == "__main__":
    encontrar_emojis_no_arquivo("app.py")