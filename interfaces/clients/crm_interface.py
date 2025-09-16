from abc import ABC, abstractmethod


class ICRM(ABC):
    @abstractmethod
    def create_deal(
        self, company_name: str, lead_name: str, phone: str, motivation: str
    ) -> dict:
        pass

    @abstractmethod
    def create_activity(
        self, deal_id: int, subject: str, due_date: str, due_time: str
    ) -> bool:
        pass

    @abstractmethod
    def move_deal_to_scheduled_meeting(self, deal_id: int) -> bool:
        pass
