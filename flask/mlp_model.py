import torch
class MLPModel(torch.nn.Module):

    def __init__(self, init_shape, num_classes):
        super(MLPModel, self).__init__()

        self.linear1 = torch.nn.Linear(init_shape, 200)
        self.linear2 = torch.nn.Linear(200, 150)
        self.linear3 = torch.nn.Linear(150, num_classes)
        self.activation = torch.nn.ReLU()
        self.softmax = torch.nn.Softmax()
        self.dropout = torch.nn.Dropout(p=0.2)

    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear3(x)
        x = self.softmax(x)
        return x

