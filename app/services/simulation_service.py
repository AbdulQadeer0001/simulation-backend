from app.simulation.single_server import (
    SingleServerSimulation,
)

from app.simulation.multi_server import (
    MultiServerSimulation,
)


class SimulationService:

    @staticmethod
    def run_single_server(customers):

        simulation = SingleServerSimulation(
            customers
        )

        return simulation.run()

    @staticmethod
    def run_multi_server(
        customers,
        server_count
    ):

        simulation = MultiServerSimulation(
            customers,
            server_count
        )

        return simulation.run()