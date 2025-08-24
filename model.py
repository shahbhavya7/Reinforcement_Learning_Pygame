import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module): # inherits from nn.Module of torch
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__() # call the constructor of the parent class nn.Module
        self.linear1 = nn.Linear(input_size, hidden_size) # define a fully connected layer from input_size to hidden_size
        self.linear2 = nn.Linear(hidden_size, output_size) # define a fully connected layer from hidden_size to output_size

    def forward(self, x): # use the layers defined in __init__ to forward propagate the input x through the network
        x = F.relu(self.linear1(x)) # apply ReLU activation function after the first layer
        x = self.linear2(x) # output layer without activation function (for regression tasks)
        return x # return the output of the network

    def save(self, file_name='model.pth'): # save the model parameters to a file
        model_folder_path = './model' # folder to save the model
        if not os.path.exists(model_folder_path): # if the folder does not exist, create it
            os.makedirs(model_folder_path) # create the folder

        file_name = os.path.join(model_folder_path, file_name) # full path to the file
        torch.save(self.state_dict(), file_name) # save the model parameters to the file
 

class QTrainer: # class to train the Q-learning model for the snake game, Q-learning is a reinforcement learning algorithm using deep learning
    def __init__(self, model, lr, gamma): # initialize the trainer with the model, learning rate and discount factor
        self.lr = lr # learning rate
        self.gamma = gamma # discount factor i.e. how much future rewards are discounted means future rewards are less important than immediate rewards
        self.model = model # the model to be trained
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr) # Adam optimizer to update the weights of the model
        self.criterion = nn.MSELoss() # Mean Squared Error loss function to calculate the loss between predicted and target Q values

    def train_step(self, state, action, reward, next_state, done): # train the model for one step using the given state, action, reward, next state and done status
        state = torch.tensor(state, dtype=torch.float) # convert state to a torch tensor of type float
        next_state = torch.tensor(next_state, dtype=torch.float) # convert next_state to a torch tensor of type float
        action = torch.tensor(action, dtype=torch.long) # convert action to a torch tensor of type long (integer)
        reward = torch.tensor(reward, dtype=torch.float) # convert reward to a torch tensor of type float
        # (n, x)

        if len(state.shape) == 1: # if state is a single sample, i.e. has only one dimension 
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # 1: predicted Q values with current state
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new
    
        # 2: Q_new = r + y * max(next_predicted Q value) -> only do this if not done
        # pred.clone()
        # preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()


