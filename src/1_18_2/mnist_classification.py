import argparse

import pytorch_lightning as pl
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchmetrics
import torchvision
from torch.utils.data import DataLoader


class MLP(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 10)

        self.train_acc = torchmetrics.Accuracy(task='multiclass', num_classes=10)
        self.val_acc = torchmetrics.Accuracy(task='multiclass', num_classes=10)

    def forward(self, inputs):
        x = F.relu(self.fc1(inputs.view(inputs.shape[0], 784)))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
        return optimizer

    def training_step(self, train_batch, batch_idx):
        x, y_true = train_batch
        y_pred = self.forward(x)
        loss = F.cross_entropy(y_pred, y_true)
        y_pred_label = torch.argmax(y_pred, dim=-1)
        acc = self.train_acc(y_pred_label, y_true)
        self.log("train_loss", loss, prog_bar=False, logger=True)
        self.log("train_acc", acc, prog_bar=True, logger=True)
        return loss

    def validation_step(self, val_batch, batch_idx):
        x, y_true = val_batch
        y_pred = self.forward(x)
        loss = F.cross_entropy(y_pred, y_true)
        y_pred_label = torch.argmax(y_pred, dim=-1)
        acc = self.val_acc(y_pred_label, y_true)
        self.log("val_loss", loss, prog_bar=False, logger=True)
        self.log("val_acc", acc, prog_bar=True, logger=True)


class MNISTModule(pl.LightningDataModule):
    def __init__(self, opt):
        super().__init__()
        self.opt = opt

    def prepare_data(self):
        self.train_dataset = torchvision.datasets.MNIST(
            self.opt.data_dir,
            train=True,
            download=True,
            transform=torchvision.transforms.ToTensor()
        )
        self.val_dataset = torchvision.datasets.MNIST(
            self.opt.data_dir,
            train=False,
            download=True,
            transform=torchvision.transforms.ToTensor()
        )

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=256, num_workers=4, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=256, num_workers=4, shuffle=False)


def main(opt):
    model = MLP()
    mnist = MNISTModule(opt)

    # Model saving
    ckpt = pl.callbacks.ModelCheckpoint(
        monitor="val_acc",
        dirpath=opt.ckpt_dir,
        filename="mnist-{epoch:03d}-{val_acc:.4f}",
        save_top_k=3,
        mode="max"
    )

    if opt.gpus == 0:
        train_flag = {"accelerator": "cpu"}
    elif opt.gpus > 0:
        train_flag = {"accelerator": "gpu", "devices": opt.gpus}

    trainer = pl.Trainer(max_epochs=20, callbacks=[ckpt], **train_flag)
    trainer.fit(model, mnist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MNIST Training")
    parser.add_argument("--data_dir", type=str, default="./data")
    parser.add_argument("--ckpt_dir", type=str, default="./ckpt")
    # 0-> CPU, 1 -> use 1 gpu
    parser.add_argument("--gpus", type=int, default=0)

    opt = parser.parse_args()

    main(opt)
