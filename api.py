import torch
from tqdm import trange
import ray
from utils import _evaluate_ray, _evaluate


class FedAlgorithm(object):
    def __init__(self,
                 init_model,
                 client_dataloaders,
                 loss,
                 logger,
                 config,
                 device
                 ):
        self.client_dataloaders = client_dataloaders
        self.loss = loss
        self.logger = logger
        self.config = config
        self.device = device
        self.server_state = self.server_init(init_model)
        self.client_states = [self.client_init(self.server_state, client_dataloader) for client_dataloader in
                              self.client_dataloaders]

    def step(self, server_state, client_states, weights):
        # server_state contains the (global) model, (global) auxiliary variables, weights of clients
        # client_states contain the (local) auxiliary variables

        # sample active clients
        active_ids = torch.randperm(self.config.n_workers)[:self.config.n_workers_per_round].tolist()

        client_states = self.clients_step(client_states, active_ids)

        # aggregate
        server_state = self.server_step(server_state, client_states, weights, active_ids)

        # broadcast
        client_states = self.clients_update(server_state, client_states, active_ids)

        return server_state, client_states

    def fit(self, weights, n_rounds=None):
        if n_rounds is None:
            n_rounds = self.config.n_global_rounds

        for round in trange(n_rounds):
            self.server_state, self.client_states = self.step(self.server_state, self.client_states, weights)
            if round % self.config.eval_freq == 0 and self.logger is not None:
                self.logger.log(round, self.server_state.model)

    # def reset_states(self):
    #     self.server_state = self.server_init()
    #     self.client_states = [self.client_init(self.server_state, client_dataloader) for client_dataloader in
    #                           self.client_dataloaders]

    def server_init(self, init_model):
        raise NotImplementedError

    def client_init(self, server_state, client_dataloader):
        raise NotImplementedError

    def clients_step(self, clients_state, active_ids):
        raise NotImplementedError

    def server_step(self, server_state, client_states, weights, active_ids):
        raise NotImplementedError

    def clients_update(self, server_state, clients_state, active_ids):
        raise NotImplementedError

    def clients_evaluate(self, active_ids=None):
        if active_ids is None:
            active_ids = list(range(len(self.client_states)))

        active_clients = zip([self.client_states[i] for i in active_ids],
                             [self.client_dataloaders[i] for i in active_ids])
        if self.config.use_ray:
            clients_loss = ray.get([_evaluate_ray.remote(self.loss, self.device, client_state.model, client_dataloader)
                                    for client_state, client_dataloader in active_clients])
        else:
            clients_loss = [_evaluate(self.loss, self.device, client_state.model, client_dataloader)
                            for client_state, client_dataloader in active_clients]
        return clients_loss


class PrimalDualFedAlgorithm(object):
    # augment FedAlgorithm with additional dual updates
    def __init__(self, primal_fed_algorithm: FedAlgorithm, config, logger):
        self.config = config
        self.logger = logger
        # logger logs testing metrics of the current model
        self.primal_fed_algorithm = primal_fed_algorithm
        # self.primal_fed_algorithm is used to update the primal variable
        self.server_state = self.server_init()
        # server_state contains the primal and dual variables

    def fit(self):
        for round in trange(self.config.n_pd_rounds):
            self.step()
            if self.logger is not None:
                self.logger.log(round * self.config.n_p_steps, self.server_state.model)

    def step(self):
        # update self.server_state
        raise NotImplementedError

    def server_init(self):
        # should utilize self.primal_fed_algorithm
        raise NotImplementedError



