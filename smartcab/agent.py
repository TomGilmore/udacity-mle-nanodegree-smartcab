import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'black'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        
        # TODO: Initialize any additional variables here
        self.q_dict = {}
        self.alpha_learning_rate = 0.50
        self.gamma_discount_factor = 0.25
        self.epsilon_exploration_rate = 0.10
        self.possible_actions = [None, 'forward', 'left', 'right']
        
    def reset(self, destination=None):
        self.planner.route_to(destination)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = {"light": inputs["light"], "oncoming": inputs["oncoming"], "left": inputs["left"], "direction": self.next_waypoint}
        
        # TODO: Select action according to your policy
        #action = random.choice(self.possible_actions)
        action = self.select_agent_action(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.update_q(self.state, action, reward)
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]

    def select_agent_action(self, state):
        next_action = None
        best_q = 0
        
        ''' Added for random exploration per review comments
            ------------------------------------------------ '''
        if self.epsilon_exploration_rate > random.random():
            self.epsilon_exploration_rate -= 0.001
            return random.choice(self.possible_actions)
            
        for choice in self.possible_actions:
            q_value = self.return_q(state, choice)
            if q_value > best_q:
                next_action = choice
                best_q = q_value
            elif q_value == best_q:
                #next_action = random.choice(self.possible_actions)
                next_action = random.choice([next_action, choice])
        return next_action

    def return_q(self, state, action):
        index = "{}:{}:{}:{}:{}".format(state["light"], state["direction"], state["oncoming"], state["left"], action)
        if index in self.q_dict:
            return self.q_dict[index]
        return 0
        
    def update_q(self, state, action, reward):
        self.next_waypoint = self.planner.next_waypoint()
        q = self.return_q(state, action)
        inputs = self.env.sense(self)
        updated_state = {"light": inputs["light"], "oncoming": inputs["oncoming"], "left": inputs["left"], "direction": self.next_waypoint}
        state_utility = reward + (self.gamma_discount_factor * self.return_q_max(updated_state))
        new_q_value = q + (self.alpha_learning_rate * (state_utility - q))
        index = "{}:{}:{}:{}:{}".format(state["light"], state["direction"], state["oncoming"], state["left"], action)
        self.q_dict[index] = new_q_value

    def return_q_max(self, state):
        max_value = None
        for action in self.possible_actions:
            cur_value = self.return_q(state, action)
            if max_value is None or cur_value > max_value:
                max_value = cur_value
        return max_value

        
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.01, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line
    
    # Note: I needed to add these variables to my environment.py file
    print "\n----- RESULTS -----\n"
    print "Successes: {}".format(e.successes)
    print "Failures: {}".format(e.failures)
    print "Invalid Moves: {}".format(e.invalids)


if __name__ == '__main__':
    run()
