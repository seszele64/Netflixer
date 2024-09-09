from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem, Popularity

class UserAgentGenerator:
    def __init__(self):
        software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]
        popularity = [Popularity.POPULAR.value, Popularity.COMMON.value]

        self.user_agent_rotator = UserAgent(
            software_names=software_names,
            operating_systems=operating_systems,
            popularity=popularity,
            limit=100
        )

    def get_random_user_agent(self):
        return self.user_agent_rotator.get_random_user_agent()

    def get_user_agents(self):
        return self.user_agent_rotator.get_user_agents()
