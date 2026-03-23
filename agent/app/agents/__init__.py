from app.agents.base import BaseAgent
from app.agents.generalist import GeneralistAgent
from app.agents.port_manager import PortManagerAgent
from app.agents.luxonis_expert import LuxonisExpertAgent
from app.agents.ml_expert import MLExpertAgent
from app.agents.devops_expert import DevOpsExpertAgent

__all__ = [
    "BaseAgent",
    "GeneralistAgent",
    "PortManagerAgent",
    "LuxonisExpertAgent",
    "MLExpertAgent",
    "DevOpsExpertAgent",
]

DOMAIN_AGENT_MAP: dict[str, type[BaseAgent]] = {
    "general": GeneralistAgent,
    "network": PortManagerAgent,
    "luxonis": LuxonisExpertAgent,
    "ml": MLExpertAgent,
    "devops": DevOpsExpertAgent,
}


def get_agent_for_domain(domain: str) -> type[BaseAgent]:
    return DOMAIN_AGENT_MAP.get(domain, GeneralistAgent)
