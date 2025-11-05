"""
Script para fazer upload dos dados e iniciar fine-tuning no OpenAI

Este script:
1. Faz upload do arquivo JSONL para OpenAI
2. Cria um job de fine-tuning
3. Retorna o ID do job para monitoramento
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class FineTuningUploader:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def upload_training_file(self, file_path):
        """Faz upload do arquivo de treinamento"""
        print(f"📤 Fazendo upload de: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose='fine-tune'
                )
            
            file_id = response.id
            print(f"   ✅ Upload concluído! File ID: {file_id}")
            return file_id
            
        except Exception as e:
            print(f"   ❌ Erro no upload: {e}")
            return None
    
    def create_fine_tuning_job(self, file_id, model='gpt-4o-mini-2024-07-18', suffix=None):
        """Cria um job de fine-tuning"""
        print(f"\n🎯 Criando job de fine-tuning...")
        print(f"   Modelo base: {model}")
        
        try:
            job_params = {
                "training_file": file_id,
                "model": model
            }
            
            # Adicionar suffix se fornecido (identificação do modelo)
            if suffix:
                job_params["suffix"] = suffix
                print(f"   Suffix: {suffix}")
            
            response = self.client.fine_tuning.jobs.create(**job_params)
            
            job_id = response.id
            print(f"   ✅ Job criado! Job ID: {job_id}")
            print(f"\n📊 Status: {response.status}")
            
            return job_id, response
            
        except Exception as e:
            print(f"   ❌ Erro ao criar job: {e}")
            return None, None
    
    def get_job_status(self, job_id):
        """Consulta o status de um job"""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            return job
        except Exception as e:
            print(f"❌ Erro ao consultar job: {e}")
            return None
    
    def executar(self, training_file='training_data.jsonl', suffix='evex-eliane'):
        """Executa todo o processo de upload e criação do fine-tuning"""
        print("🚀 Iniciando processo de fine-tuning...\n")
        
        # Verificar se arquivo existe
        file_path = os.path.join(os.path.dirname(__file__), training_file)
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            print(f"   Execute primeiro: python fine_tuning/prepare_training_data.py")
            return None
        
        # 1. Upload do arquivo
        file_id = self.upload_training_file(file_path)
        if not file_id:
            return None
        
        # 2. Criar job de fine-tuning
        job_id, job_info = self.create_fine_tuning_job(
            file_id=file_id,
            model='gpt-4o-mini-2024-07-18',
            suffix=suffix
        )
        
        if not job_id:
            return None
        
        # 3. Salvar informações do job
        self._salvar_job_info(job_id, file_id, job_info)
        
        # 4. Instruções finais
        print("\n" + "="*60)
        print("✨ FINE-TUNING INICIADO COM SUCESSO!")
        print("="*60)
        print(f"\n📝 Informações importantes:")
        print(f"   Job ID: {job_id}")
        print(f"   File ID: {file_id}")
        print(f"   Status atual: {job_info.status if job_info else 'unknown'}")
        
        print(f"\n⏳ O treinamento pode levar de 10 minutos a algumas horas.")
        print(f"\n📊 Para monitorar o progresso:")
        print(f"   python fine_tuning/monitor_training.py {job_id}")
        
        print(f"\n🌐 Ou acesse o dashboard:")
        print(f"   https://platform.openai.com/finetune/{job_id}")
        
        return job_id
    
    def _salvar_job_info(self, job_id, file_id, job_info):
        """Salva informações do job em arquivo local"""
        import json
        from datetime import datetime
        
        info_file = os.path.join(os.path.dirname(__file__), 'fine_tuning_jobs.json')
        
        # Carregar jobs existentes
        jobs = []
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                jobs = json.load(f)
        
        # Adicionar novo job
        jobs.append({
            'job_id': job_id,
            'file_id': file_id,
            'status': job_info.status if job_info else 'unknown',
            'created_at': datetime.now().isoformat(),
            'model': job_info.model if job_info else 'gpt-4o-mini-2024-07-18'
        })
        
        # Salvar
        with open(info_file, 'w') as f:
            json.dumps(jobs, f, indent=2)
        
        print(f"\n💾 Informações salvas em: {info_file}")

def main():
    """Função principal"""
    uploader = FineTuningUploader()
    
    # Você pode customizar o suffix aqui (será o nome do modelo)
    # Exemplo: "evex-eliane-v2", "evex-sdr-2025", etc.
    uploader.executar(
        training_file='training_data.jsonl',
        suffix='evex-eliane'
    )

if __name__ == "__main__":
    main()
