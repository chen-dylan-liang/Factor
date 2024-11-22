import torch
import torch.nn as nn
import lightning as pl
import torch.optim as optim


class FeedForwardModel(pl.LightningModule):
    def __init__(self, input_dim, hidden_dim, output_dim, learning_rate=0.001):
        super(FeedForwardModel, self).__init__()
        self.save_hyperparameters()

        # Define network layers
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
        self.relu = nn.ReLU()

        # Define loss
        self.criterion = nn.MSELoss()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def training_step(self, batch, batch_idx):
        inputs, targets = batch
        outputs = self(inputs)
        loss = self.criterion(outputs, targets)
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        inputs, targets = batch
        outputs = self(inputs)
        val_loss = self.criterion(outputs, targets)
        self.log("val_loss", val_loss, prog_bar=True)
        return val_loss

    def test_step(self, batch, batch_idx):
        inputs, targets = batch
        outputs = self(inputs)
        test_loss = self.criterion(outputs, targets)
        self.log("test_loss", test_loss)
        return test_loss

    def configure_optimizers(self):
        return optim.Adam(self.parameters(), lr=self.hparams.learning_rate)