import pytorch_lightning as pl
from Tactor.model import FeedForwardModel
from Tactor.dataloader import TrajectoryDataset
import torch
from torch.utils.data import DataLoader
import glob

def main():
    # Configuration
    data_dir = "./data"
    batch_size = 32
    num_epochs = 1000
    seq_length = 10 # Number of future actions to predict
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Initialize dataset and dataloader
    all_file_paths = sorted(glob.glob(f"{data_dir}/*.traj"))
    train_files = all_file_paths[:35]
    val_files = all_file_paths[35:45]
    test_files = all_file_paths[45:]
    
    train_dataset = TrajectoryDataset(train_files, seq_length=seq_length)
    val_dataset = TrajectoryDataset(val_files, seq_length=seq_length)
    test_dataset = TrajectoryDataset(test_files, seq_length=seq_length)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize model
    input_dim = 12  # 6 position + 6 force features
    hidden_dim = 128
    output_dim = seq_length * 6  # seq_length timesteps * 6 features
    
    model = FeedForwardModel(input_dim, hidden_dim, output_dim)
    
    # Initialize trainer with validation and test evaluation
    trainer = pl.Trainer(
        max_epochs=num_epochs, 
        accelerator="gpu" if torch.cuda.is_available() else "cpu", 
        log_every_n_steps=10
    )
    
    # Train and validate the model
    trainer.fit(model, train_dataloaders=train_loader, val_dataloaders=val_loader)
    
    # Test the model
    trainer.test(model, dataloaders=test_loader)

    # Save the trained model
    trainer.save_checkpoint("model.ckpt")

if __name__ == "__main__":
    main()