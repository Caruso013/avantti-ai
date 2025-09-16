from abc import ABC, abstractmethod


class ICalendar(ABC):
    @abstractmethod
    def get_events(self):
        pass

    @abstractmethod
    def create_event(self, event: dict):
        pass
