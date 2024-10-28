import torch
from torch.utils.data import Dataset
import glob
import numpy as np
import logging
from typing import Tuple, List

class TrajectoryDataset(Dataset):
    def __init__(self, file_paths: List[str], seq_length: int = 10):
        """
        Args:
            file_paths (List[str]): List of file paths for the dataset split
            seq_length (int): Number of future timesteps to predict
        """
        self.file_paths = file_paths
        self.seq_length = seq_length
        self.data = []
        self._load_and_process_data()
    
    def _load_and_process_data(self):
        """Loads all data files and generates input/target pairs."""
        for file_path in self.file_paths:
            data = np.load(file_path, allow_pickle=True)
            pos_data = torch.tensor(data['pos_data'], dtype=torch.float32)  # (500, 6)
            ext_f_data = torch.tensor(data['ext_f_data'], dtype=torch.float32)  # (500, 6)
            
            # Combine position and force data along the last dimension
            inputs = torch.cat((pos_data, ext_f_data), dim=1)  # (500, 12)

            # Generate all possible input/target pairs within this episode
            for start_idx in range(inputs.shape[0] - self.seq_length):
                current_state = inputs[start_idx]  # (12,)
                future_positions = pos_data[start_idx + 1 : start_idx + 1 + self.seq_length]  # (seq_length, 6)
                target = future_positions.reshape(-1)  # Flatten to (seq_length * 6,)
                
                # Store as tuple in self.data
                self.data.append((current_state, target))
        
        logging.info(f"Generated {len(self.data)} input/target pairs from {len(self.file_paths)} files.")

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.data[idx]