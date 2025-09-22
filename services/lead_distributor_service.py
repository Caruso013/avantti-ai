"""
Sistema de distribuição de leads entre equipes Contact2Sale
"""

import os
import json
import logging
import random
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TeamInfo:
    """Informações de uma equipe"""
    company_id: str
    name: str
    active: bool = True
    priority: int = 1  # 1=alta, 2=normal, 3=baixa
    max_leads_per_day: Optional[int] = None

class LeadDistributor:
    """Distribuidor de leads entre equipes"""
    
    def __init__(self):
        # Equipes da Evex Imóveis (baseado na resposta da API)
        self.teams = [
            TeamInfo(
                company_id="c9433557c1656dea3004165b6bcb7e2a",
                name="Evex Imóveis - Principal",
                priority=1
            ),
            TeamInfo(
                company_id="cb6909c5e37eeaafcc9cc6836c3803aa", 
                name="Evex Imóveis - Corretores",
                priority=1
            ),
            TeamInfo(
                company_id="4f83feb6f3bd5ff1f4eee42b6bb0b154",
                name="Evex Imóveis - Equipe Uliane",
                priority=2
            ),
            TeamInfo(
                company_id="b9ea1217943e965bf7308a9dba5cd8f1",
                name="Evex Imóveis - Equipe Johnny", 
                priority=2
            ),
            TeamInfo(
                company_id="88367ead3e3a8bbf5d1f439845ab74a9",
                name="Evex Imóveis - Silvio",
                priority=2
            ),
            TeamInfo(
                company_id="a97d32e9c6272650e5edd5975f59e70c",
                name="Evex Imóveis - Equipe Laiana",
                priority=2
            ),
            TeamInfo(
                company_id="8f13cdadcaafcf5089d78c7f385ac1db",
                name="Evex Imóveis - Equipe Ludovico",
                priority=2
            ),
            TeamInfo(
                company_id="012b545e89037c5b690192f9eefd272e",
                name="Evex Imóveis - Equipe Irineu",
                priority=2
            ),
            TeamInfo(
                company_id="9f05463d94a6cdd3c85378ad1709ddd6",
                name="Evex Imóveis - Equipe CH STO Antonio",
                priority=2
            ),
            TeamInfo(
                company_id="2ab9583a548aa0c069ab24129fd7449d",
                name="Evex Imóveis - Equipe Molinari",
                priority=2
            ),
            TeamInfo(
                company_id="8bc37f84ee2fc59c0f7ca028e0778d0a",
                name="Evex Imóveis - Equipe Ponta Grossa",
                priority=3  # Menor prioridade por ser cidade específica
            )
        ]
        
        # Configurações de distribuição
        self.distribution_method = os.getenv("C2S_DISTRIBUTION_METHOD", "round_robin")  # round_robin, random, priority
        self.queue_file = "data/lead_distribution_queue.json"
        self.stats_file = "data/lead_distribution_stats.json"
        
        # Cria diretório se não existir
        os.makedirs("data", exist_ok=True)
        
        # Carrega estado da fila
        self._load_queue_state()
        
        logger.info(f"Lead distributor inicializado com {len(self.get_active_teams())} equipes ativas")
    
    def get_active_teams(self) -> List[TeamInfo]:
        """Retorna apenas equipes ativas"""
        return [team for team in self.teams if team.active]
    
    def _load_queue_state(self):
        """Carrega estado da fila de distribuição"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    self.current_index = data.get("current_index", 0)
                    self.last_distribution = data.get("last_distribution")
            else:
                self.current_index = 0
                self.last_distribution = None
        except Exception as e:
            logger.error(f"Erro ao carregar estado da fila: {e}")
            self.current_index = 0
            self.last_distribution = None
    
    def _save_queue_state(self):
        """Salva estado da fila de distribuição"""
        try:
            data = {
                "current_index": self.current_index,
                "last_distribution": self.last_distribution,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.queue_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar estado da fila: {e}")
    
    def _update_stats(self, team: TeamInfo, lead_info: Dict):
        """Atualiza estatísticas de distribuição"""
        try:
            # Carrega stats existentes
            stats = {}
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Inicializa estrutura se não existir
            if today not in stats:
                stats[today] = {}
            
            if team.company_id not in stats[today]:
                stats[today][team.company_id] = {
                    "team_name": team.name,
                    "leads_count": 0,
                    "leads": []
                }
            
            # Adiciona lead
            stats[today][team.company_id]["leads_count"] += 1
            stats[today][team.company_id]["leads"].append({
                "timestamp": datetime.now().isoformat(),
                "phone": lead_info.get("phone", ""),
                "name": lead_info.get("name", ""),
                "source": lead_info.get("source", "")
            })
            
            # Salva stats
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas: {e}")
    
    def _round_robin_distribution(self) -> TeamInfo:
        """Distribuição por rodízio (round robin)"""
        active_teams = self.get_active_teams()
        
        if not active_teams:
            raise ValueError("Nenhuma equipe ativa disponível")
        
        # Pega equipe atual e avança índice
        team = active_teams[self.current_index % len(active_teams)]
        self.current_index = (self.current_index + 1) % len(active_teams)
        
        return team
    
    def _random_distribution(self) -> TeamInfo:
        """Distribuição aleatória"""
        active_teams = self.get_active_teams()
        
        if not active_teams:
            raise ValueError("Nenhuma equipe ativa disponível")
        
        return random.choice(active_teams)
    
    def _priority_distribution(self) -> TeamInfo:
        """Distribuição baseada em prioridade"""
        active_teams = self.get_active_teams()
        
        if not active_teams:
            raise ValueError("Nenhuma equipe ativa disponível")
        
        # Agrupa por prioridade
        priority_groups = {}
        for team in active_teams:
            if team.priority not in priority_groups:
                priority_groups[team.priority] = []
            priority_groups[team.priority].append(team)
        
        # Pega grupo de maior prioridade (menor número)
        highest_priority = min(priority_groups.keys())
        priority_teams = priority_groups[highest_priority]
        
        # Round robin dentro do grupo de prioridade
        return priority_teams[self.current_index % len(priority_teams)]
    
    def get_next_team(self, lead_info: Dict) -> TeamInfo:
        """Determina próxima equipe para receber o lead"""
        
        # Lógica especial baseada em localização
        location = lead_info.get("location", "").lower()
        if "ponta grossa" in location:
            # Direciona leads de Ponta Grossa para equipe específica
            ponta_grossa_team = next(
                (team for team in self.teams if "ponta grossa" in team.name.lower()),
                None
            )
            if ponta_grossa_team and ponta_grossa_team.active:
                logger.info(f"Lead direcionado para Ponta Grossa por localização")
                return ponta_grossa_team
        
        # Distribuição normal baseada no método configurado
        if self.distribution_method == "round_robin":
            team = self._round_robin_distribution()
        elif self.distribution_method == "random":
            team = self._random_distribution()
        elif self.distribution_method == "priority":
            team = self._priority_distribution()
        else:
            # Fallback para round robin
            team = self._round_robin_distribution()
        
        # Salva estado e atualiza stats
        self.last_distribution = datetime.now().isoformat()
        self._save_queue_state()
        self._update_stats(team, lead_info)
        
        logger.info(f"Lead distribuído para: {team.name} ({self.distribution_method})")
        
        return team
    
    def get_distribution_stats(self, days: int = 7) -> Dict:
        """Retorna estatísticas de distribuição dos últimos N dias"""
        try:
            if not os.path.exists(self.stats_file):
                return {}
            
            with open(self.stats_file, 'r') as f:
                all_stats = json.load(f)
            
            # Filtra últimos N dias
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            filtered_stats = {}
            for date_str, day_stats in all_stats.items():
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if start_date <= date_obj <= end_date:
                    filtered_stats[date_str] = day_stats
            
            return filtered_stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def set_team_active(self, company_id: str, active: bool):
        """Ativa/desativa uma equipe"""
        for team in self.teams:
            if team.company_id == company_id:
                team.active = active
                logger.info(f"Equipe {team.name} {'ativada' if active else 'desativada'}")
                break
    
    def get_team_by_company_id(self, company_id: str) -> Optional[TeamInfo]:
        """Busca equipe pelo company_id"""
        return next((team for team in self.teams if team.company_id == company_id), None)