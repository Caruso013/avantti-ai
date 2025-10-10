"""
Script para monitorar o progresso do fine-tuning

Este script consulta o status do job e exibe informações em tempo real.
"""

import os
import sys
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class FineTuningMonitor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def get_job_status(self, job_id):
        """Consulta status detalhado do job"""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            return job
        except Exception as e:
            print(f"❌ Erro ao consultar job: {e}")
            return None
    
    def get_job_events(self, job_id, limit=10):
        """Consulta eventos do job (logs)"""
        try:
            events = self.client.fine_tuning.jobs.list_events(
                fine_tuning_job_id=job_id,
                limit=limit
            )
            return events.data
        except Exception as e:
            print(f"❌ Erro ao consultar eventos: {e}")
            return []
    
    def exibir_status(self, job):
        """Exibe status formatado do job"""
        print("\n" + "="*60)
        print("📊 STATUS DO FINE-TUNING")
        print("="*60)
        
        print(f"\n🆔 Job ID: {job.id}")
        print(f"📝 Status: {job.status}")
        print(f"🤖 Modelo base: {job.model}")
        print(f"✨ Modelo final: {job.fine_tuned_model or 'Ainda não disponível'}")
        
        if job.trained_tokens:
            print(f"\n📈 Progresso:")
            print(f"   Tokens treinados: {job.trained_tokens:,}")
        
        if job.error:
            print(f"\n❌ Erro: {job.error}")
        
        print(f"\n🕐 Criado em: {job.created_at}")
        if job.finished_at:
            print(f"✅ Finalizado em: {job.finished_at}")
            duration = job.finished_at - job.created_at
            print(f"⏱️  Duração: {duration // 60} minutos")
    
    def exibir_eventos(self, events):
        """Exibe eventos recentes do job"""
        if not events:
            print("\n📝 Nenhum evento disponível ainda.")
            return
        
        print("\n📝 Últimos eventos:")
        print("-" * 60)
        
        for event in reversed(events):  # Mostrar do mais antigo para o mais recente
            timestamp = time.strftime('%H:%M:%S', time.localtime(event.created_at))
            level = event.level.upper()
            message = event.message
            
            emoji = "ℹ️"
            if level == "INFO":
                emoji = "ℹ️"
            elif level == "WARNING":
                emoji = "⚠️"
            elif level == "ERROR":
                emoji = "❌"
            
            print(f"{emoji} [{timestamp}] {message}")
    
    def monitorar_continuo(self, job_id, intervalo=30):
        """Monitora o job continuamente até conclusão"""
        print(f"🔄 Monitorando job {job_id}...")
        print(f"   (Atualizando a cada {intervalo} segundos. Ctrl+C para sair)")
        
        try:
            while True:
                job = self.get_job_status(job_id)
                
                if not job:
                    print("❌ Não foi possível consultar o job.")
                    break
                
                # Limpar terminal (funciona no Windows e Unix)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                self.exibir_status(job)
                
                # Se o job terminou (sucesso ou erro), exibir eventos e sair
                if job.status in ['succeeded', 'failed', 'cancelled']:
                    events = self.get_job_events(job_id, limit=20)
                    self.exibir_eventos(events)
                    
                    if job.status == 'succeeded':
                        print("\n" + "="*60)
                        print("✨ FINE-TUNING CONCLUÍDO COM SUCESSO!")
                        print("="*60)
                        print(f"\n🎉 Seu modelo está pronto!")
                        print(f"   ID do modelo: {job.fine_tuned_model}")
                        print(f"\n📝 Para usar no código, substitua:")
                        print(f"   model='gpt-4o-mini'")
                        print(f"   por")
                        print(f"   model='{job.fine_tuned_model}'")
                    else:
                        print(f"\n❌ Job finalizado com status: {job.status}")
                    
                    break
                
                # Aguardar antes de próxima consulta
                print(f"\n⏳ Próxima atualização em {intervalo} segundos...")
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoramento interrompido.")
            print(f"   O treinamento continua rodando em segundo plano.")
            print(f"   Para retomar o monitoramento: python fine_tuning/monitor_training.py {job_id}")
    
    def consulta_unica(self, job_id):
        """Consulta única do status (sem loop)"""
        job = self.get_job_status(job_id)
        
        if not job:
            return
        
        self.exibir_status(job)
        
        events = self.get_job_events(job_id, limit=10)
        self.exibir_eventos(events)
        
        if job.status == 'succeeded':
            print("\n✨ Modelo pronto para uso!")
            print(f"   model='{job.fine_tuned_model}'")
        elif job.status in ['validating_files', 'queued', 'running']:
            print(f"\n⏳ Treinamento em andamento...")
            print(f"   Para monitorar continuamente: python fine_tuning/monitor_training.py {job_id} --watch")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("❌ Uso: python fine_tuning/monitor_training.py <JOB_ID> [--watch]")
        print("\nExemplo:")
        print("   python fine_tuning/monitor_training.py ftjob-abc123")
        print("   python fine_tuning/monitor_training.py ftjob-abc123 --watch")
        sys.exit(1)
    
    job_id = sys.argv[1]
    watch_mode = '--watch' in sys.argv or '-w' in sys.argv
    
    monitor = FineTuningMonitor()
    
    if watch_mode:
        monitor.monitorar_continuo(job_id, intervalo=30)
    else:
        monitor.consulta_unica(job_id)

if __name__ == "__main__":
    main()
