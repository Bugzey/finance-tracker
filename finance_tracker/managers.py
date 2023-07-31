"""
Application logic - managers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy.orm import (
    Session,
)

from finance_tracker.models import (
    BaseModel,
)


@dataclass
class BaseManager(ABC):
    sess: Session

    @property
    @abstractmethod
    def model(self) -> BaseModel:
        pass

    def get(self, id: int) -> BaseModel:
        return self.sess.get(self.model, id)

    def create(self, data: dict) -> BaseModel:
        pass


class ApplicationManager(BaseManager):
    pass
