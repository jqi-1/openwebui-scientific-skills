---
name: pytorch-lightning
description: Deep learning framework (PyTorch Lightning / lightning package). Organize PyTorch code into LightningModules, configure Trainers for multi-GPU/TPU, implement data pipelines, callbacks, logging (W&B, TensorBoard, MLflow), distributed training (DDP, FSDP, DeepSpeed), for scalable neural network training.
---

# PyTorch Lightning

## Overview

PyTorch Lightning is a deep learning framework that organizes PyTorch code to eliminate boilerplate while maintaining full flexibility. Automate training workflows, multi-device orchestration, and implement best practices for neural network training and scaling across multiple GPUs/TPUs.

**Current upstream:** lightning 2.6.4 (PyPI, May 2026). Docs: [lightning.ai/docs/pytorch/stable](https://lightning.ai/docs/pytorch/stable/). Use `import lightning as L` (the `pytorch-lightning` package name still installs the same library).

## Installation

```bash
uv pip install lightning
```

Optional extras:

```bash
uv pip install lightning[extra]    # loggers, strategies, etc.
uv pip install wandb mlflow        # specific loggers as needed
```

## When to Use This Skill

This skill should be used when:
- Building, training, or deploying neural networks using PyTorch Lightning
- Organizing PyTorch code into LightningModules
- Configuring Trainers for multi-GPU/TPU training
- Implementing data pipelines with LightningDataModules
- Working with callbacks, logging, and distributed training strategies (DDP, FSDP, DeepSpeed)
- Structuring deep learning projects professionally

## Core Capabilities

### 1. LightningModule - Model Definition

Organize PyTorch models into six logical sections:

1. **Initialization** - `__init__()` and `setup()`
2. **Training Loop** - `training_step(batch, batch_idx)`
3. **Validation Loop** - `validation_step(batch, batch_idx)`
4. **Test Loop** - `test_step(batch, batch_idx)`
5. **Prediction** - `predict_step(batch, batch_idx)`
6. **Optimizer Configuration** - `configure_optimizers()`

**Quick template reference:** See `scripts/template_lightning_module.py` for a complete boilerplate.

**Detailed documentation:** Read `references/lightning_module.md` for comprehensive method documentation, hooks, properties, and best practices.

### 2. Trainer - Training Automation

The Trainer automates the training loop, device management, gradient operations, and callbacks. Key features:

- Multi-GPU/TPU support with strategy selection (DDP, FSDP, DeepSpeed)
- Automatic mixed precision training
- Gradient accumulation and clipping
- Checkpointing and early stopping
- Progress bars and logging

**Quick setup reference:** See `scripts/quick_trainer_setup.py` for common Trainer configurations.

**Detailed documentation:** Read `references/trainer.md` for all parameters, methods, and configuration options.

### 3. LightningDataModule - Data Pipeline Organization

Encapsulate all data processing steps in a reusable class:

1. `prepare_data()` - Download and process data (single-process)
2. `setup()` - Create datasets and apply transforms (per-GPU)
3. `train_dataloader()` - Return training DataLoader
4. `val_dataloader()` - Return validation DataLoader
5. `test_dataloader()` - Return test DataLoader

**Quick template reference:** See `scripts/template_datamodule.py` for a complete boilerplate.

**Detailed documentation:** Read `references/data_module.md` for method details and usage patterns.

### 4. Callbacks - Extensible Training Logic

Add custom functionality at specific training hooks without modifying your LightningModule. Built-in callbacks include:

- **ModelCheckpoint** - Save best/latest models
- **EarlyStopping** - Stop when metrics plateau
- **LearningRateMonitor** - Track LR scheduler changes
- **BatchSizeFinder** - Auto-determine optimal batch size

**Detailed documentation:** Read `references/callbacks.md` for built-in callbacks and custom callback creation.

### 5. Logging - Experiment Tracking

Integrate with multiple logging platforms:

- TensorBoard (default)
- Weights & Biases (WandbLogger)
- MLflow (MLFlowLogger)
- Comet (CometLogger)
- CSV (CSVLogger)

Note: `NeptuneLogger` was removed in lightning 2.6.4. Use W&B, MLflow, or TensorBoard instead.

Log metrics using `self.log("metric_name", value)` in any LightningModule method.

**Detailed documentation:** Read `references/logging.md` for logger setup and configuration.

### 6. Distributed Training - Scale to Multiple Devices

Choose the right strategy based on model size:

- **DDP** - For models <500M parameters (ResNet, smaller transformers)
- **FSDP** - For models 500M+ parameters (large transformers, recommended for Lightning users)
- **DeepSpeed** - For cutting-edge features and fine-grained control

Configure with: `Trainer(strategy="ddp", accelerator="gpu", devices=4)`

**Detailed documentation:** Read `references/distributed_training.md` for strategy comparison and configuration.

### 7. Best Practices

- Device agnostic code - Use `self.device` instead of `.cuda()`
- Hyperparameter saving - Use `self.save_hyperparameters()` in `__init__()`
- Metric logging - Use `self.log()` for automatic aggregation across devices
- Reproducibility - Use `seed_everything()` and `Trainer(deterministic=True)`
- Debugging - Use `Trainer(fast_dev_run=True)` to test with 1 batch

**Detailed documentation:** Read `references/best_practices.md` for common patterns and pitfalls.

## Quick Workflow

1. **Define model:**
   ```python
   class MyModel(L.LightningModule):
       def __init__(self):
           super().__init__()
           self.save_hyperparameters()
           self.model = YourNetwork()

       def training_step(self, batch, batch_idx):
           x, y = batch
           loss = F.cross_entropy(self.model(x), y)
           self.log("train_loss", loss)
           return loss

       def configure_optimizers(self):
           return torch.optim.Adam(self.parameters())
   ```

2. **Prepare data:**
   ```python
   # Option 1: Direct DataLoaders
   train_loader = DataLoader(train_dataset, batch_size=32)

   # Option 2: LightningDataModule (recommended for reusability)
   dm = MyDataModule(batch_size=32)
   ```

3. **Train:**
   ```python
   trainer = L.Trainer(max_epochs=10, accelerator="gpu", devices=2)
   trainer.fit(model, train_loader)  # or trainer.fit(model, datamodule=dm)
   ```

## Resources

### scripts/
Executable Python templates for common PyTorch Lightning patterns:

- `template_lightning_module.py` - Complete LightningModule boilerplate
- `template_datamodule.py` - Complete LightningDataModule boilerplate
- `quick_trainer_setup.py` - Common Trainer configuration examples

### references/
Detailed documentation for each PyTorch Lightning component:

- `lightning_module.md` - Comprehensive LightningModule guide (methods, hooks, properties)
- `trainer.md` - Trainer configuration and parameters
- `data_module.md` - LightningDataModule patterns and methods
- `callbacks.md` - Built-in and custom callbacks
- `logging.md` - Logger integrations and usage
- `distributed_training.md` - DDP, FSDP, DeepSpeed comparison and setup
- `best_practices.md` - Common patterns, tips, and pitfalls

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pytorch-lightning/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/best_practices.md`

# Best Practices - PyTorch Lightning

## Code Organization

### 1. Separate Research from Engineering

**Good:**
```python
class MyModel(L.LightningModule):
    # Research code (what the model does)
    def training_step(self, batch, batch_idx):
        loss = self.compute_loss(batch)
        return loss

# Engineering code (how to train) - in Trainer
trainer = L.Trainer(
    max_epochs=100,
    accelerator="gpu",
    devices=4,
    strategy="ddp"
)
```

**Bad:**
```python
# Mixing research and engineering logic
class MyModel(L.LightningModule):
    def training_step(self, batch, batch_idx):
        loss = self.compute_loss(batch)

        # Don't do device management manually
        loss = loss.cuda()

        # Don't do optimizer steps manually (unless manual optimization)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss
```

### 2. Use LightningDataModule

**Good:**
```python
class MyDataModule(L.LightningDataModule):
    def __init__(self, data_dir, batch_size):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size

    def prepare_data(self):
        # Download data once
        download_data(self.data_dir)

    def setup(self, stage):
        # Load data per-process
        self.train_dataset = MyDataset(self.data_dir, split='train')
        self.val_dataset = MyDataset(self.data_dir, split='val')

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)

# Reusable and shareable
dm = MyDataModule("./data", batch_size=32)
trainer.fit(model, datamodule=dm)
```

**Bad:**
```python
# Scattered data logic
train_dataset = load_data()
val_dataset = load_data()
train_loader = DataLoader(train_dataset, ...)
val_loader = DataLoader(val_dataset, ...)
trainer.fit(model, train_loader, val_loader)
```

### 3. Keep Models Modular

```python
class Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(...)

    def forward(self, x):
        return self.layers(x)

class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(...)

    def forward(self, x):
        return self.layers(x)

class MyModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.encoder = Encoder()
        self.decoder = Decoder()

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)
```

## Device Agnosticism

### 1. Never Use Explicit CUDA Calls

**Bad:**
```python
x = x.cuda()
model = model.cuda()
torch.cuda.set_device(0)
```

**Good:**
```python
# Inside LightningModule
x = x.to(self.device)

# Or let Lightning handle it automatically
def training_step(self, batch, batch_idx):
    x, y = batch  # Already on correct device
    return loss
```

### 2. Use `self.device` Property

```python
class MyModel(L.LightningModule):
    def training_step(self, batch, batch_idx):
        # Create tensors on correct device
        noise = torch.randn(batch.size(0), 100).to(self.device)

        # Or use type_as
        noise = torch.randn(batch.size(0), 100).type_as(batch)
```

### 3. Register Buffers for Non-Parameters

```python
class MyModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        # Register buffers (automatically moved to correct device)
        self.register_buffer("running_mean", torch.zeros(100))

    def forward(self, x):
        # self.running_mean is automatically on correct device
        return x - self.running_mean
```

## Hyperparameter Management

### 1. Always Use `save_hyperparameters()`

**Good:**
```python
class MyModel(L.LightningModule):
    def __init__(self, learning_rate, hidden_dim, dropout):
        super().__init__()
        self.save_hyperparameters()  # Saves all arguments

        # Access via self.hparams
        self.model = nn.Linear(self.hparams.hidden_dim, 10)

# Load from checkpoint with saved hparams
model = MyModel.load_from_checkpoint("checkpoint.ckpt")
print(model.hparams.learning_rate)  # Original value preserved
```

**Bad:**
```python
class MyModel(L.LightningModule):
    def __init__(self, learning_rate, hidden_dim, dropout):
        super().__init__()
        self.learning_rate = learning_rate  # Manual tracking
        self.hidden_dim = hidden_dim
```

### 2. Ignore Specific Arguments

```python
class MyModel(L.LightningModule):
    def __init__(self, lr, model, dataset):
        super().__init__()
        # Don't save 'model' and 'dataset' (not serializable)
        self.save_hyperparameters(ignore=['model', 'dataset'])

        self.model = model
        self.dataset = dataset
```

### 3. Use Hyperparameters in `configure_optimizers()`

```python
def configure_optimizers(self):
    # Use saved hyperparameters
    optimizer = torch.optim.Adam(
        self.parameters(),
        lr=self.hparams.learning_rate,
        weight_decay=self.hparams.weight_decay
    )
    return optimizer
```

## Logging Best Practices

### 1. Log Both Step and Epoch Metrics

```python
def training_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)

    # Log per-step for detailed monitoring
    # Log per-epoch for aggregated view
    self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)

    return loss
```

### 2. Use Structured Logging

```python
def training_step(self, batch, batch_idx):
    # Organize with prefixes
    self.log("train/loss", loss)
    self.log("train/acc", acc)
    self.log("train/f1", f1)

def validation_step(self, batch, batch_idx):
    self.log("val/loss", loss)
    self.log("val/acc", acc)
    self.log("val/f1", f1)
```

### 3. Sync Metrics in Distributed Training

```python
def validation_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)

    # IMPORTANT: sync_dist=True for proper aggregation across GPUs
    self.log("val_loss", loss, sync_dist=True)
```

### 4. Monitor Learning Rate

```python
from lightning.pytorch.callbacks import LearningRateMonitor

trainer = L.Trainer(
    callbacks=[LearningRateMonitor(logging_interval="step")]
)
```

## Reproducibility

### 1. Seed Everything

```python
import lightning as L

# Set seed for reproducibility
L.seed_everything(42, workers=True)

trainer = L.Trainer(
    deterministic=True,  # Use deterministic algorithms
    benchmark=False      # Disable cudnn benchmarking
)
```

### 2. Avoid Non-Deterministic Operations

```python
# Bad: Non-deterministic
torch.use_deterministic_algorithms(False)

# Good: Deterministic
torch.use_deterministic_algorithms(True)
```

### 3. Log Random State

```python
def on_save_checkpoint(self, checkpoint):
    # Save random states
    checkpoint['rng_state'] = {
        'torch': torch.get_rng_state(),
        'numpy': np.random.get_state(),
        'python': random.getstate()
    }

def on_load_checkpoint(self, checkpoint):
    # Restore random states
    if 'rng_state' in checkpoint:
        torch.set_rng_state(checkpoint['rng_state']['torch'])
        np.random.set_state(checkpoint['rng_state']['numpy'])
        random.setstate(checkpoint['rng_state']['python'])
```

## Debugging

### 1. Use `fast_dev_run`

```python
# Test with 1 batch before full training
trainer = L.Trainer(fast_dev_run=True)
trainer.fit(model, datamodule=dm)
```

### 2. Limit Training Data

```python
# Use only 10% of data for quick iteration
trainer = L.Trainer(
    limit_train_batches=0.1,
    limit_val_batches=0.1
)
```

### 3. Enable Anomaly Detection

```python
# Detect NaN/Inf in gradients
trainer = L.Trainer(detect_anomaly=True)
```

### 4. Overfit on Small Batch

```python
# Overfit on 10 batches to verify model capacity
trainer = L.Trainer(overfit_batches=10)
```

### 5. Profile Code

```python
# Find performance bottlenecks
trainer = L.Trainer(profiler="simple")  # or "advanced"
```

## Memory Optimization

### 1. Use Mixed Precision

```python
# FP16/BF16 mixed precision for memory savings and speed
trainer = L.Trainer(
    precision="16-mixed",   # V100, T4
    # or
    precision="bf16-mixed"  # A100, H100
)
```

### 2. Gradient Accumulation

```python
# Simulate larger batch size without memory increase
trainer = L.Trainer(
    accumulate_grad_batches=4  # Accumulate over 4 batches
)
```

### 3. Gradient Checkpointing

```python
class MyModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = transformers.AutoModel.from_pretrained("bert-base")

        # Enable gradient checkpointing
        self.model.gradient_checkpointing_enable()
```

### 4. Clear Cache

```python
def on_train_epoch_end(self):
    # Clear collected outputs to free memory
    self.training_step_outputs.clear()

    # Clear CUDA cache if needed
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
```

### 5. Use Efficient Data Types

```python
# Use appropriate precision
# FP32 for stability, FP16/BF16 for speed/memory

class MyModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        # Use bfloat16 for better numerical stability than fp16
        self.model = MyTransformer().to(torch.bfloat16)
```

## Training Stability

### 1. Gradient Clipping

```python
# Prevent gradient explosion
trainer = L.Trainer(
    gradient_clip_val=1.0,
    gradient_clip_algorithm="norm"  # or "value"
)
```

### 2. Learning Rate Warmup

```python
def configure_optimizers(self):
    optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)

    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=1e-2,
        total_steps=self.trainer.estimated_stepping_batches,
        pct_start=0.1  # 10% warmup
    )

    return {
        "optimizer": optimizer,
        "lr_scheduler": {
            "scheduler": scheduler,
            "interval": "step"
        }
    }
```

### 3. Monitor Gradients

```python
class MyModel(L.LightningModule):
    def on_after_backward(self):
        # Log gradient norms
        for name, param in self.named_parameters():
            if param.grad is not None:
                self.log(f"grad_norm/{name}", param.grad.norm())
```

### 4. Use EarlyStopping

```python
from lightning.pytorch.callbacks import EarlyStopping

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    mode="min",
    verbose=True
)

trainer = L.Trainer(callbacks=[early_stop])
```

## Checkpointing

### 1. Save Top-K and Last

```python
from lightning.pytorch.callbacks import ModelCheckpoint

checkpoint_callback = ModelCheckpoint(
    dirpath="checkpoints/",
    filename="{epoch}-{val_loss:.2f}",
    monitor="val_loss",
    mode="min",
    save_top_k=3,    # Keep best 3
    save_last=True   # Always save last for resuming
)

trainer = L.Trainer(callbacks=[checkpoint_callback])
```

### 2. Resume Training

```python
# Resume from last checkpoint
trainer.fit(model, datamodule=dm, ckpt_path="last.ckpt")

# Resume from specific checkpoint
trainer.fit(model, datamodule=dm, ckpt_path="epoch=10-val_loss=0.23.ckpt")
```

### 3. Custom Checkpoint State

```python
def on_save_checkpoint(self, checkpoint):
    # Add custom state
    checkpoint['custom_data'] = self.custom_data
    checkpoint['epoch_metrics'] = self.metrics

def on_load_checkpoint(self, checkpoint):
    # Restore custom state
    self.custom_data = checkpoint.get('custom_data', {})
    self.metrics = checkpoint.get('epoch_metrics', [])
```

## Testing

### 1. Separate Train and Test

```python
# Train
trainer = L.Trainer(max_epochs=100)
trainer.fit(model, datamodule=dm)

# Test ONLY ONCE before publishing
trainer.test(model, datamodule=dm)
```

### 2. Use Validation for Model Selection

```python
# Use validation for hyperparameter tuning
checkpoint_callback = ModelCheckpoint(monitor="val_loss", mode="min")
trainer = L.Trainer(callbacks=[checkpoint_callback])
trainer.fit(model, datamodule=dm)

# Load best model
best_model = MyModel.load_from_checkpoint(checkpoint_callback.best_model_path)

# Test only once with best model
trainer.test(best_model, datamodule=dm)
```

## Code Quality

### 1. Type Hints

```python
from typing import Any, Dict, Tuple
import torch
from torch import Tensor

class MyModel(L.LightningModule):
    def training_step(self, batch: Tuple[Tensor, Tensor], batch_idx: int) -> Tensor:
        x, y = batch
        loss = self.compute_loss(x, y)
        return loss

    def configure_optimizers(self) -> Dict[str, Any]:
        optimizer = torch.optim.Adam(self.parameters())
        return {"optimizer": optimizer}
```

### 2. Docstrings

```python
class MyModel(L.LightningModule):
    """
    My awesome model for image classification.

    Args:
        num_classes: Number of output classes
        learning_rate: Learning rate for optimizer
        hidden_dim: Hidden dimension size
    """

    def __init__(self, num_classes: int, learning_rate: float, hidden_dim: int):
        super().__init__()
        self.save_hyperparameters()
```

### 3. Property Methods

```python
class MyModel(L.LightningModule):
    @property
    def learning_rate(self) -> float:
        """Current learning rate."""
        return self.hparams.learning_rate

    @property
    def num_parameters(self) -> int:
        """Total number of parameters."""
        return sum(p.numel() for p in self.parameters())
```

## Common Pitfalls

### 1. Forgetting to Return Loss

**Bad:**
```python
def training_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)
    self.log("train_loss", loss)
    # FORGOT TO RETURN LOSS!
```

**Good:**
```python
def training_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)
    self.log("train_loss", loss)
    return loss  # MUST return loss
```

### 2. Not Syncing Metrics in DDP

**Bad:**
```python
def validation_step(self, batch, batch_idx):
    self.log("val_acc", acc)  # Wrong value with multi-GPU!
```

**Good:**
```python
def validation_step(self, batch, batch_idx):
    self.log("val_acc", acc, sync_dist=True)  # Correct aggregation
```

### 3. Manual Device Management

**Bad:**
```python
def training_step(self, batch, batch_idx):
    x = x.cuda()  # Don't do this
    y = y.cuda()
```

**Good:**
```python
def training_step(self, batch, batch_idx):
    # Lightning handles device placement
    x, y = batch  # Already on correct device
```

### 4. Not Using `self.log()`

**Bad:**
```python
def training_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)
    self.training_losses.append(loss)  # Manual tracking
    return loss
```

**Good:**
```python
def training_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)
    self.log("train_loss", loss)  # Automatic logging
    return loss
```

### 5. Modifying Batch In-Place

**Bad:**
```python
def training_step(self, batch, batch_idx):
    x, y = batch
    x[:] = self.augment(x)  # In-place modification can cause issues
```

**Good:**
```python
def training_step(self, batch, batch_idx):
    x, y = batch
    x = self.augment(x)  # Create new tensor
```

## Performance Tips

### 1. Use DataLoader Workers

```python
def train_dataloader(self):
    return DataLoader(
        self.train_dataset,
        batch_size=32,
        num_workers=4,           # Use multiple workers
        pin_memory=True,         # Faster GPU transfer
        persistent_workers=True  # Keep workers alive
    )
```

### 2. Enable Benchmark Mode (if fixed input size)

```python
trainer = L.Trainer(benchmark=True)
```

### 3. Use Automatic Batch Size Finding

```python
from lightning.pytorch.tuner import Tuner

trainer = L.Trainer()
tuner = Tuner(trainer)

# Find optimal batch size
tuner.scale_batch_size(model, datamodule=dm, mode="power")

# Then train
trainer.fit(model, datamodule=dm)
```

### 4. Optimize Data Loading

```python
# Use faster image decoding
import torch
import torchvision.transforms as T

transforms = T.Compose([
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Use PIL-SIMD for faster image loading
# uv pip install pillow-simd
```

### `references/callbacks.md`

# Callbacks - Comprehensive Guide

## Overview

Callbacks enable adding arbitrary self-contained programs to training without cluttering your LightningModule research code. They execute custom logic at specific hooks during the training lifecycle.

## Architecture

Lightning organizes training logic across three components:
- **Trainer** - Engineering infrastructure
- **LightningModule** - Research code
- **Callbacks** - Non-essential functionality (monitoring, checkpointing, custom behaviors)

## Creating Custom Callbacks

Basic structure:

```python
from lightning.pytorch.callbacks import Callback

class MyCustomCallback(Callback):
    def on_train_start(self, trainer, pl_module):
        print("Training is starting!")

    def on_train_end(self, trainer, pl_module):
        print("Training is done!")

# Use with Trainer
trainer = L.Trainer(callbacks=[MyCustomCallback()])
```

## Built-in Callbacks

### ModelCheckpoint

Save models based on monitored metrics.

**Key Parameters:**
- `dirpath` - Directory to save checkpoints
- `filename` - Checkpoint filename pattern
- `monitor` - Metric to monitor
- `mode` - "min" or "max" for monitored metric
- `save_top_k` - Number of best models to keep
- `save_last` - Save last epoch checkpoint
- `every_n_epochs` - Save every N epochs
- `save_on_train_epoch_end` - Save at train epoch end vs validation end

**Examples:**
```python
from lightning.pytorch.callbacks import ModelCheckpoint

# Save top 3 models based on validation loss
checkpoint_callback = ModelCheckpoint(
    dirpath="checkpoints/",
    filename="model-{epoch:02d}-{val_loss:.2f}",
    monitor="val_loss",
    mode="min",
    save_top_k=3,
    save_last=True
)

# Save every 10 epochs
checkpoint_callback = ModelCheckpoint(
    dirpath="checkpoints/",
    filename="model-{epoch:02d}",
    every_n_epochs=10,
    save_top_k=-1  # Save all
)

# Save best model based on accuracy
checkpoint_callback = ModelCheckpoint(
    dirpath="checkpoints/",
    filename="best-model",
    monitor="val_acc",
    mode="max",
    save_top_k=1
)

trainer = L.Trainer(callbacks=[checkpoint_callback])
```

**Accessing Saved Checkpoints:**
```python
# Get best model path
best_model_path = checkpoint_callback.best_model_path

# Get last checkpoint path
last_checkpoint = checkpoint_callback.last_model_path

# Get all checkpoint paths
all_checkpoints = checkpoint_callback.best_k_models
```

### EarlyStopping

Stop training when a monitored metric stops improving.

**Key Parameters:**
- `monitor` - Metric to monitor
- `patience` - Number of epochs with no improvement after which training stops
- `mode` - "min" or "max" for monitored metric
- `min_delta` - Minimum change to qualify as an improvement
- `verbose` - Print messages
- `strict` - Crash if monitored metric not found

**Examples:**
```python
from lightning.pytorch.callbacks import EarlyStopping

# Stop when validation loss stops improving
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    mode="min",
    verbose=True
)

# Stop when accuracy plateaus
early_stop = EarlyStopping(
    monitor="val_acc",
    patience=5,
    mode="max",
    min_delta=0.001  # Must improve by at least 0.001
)

trainer = L.Trainer(callbacks=[early_stop])
```

### LearningRateMonitor

Track learning rate changes from schedulers.

**Key Parameters:**
- `logging_interval` - When to log: "step" or "epoch"
- `log_momentum` - Also log momentum values

**Example:**
```python
from lightning.pytorch.callbacks import LearningRateMonitor

lr_monitor = LearningRateMonitor(logging_interval="step")
trainer = L.Trainer(callbacks=[lr_monitor])

# Logs learning rate automatically as "lr-{optimizer_name}"
```

### DeviceStatsMonitor

Log device performance metrics (GPU/CPU/TPU).

**Key Parameters:**
- `cpu_stats` - Log CPU stats

**Example:**
```python
from lightning.pytorch.callbacks import DeviceStatsMonitor

device_stats = DeviceStatsMonitor(cpu_stats=True)
trainer = L.Trainer(callbacks=[device_stats])

# Logs: gpu_utilization, gpu_memory_usage, etc.
```

### ModelSummary / RichModelSummary

Display model architecture and parameter count.

**Example:**
```python
from lightning.pytorch.callbacks import ModelSummary, RichModelSummary

# Basic summary
summary = ModelSummary(max_depth=2)

# Rich formatted summary (prettier)
rich_summary = RichModelSummary(max_depth=3)

trainer = L.Trainer(callbacks=[rich_summary])
```

### Timer

Track and limit training duration.

**Key Parameters:**
- `duration` - Maximum training time (timedelta or dict)
- `interval` - Check interval: "step", "epoch", or "batch"

**Example:**
```python
from lightning.pytorch.callbacks import Timer
from datetime import timedelta

# Limit training to 1 hour
timer = Timer(duration=timedelta(hours=1))

# Or using dict
timer = Timer(duration={"hours": 23, "minutes": 30})

trainer = L.Trainer(callbacks=[timer])
```

### BatchSizeFinder

Automatically find the optimal batch size.

**Example:**
```python
from lightning.pytorch.callbacks import BatchSizeFinder

batch_finder = BatchSizeFinder(mode="power", steps_per_trial=3)

trainer = L.Trainer(callbacks=[batch_finder])
trainer.fit(model, datamodule=dm)

# Optimal batch size is set automatically
```

### GradientAccumulationScheduler

Schedule gradient accumulation steps dynamically.

**Example:**
```python
from lightning.pytorch.callbacks import GradientAccumulationScheduler

# Accumulate 4 batches for first 5 epochs, then 2 batches
accumulator = GradientAccumulationScheduler(scheduling={0: 4, 5: 2})

trainer = L.Trainer(callbacks=[accumulator])
```

### StochasticWeightAveraging (SWA)

Apply stochastic weight averaging for better generalization.

**Example:**
```python
from lightning.pytorch.callbacks import StochasticWeightAveraging

swa = StochasticWeightAveraging(swa_lrs=1e-2, swa_epoch_start=0.8)

trainer = L.Trainer(callbacks=[swa])
```

## Custom Callback Examples

### Simple Logging Callback

```python
class MetricsLogger(Callback):
    def __init__(self):
        self.metrics = []

    def on_validation_end(self, trainer, pl_module):
        # Access logged metrics
        metrics = trainer.callback_metrics
        self.metrics.append(dict(metrics))
        print(f"Validation metrics: {metrics}")
```

### Gradient Monitoring Callback

```python
class GradientMonitor(Callback):
    def on_after_backward(self, trainer, pl_module):
        # Log gradient norms
        for name, param in pl_module.named_parameters():
            if param.grad is not None:
                grad_norm = param.grad.norm().item()
                pl_module.log(f"grad_norm/{name}", grad_norm)
```

### Custom Checkpointing Callback

```python
class CustomCheckpoint(Callback):
    def __init__(self, save_dir):
        self.save_dir = save_dir

    def on_train_epoch_end(self, trainer, pl_module):
        epoch = trainer.current_epoch
        if epoch % 5 == 0:  # Save every 5 epochs
            filepath = f"{self.save_dir}/custom-{epoch}.ckpt"
            trainer.save_checkpoint(filepath)
            print(f"Saved checkpoint: {filepath}")
```

### Model Freezing Callback

```python
class FreezeUnfreeze(Callback):
    def __init__(self, freeze_until_epoch=10):
        self.freeze_until_epoch = freeze_until_epoch

    def on_train_epoch_start(self, trainer, pl_module):
        epoch = trainer.current_epoch

        if epoch < self.freeze_until_epoch:
            # Freeze backbone
            for param in pl_module.backbone.parameters():
                param.requires_grad = False
        else:
            # Unfreeze backbone
            for param in pl_module.backbone.parameters():
                param.requires_grad = True
```

### Learning Rate Finder Callback

```python
class LRFinder(Callback):
    def __init__(self, min_lr=1e-5, max_lr=1e-1, num_steps=100):
        self.min_lr = min_lr
        self.max_lr = max_lr
        self.num_steps = num_steps
        self.lrs = []
        self.losses = []

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if batch_idx >= self.num_steps:
            trainer.should_stop = True
            return

        # Exponential LR schedule
        lr = self.min_lr * (self.max_lr / self.min_lr) ** (batch_idx / self.num_steps)
        optimizer = trainer.optimizers[0]
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr

        self.lrs.append(lr)
        self.losses.append(outputs['loss'].item())

    def on_train_end(self, trainer, pl_module):
        # Plot LR vs Loss
        import matplotlib.pyplot as plt
        plt.plot(self.lrs, self.losses)
        plt.xscale('log')
        plt.xlabel('Learning Rate')
        plt.ylabel('Loss')
        plt.savefig('lr_finder.png')
```

### Prediction Saver Callback

```python
class PredictionSaver(Callback):
    def __init__(self, save_path):
        self.save_path = save_path
        self.predictions = []

    def on_predict_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        self.predictions.append(outputs)

    def on_predict_end(self, trainer, pl_module):
        # Save all predictions
        torch.save(self.predictions, self.save_path)
        print(f"Predictions saved to {self.save_path}")
```

## Available Hooks

### Setup and Teardown
- `setup(trainer, pl_module, stage)` - Called at beginning of fit/test/predict
- `teardown(trainer, pl_module, stage)` - Called at end of fit/test/predict

### Training Lifecycle
- `on_fit_start(trainer, pl_module)` - Called at start of fit
- `on_fit_end(trainer, pl_module)` - Called at end of fit
- `on_train_start(trainer, pl_module)` - Called at start of training
- `on_train_end(trainer, pl_module)` - Called at end of training

### Epoch Boundaries
- `on_train_epoch_start(trainer, pl_module)` - Called at start of training epoch
- `on_train_epoch_end(trainer, pl_module)` - Called at end of training epoch
- `on_validation_epoch_start(trainer, pl_module)` - Called at start of validation
- `on_validation_epoch_end(trainer, pl_module)` - Called at end of validation
- `on_test_epoch_start(trainer, pl_module)` - Called at start of test
- `on_test_epoch_end(trainer, pl_module)` - Called at end of test

### Batch Boundaries
- `on_train_batch_start(trainer, pl_module, batch, batch_idx)` - Before training batch
- `on_train_batch_end(trainer, pl_module, outputs, batch, batch_idx)` - After training batch
- `on_validation_batch_start(trainer, pl_module, batch, batch_idx)` - Before validation batch
- `on_validation_batch_end(trainer, pl_module, outputs, batch, batch_idx)` - After validation batch

### Gradient Events
- `on_before_backward(trainer, pl_module, loss)` - Before loss.backward()
- `on_after_backward(trainer, pl_module)` - After loss.backward()
- `on_before_optimizer_step(trainer, pl_module, optimizer)` - Before optimizer.step()

### Checkpoint Events
- `on_save_checkpoint(trainer, pl_module, checkpoint)` - When saving checkpoint
- `on_load_checkpoint(trainer, pl_module, checkpoint)` - When loading checkpoint

### Exception Handling
- `on_exception(trainer, pl_module, exception)` - When exception occurs

## State Management

For callbacks requiring persistence across checkpoints:

```python
class StatefulCallback(Callback):
    def __init__(self):
        self.counter = 0

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        self.counter += 1

    def state_dict(self):
        return {"counter": self.counter}

    def load_state_dict(self, state_dict):
        self.counter = state_dict["counter"]

    @property
    def state_key(self):
        # Unique identifier for this callback
        return "my_stateful_callback"
```

## Best Practices

### 1. Keep Callbacks Isolated
Each callback should be self-contained and independent:

```python
# Good: Self-contained
class MyCallback(Callback):
    def __init__(self):
        self.data = []

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        self.data.append(outputs['loss'].item())

# Bad: Depends on external state
global_data = []

class BadCallback(Callback):
    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        global_data.append(outputs['loss'].item())  # External dependency
```

### 2. Avoid Inter-Callback Dependencies
Callbacks should not depend on other callbacks:

```python
# Bad: Callback B depends on Callback A
class CallbackA(Callback):
    def __init__(self):
        self.value = 0

class CallbackB(Callback):
    def __init__(self, callback_a):
        self.callback_a = callback_a  # Tight coupling

# Good: Independent callbacks
class CallbackA(Callback):
    def __init__(self):
        self.value = 0

class CallbackB(Callback):
    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        # Access trainer state instead
        value = trainer.callback_metrics.get('metric')
```

### 3. Never Manually Invoke Callback Methods
Let Lightning call callbacks automatically:

```python
# Bad: Manual invocation
callback = MyCallback()
callback.on_train_start(trainer, model)  # Don't do this

# Good: Let Trainer handle it
trainer = L.Trainer(callbacks=[MyCallback()])
```

### 4. Design for Any Execution Order
Callbacks may execute in any order, so don't rely on specific ordering:

```python
# Good: Order-independent
class GoodCallback(Callback):
    def on_train_epoch_end(self, trainer, pl_module):
        # Use trainer state, not other callbacks
        metrics = trainer.callback_metrics
        self.log_metrics(metrics)
```

### 5. Use Callbacks for Non-Essential Logic
Keep core research code in LightningModule, use callbacks for auxiliary functionality:

```python
# Good separation
class MyModel(L.LightningModule):
    # Core research logic here
    def training_step(self, batch, batch_idx):
        return loss

# Non-essential monitoring in callback
class MonitorCallback(Callback):
    def on_validation_end(self, trainer, pl_module):
        # Monitoring logic
        pass
```

## Common Patterns

### Combining Multiple Callbacks

```python
from lightning.pytorch.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    LearningRateMonitor,
    DeviceStatsMonitor
)

callbacks = [
    ModelCheckpoint(monitor="val_loss", mode="min", save_top_k=3),
    EarlyStopping(monitor="val_loss", patience=10, mode="min"),
    LearningRateMonitor(logging_interval="step"),
    DeviceStatsMonitor()
]

trainer = L.Trainer(callbacks=callbacks)
```

### Conditional Callback Activation

```python
class ConditionalCallback(Callback):
    def __init__(self, activate_after_epoch=10):
        self.activate_after_epoch = activate_after_epoch

    def on_train_epoch_end(self, trainer, pl_module):
        if trainer.current_epoch >= self.activate_after_epoch:
            # Only active after specified epoch
            self.do_something(trainer, pl_module)
```

### Multi-Stage Training Callback

```python
class MultiStageTraining(Callback):
    def __init__(self, stage_epochs=[10, 20, 30]):
        self.stage_epochs = stage_epochs
        self.current_stage = 0

    def on_train_epoch_start(self, trainer, pl_module):
        epoch = trainer.current_epoch

        if epoch in self.stage_epochs:
            self.current_stage += 1
            print(f"Entering stage {self.current_stage}")

            # Adjust learning rate for new stage
            for optimizer in trainer.optimizers:
                for param_group in optimizer.param_groups:
                    param_group['lr'] *= 0.1
```

### `references/data_module.md`

# LightningDataModule - Comprehensive Guide

## Overview

A LightningDataModule is a reusable, shareable class that encapsulates all data processing steps in PyTorch Lightning. It solves the problem of scattered data preparation logic by standardizing how datasets are managed and shared across projects.

## Core Problem It Solves

In traditional PyTorch workflows, data handling is fragmented across multiple files, making it difficult to answer questions like:
- "What splits did you use?"
- "What transforms were applied?"
- "How was the data prepared?"

DataModules centralize this information for reproducibility and reusability.

## Five Processing Steps

A DataModule organizes data handling into five phases:

1. **Download/tokenize/process** - Initial data acquisition
2. **Clean and save** - Persist processed data to disk
3. **Load into Dataset** - Create PyTorch Dataset objects
4. **Apply transforms** - Data augmentation, normalization, etc.
5. **Wrap in DataLoader** - Configure batching and loading

## Main Methods

### `prepare_data()`
Downloads and processes data. Runs only once on a single process (not distributed).

**Use for:**
- Downloading datasets
- Tokenizing text
- Saving processed data to disk

**Important:** Do not set state here (e.g., self.x = y). State is not transferred to other processes.

**Example:**
```python
def prepare_data(self):
    # Download data (runs once)
    download_dataset("http://example.com/data.zip", "data/")

    # Tokenize and save (runs once)
    tokenize_and_save("data/raw/", "data/processed/")
```

### `setup(stage)`
Creates datasets and applies transforms. Runs on every process in distributed training.

**Parameters:**
- `stage` - 'fit', 'validate', 'test', or 'predict'

**Use for:**
- Creating train/val/test splits
- Building Dataset objects
- Applying transforms
- Setting state (self.train_dataset = ...)

**Example:**
```python
def setup(self, stage):
    if stage == 'fit':
        full_dataset = MyDataset("data/processed/")
        self.train_dataset, self.val_dataset = random_split(
            full_dataset, [0.8, 0.2]
        )

    if stage == 'test':
        self.test_dataset = MyDataset("data/processed/test/")

    if stage == 'predict':
        self.predict_dataset = MyDataset("data/processed/predict/")
```

### `train_dataloader()`
Returns the training DataLoader.

**Example:**
```python
def train_dataloader(self):
    return DataLoader(
        self.train_dataset,
        batch_size=self.batch_size,
        shuffle=True,
        num_workers=self.num_workers,
        pin_memory=True
    )
```

### `val_dataloader()`
Returns the validation DataLoader(s).

**Example:**
```python
def val_dataloader(self):
    return DataLoader(
        self.val_dataset,
        batch_size=self.batch_size,
        shuffle=False,
        num_workers=self.num_workers,
        pin_memory=True
    )
```

### `test_dataloader()`
Returns the test DataLoader(s).

**Example:**
```python
def test_dataloader(self):
    return DataLoader(
        self.test_dataset,
        batch_size=self.batch_size,
        shuffle=False,
        num_workers=self.num_workers
    )
```

### `predict_dataloader()`
Returns the prediction DataLoader(s).

**Example:**
```python
def predict_dataloader(self):
    return DataLoader(
        self.predict_dataset,
        batch_size=self.batch_size,
        shuffle=False,
        num_workers=self.num_workers
    )
```

## Complete Example

```python
import lightning as L
from torch.utils.data import DataLoader, Dataset, random_split
import torch

class MyDataset(Dataset):
    def __init__(self, data_path, transform=None):
        self.data_path = data_path
        self.transform = transform
        self.data = self._load_data()

    def _load_data(self):
        # Load your data here
        return torch.randn(1000, 3, 224, 224)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        if self.transform:
            sample = self.transform(sample)
        return sample

class MyDataModule(L.LightningDataModule):
    def __init__(self, data_dir="./data", batch_size=32, num_workers=4):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers

        # Transforms
        self.train_transform = self._get_train_transforms()
        self.test_transform = self._get_test_transforms()

    def _get_train_transforms(self):
        # Define training transforms
        return lambda x: x  # Placeholder

    def _get_test_transforms(self):
        # Define test/val transforms
        return lambda x: x  # Placeholder

    def prepare_data(self):
        # Download data (runs once on single process)
        # download_data(self.data_dir)
        pass

    def setup(self, stage=None):
        # Create datasets (runs on every process)
        if stage == 'fit' or stage is None:
            full_dataset = MyDataset(
                self.data_dir,
                transform=self.train_transform
            )
            train_size = int(0.8 * len(full_dataset))
            val_size = len(full_dataset) - train_size
            self.train_dataset, self.val_dataset = random_split(
                full_dataset, [train_size, val_size]
            )

        if stage == 'test' or stage is None:
            self.test_dataset = MyDataset(
                self.data_dir,
                transform=self.test_transform
            )

        if stage == 'predict':
            self.predict_dataset = MyDataset(
                self.data_dir,
                transform=self.test_transform
            )

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=True,
            persistent_workers=True if self.num_workers > 0 else False
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
            persistent_workers=True if self.num_workers > 0 else False
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers
        )

    def predict_dataloader(self):
        return DataLoader(
            self.predict_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers
        )
```

## Usage

```python
# Create DataModule
dm = MyDataModule(data_dir="./data", batch_size=64, num_workers=8)

# Use with Trainer
trainer = L.Trainer(max_epochs=10)
trainer.fit(model, datamodule=dm)

# Test
trainer.test(model, datamodule=dm)

# Predict
predictions = trainer.predict(model, datamodule=dm)

# Or use standalone in PyTorch
dm.prepare_data()
dm.setup(stage='fit')
train_loader = dm.train_dataloader()

for batch in train_loader:
    # Your training code
    pass
```

## Additional Hooks

### `transfer_batch_to_device(batch, device, dataloader_idx)`
Custom logic for moving batches to devices.

**Example:**
```python
def transfer_batch_to_device(self, batch, device, dataloader_idx):
    # Custom transfer logic
    if isinstance(batch, dict):
        return {k: v.to(device) for k, v in batch.items()}
    return super().transfer_batch_to_device(batch, device, dataloader_idx)
```

### `on_before_batch_transfer(batch, dataloader_idx)`
Augment or modify batch before transferring to device (runs on CPU).

**Example:**
```python
def on_before_batch_transfer(self, batch, dataloader_idx):
    # Apply CPU-based augmentations
    batch['image'] = apply_augmentation(batch['image'])
    return batch
```

### `on_after_batch_transfer(batch, dataloader_idx)`
Augment or modify batch after transferring to device (runs on GPU).

**Example:**
```python
def on_after_batch_transfer(self, batch, dataloader_idx):
    # Apply GPU-based augmentations
    batch['image'] = gpu_augmentation(batch['image'])
    return batch
```

### `state_dict()` / `load_state_dict(state_dict)`
Save and restore DataModule state for checkpointing.

**Example:**
```python
def state_dict(self):
    return {"current_fold": self.current_fold}

def load_state_dict(self, state_dict):
    self.current_fold = state_dict["current_fold"]
```

### `teardown(stage)`
Cleanup operations after training/testing/prediction.

**Example:**
```python
def teardown(self, stage):
    # Clean up resources
    if stage == 'fit':
        self.train_dataset = None
        self.val_dataset = None
```

## Advanced Patterns

### Multiple Validation/Test DataLoaders

Return a list or dictionary of DataLoaders:

```python
def val_dataloader(self):
    return [
        DataLoader(self.val_dataset_1, batch_size=32),
        DataLoader(self.val_dataset_2, batch_size=32)
    ]

# Or with names (for logging)
def val_dataloader(self):
    return {
        "val_easy": DataLoader(self.val_easy, batch_size=32),
        "val_hard": DataLoader(self.val_hard, batch_size=32)
    }

# In LightningModule
def validation_step(self, batch, batch_idx, dataloader_idx=0):
    if dataloader_idx == 0:
        # Handle val_dataset_1
        pass
    else:
        # Handle val_dataset_2
        pass
```

### Cross-Validation

```python
class CrossValidationDataModule(L.LightningDataModule):
    def __init__(self, data_dir, batch_size, num_folds=5):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_folds = num_folds
        self.current_fold = 0

    def setup(self, stage=None):
        full_dataset = MyDataset(self.data_dir)
        fold_size = len(full_dataset) // self.num_folds

        # Create fold indices
        indices = list(range(len(full_dataset)))
        val_start = self.current_fold * fold_size
        val_end = val_start + fold_size

        val_indices = indices[val_start:val_end]
        train_indices = indices[:val_start] + indices[val_end:]

        self.train_dataset = Subset(full_dataset, train_indices)
        self.val_dataset = Subset(full_dataset, val_indices)

    def set_fold(self, fold):
        self.current_fold = fold

    def state_dict(self):
        return {"current_fold": self.current_fold}

    def load_state_dict(self, state_dict):
        self.current_fold = state_dict["current_fold"]

# Usage
dm = CrossValidationDataModule("./data", batch_size=32, num_folds=5)

for fold in range(5):
    dm.set_fold(fold)
    trainer = L.Trainer(max_epochs=10)
    trainer.fit(model, datamodule=dm)
```

### Hyperparameter Saving

```python
class MyDataModule(L.LightningDataModule):
    def __init__(self, data_dir, batch_size=32, num_workers=4):
        super().__init__()
        # Save hyperparameters
        self.save_hyperparameters()

    def setup(self, stage=None):
        # Access via self.hparams
        print(f"Batch size: {self.hparams.batch_size}")
```

## Best Practices

### 1. Separate prepare_data and setup
- `prepare_data()` - Downloads/processes (single process, no state)
- `setup()` - Creates datasets (every process, set state)

### 2. Use stage Parameter
Check the stage in `setup()` to avoid unnecessary work:

```python
def setup(self, stage):
    if stage == 'fit':
        # Only load train/val data when fitting
        self.train_dataset = ...
        self.val_dataset = ...
    elif stage == 'test':
        # Only load test data when testing
        self.test_dataset = ...
```

### 3. Pin Memory for GPU Training
Enable `pin_memory=True` in DataLoaders for faster GPU transfer:

```python
def train_dataloader(self):
    return DataLoader(..., pin_memory=True)
```

### 4. Use Persistent Workers
Prevent worker restarts between epochs:

```python
def train_dataloader(self):
    return DataLoader(
        ...,
        num_workers=4,
        persistent_workers=True
    )
```

### 5. Avoid Shuffle in Validation/Test
Never shuffle validation or test data:

```python
def val_dataloader(self):
    return DataLoader(..., shuffle=False)  # Never True
```

### 6. Make DataModules Reusable
Accept configuration parameters in `__init__`:

```python
class MyDataModule(L.LightningDataModule):
    def __init__(self, data_dir, batch_size, num_workers, augment=True):
        super().__init__()
        self.save_hyperparameters()
```

### 7. Document Data Structure
Add docstrings explaining data format and expectations:

```python
class MyDataModule(L.LightningDataModule):
    """
    DataModule for XYZ dataset.

    Data format: (image, label) tuples
    - image: torch.Tensor of shape (C, H, W)
    - label: int in range [0, num_classes)

    Args:
        data_dir: Path to data directory
        batch_size: Batch size for dataloaders
        num_workers: Number of data loading workers
    """
```

## Common Pitfalls

### 1. Setting State in prepare_data
**Wrong:**
```python
def prepare_data(self):
    self.dataset = load_data()  # State not transferred to other processes!
```

**Correct:**
```python
def prepare_data(self):
    download_data()  # Only download, no state

def setup(self, stage):
    self.dataset = load_data()  # Set state here
```

### 2. Not Using stage Parameter
**Inefficient:**
```python
def setup(self, stage):
    self.train_dataset = load_train()
    self.val_dataset = load_val()
    self.test_dataset = load_test()  # Loads even when just fitting
```

**Efficient:**
```python
def setup(self, stage):
    if stage == 'fit':
        self.train_dataset = load_train()
        self.val_dataset = load_val()
    elif stage == 'test':
        self.test_dataset = load_test()
```

### 3. Forgetting to Return DataLoaders
**Wrong:**
```python
def train_dataloader(self):
    DataLoader(self.train_dataset, ...)  # Forgot return!
```

**Correct:**
```python
def train_dataloader(self):
    return DataLoader(self.train_dataset, ...)
```

## Integration with Trainer

```python
# Initialize DataModule
dm = MyDataModule(data_dir="./data", batch_size=64)

# All data loading is handled by DataModule
trainer = L.Trainer(max_epochs=10)
trainer.fit(model, datamodule=dm)

# DataModule handles validation too
trainer.validate(model, datamodule=dm)

# And testing
trainer.test(model, datamodule=dm)

# And prediction
predictions = trainer.predict(model, datamodule=dm)
```

### `references/distributed_training.md`

# Distributed Training - Comprehensive Guide

## Overview

PyTorch Lightning provides several strategies for training large models efficiently across multiple GPUs, nodes, and machines. Choose the right strategy based on model size and hardware configuration.

## Strategy Selection Guide

### When to Use Each Strategy

**Regular Training (Single Device)**
- Model size: Any size that fits in single GPU memory
- Use case: Prototyping, small models, debugging

**DDP (Distributed Data Parallel)**
- Model size: <500M parameters (e.g., ResNet50 ~80M parameters)
- When: Weights, activations, optimizer states, and gradients all fit in GPU memory
- Goal: Scale batch size and speed across multiple GPUs
- Best for: Most standard deep learning models

**FSDP (Fully Sharded Data Parallel)**
- Model size: 500M+ parameters (e.g., large transformers like BERT-Large, GPT)
- When: Model doesn't fit in single GPU memory
- Recommended for: Users new to model parallelism or migrating from DDP
- Features: Activation checkpointing, CPU parameter offloading

**DeepSpeed**
- Model size: 500M+ parameters
- When: Need cutting-edge features or already familiar with DeepSpeed
- Features: CPU/disk parameter offloading, distributed checkpoints, fine-grained control
- Trade-off: More complex configuration

## DDP (Distributed Data Parallel)

### Basic Usage

```python
# Single GPU
trainer = L.Trainer(accelerator="gpu", devices=1)

# Multi-GPU on single node (automatic DDP)
trainer = L.Trainer(accelerator="gpu", devices=4)

# Explicit DDP strategy
trainer = L.Trainer(strategy="ddp", accelerator="gpu", devices=4)
```

### Multi-Node DDP

```python
# On each node, run:
trainer = L.Trainer(
    strategy="ddp",
    accelerator="gpu",
    devices=4,  # GPUs per node
    num_nodes=4  # Total nodes
)
```

### DDP Configuration

```python
from lightning.pytorch.strategies import DDPStrategy

trainer = L.Trainer(
    strategy=DDPStrategy(
        process_group_backend="nccl",  # "nccl" for GPU, "gloo" for CPU
        find_unused_parameters=False,   # Set True if model has unused parameters
        gradient_as_bucket_view=True    # More memory efficient
    ),
    accelerator="gpu",
    devices=4
)
```

### DDP Spawn

Use when `ddp` causes issues (slower but more compatible):

```python
trainer = L.Trainer(strategy="ddp_spawn", accelerator="gpu", devices=4)
```

### Best Practices for DDP

1. **Batch size:** Multiply by number of GPUs
   ```python
   # If using 4 GPUs, effective batch size = batch_size * 4
   dm = MyDataModule(batch_size=32)  # 32 * 4 = 128 effective batch size
   ```

2. **Learning rate:** Often scaled with batch size
   ```python
   # Linear scaling rule
   base_lr = 0.001
   num_gpus = 4
   lr = base_lr * num_gpus
   ```

3. **Synchronization:** Use `sync_dist=True` for metrics
   ```python
   self.log("val_loss", loss, sync_dist=True)
   ```

4. **Rank-specific operations:** Use decorators for main process only
   ```python
   from lightning.pytorch.utilities import rank_zero_only

   @rank_zero_only
   def save_results(self):
       # Only runs on main process (rank 0)
       torch.save(self.results, "results.pt")
   ```

## FSDP (Fully Sharded Data Parallel)

### Basic Usage

```python
trainer = L.Trainer(
    strategy="fsdp",
    accelerator="gpu",
    devices=4
)
```

### FSDP Configuration

```python
from lightning.pytorch.strategies import FSDPStrategy
import torch.nn as nn

trainer = L.Trainer(
    strategy=FSDPStrategy(
        # Sharding strategy
        sharding_strategy="FULL_SHARD",  # or "SHARD_GRAD_OP", "NO_SHARD", "HYBRID_SHARD"

        # Activation checkpointing (save memory)
        activation_checkpointing_policy={nn.TransformerEncoderLayer},

        # CPU offloading (save GPU memory, slower)
        cpu_offload=False,

        # Mixed precision
        mixed_precision=True,

        # Wrap policy (auto-wrap layers)
        auto_wrap_policy=None
    ),
    accelerator="gpu",
    devices=8,
    precision="bf16-mixed"
)
```

### Sharding Strategies

**FULL_SHARD (default)**
- Shards optimizer states, gradients, and parameters
- Maximum memory savings
- More communication overhead

**SHARD_GRAD_OP**
- Shards optimizer states and gradients only
- Parameters kept on all devices
- Less memory savings but faster

**NO_SHARD**
- No sharding (equivalent to DDP)
- For comparison or when sharding not needed

**HYBRID_SHARD**
- Combines FULL_SHARD within nodes and NO_SHARD across nodes
- Good for multi-node setups

### Activation Checkpointing

Trade computation for memory:

```python
from lightning.pytorch.strategies import FSDPStrategy
import torch.nn as nn

# Checkpoint specific layer types
trainer = L.Trainer(
    strategy=FSDPStrategy(
        activation_checkpointing_policy={
            nn.TransformerEncoderLayer,
            nn.TransformerDecoderLayer
        }
    )
)
```

### CPU Offloading

Offload parameters to CPU when not in use:

```python
trainer = L.Trainer(
    strategy=FSDPStrategy(
        cpu_offload=True  # Slower but saves GPU memory
    ),
    accelerator="gpu",
    devices=4
)
```

### FSDP with Large Models

```python
from lightning.pytorch.strategies import FSDPStrategy
import torch.nn as nn

class LargeTransformer(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=4096, nhead=32),
            num_layers=48
        )

    def configure_sharded_model(self):
        # Called by FSDP to wrap model
        pass

# Train
trainer = L.Trainer(
    strategy=FSDPStrategy(
        activation_checkpointing_policy={nn.TransformerEncoderLayer},
        cpu_offload=False,
        sharding_strategy="FULL_SHARD"
    ),
    accelerator="gpu",
    devices=8,
    precision="bf16-mixed",
    max_epochs=10
)

model = LargeTransformer()
trainer.fit(model, datamodule=dm)
```

## DeepSpeed

### Installation

```bash
uv pip install deepspeed
```

### Basic Usage

```python
trainer = L.Trainer(
    strategy="deepspeed_stage_2",  # or "deepspeed_stage_3"
    accelerator="gpu",
    devices=4,
    precision="16-mixed"
)
```

### DeepSpeed Stages

**Stage 1: Optimizer State Sharding**
- Shards optimizer states
- Moderate memory savings

```python
trainer = L.Trainer(strategy="deepspeed_stage_1")
```

**Stage 2: Optimizer + Gradient Sharding**
- Shards optimizer states and gradients
- Good memory savings

```python
trainer = L.Trainer(strategy="deepspeed_stage_2")
```

**Stage 3: Full Model Sharding (ZeRO-3)**
- Shards optimizer states, gradients, and model parameters
- Maximum memory savings
- Can train very large models

```python
trainer = L.Trainer(strategy="deepspeed_stage_3")
```

**Stage 2 with Offloading**
- Offload to CPU or NVMe

```python
trainer = L.Trainer(strategy="deepspeed_stage_2_offload")
trainer = L.Trainer(strategy="deepspeed_stage_3_offload")
```

### DeepSpeed Configuration File

For fine-grained control:

```python
from lightning.pytorch.strategies import DeepSpeedStrategy

# Create config file: ds_config.json
config = {
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": True
        },
        "offload_param": {
            "device": "cpu",
            "pin_memory": True
        },
        "overlap_comm": True,
        "contiguous_gradients": True,
        "sub_group_size": 1e9,
        "reduce_bucket_size": "auto",
        "stage3_prefetch_bucket_size": "auto",
        "stage3_param_persistence_threshold": "auto",
        "stage3_max_live_parameters": 1e9,
        "stage3_max_reuse_distance": 1e9
    },
    "fp16": {
        "enabled": True,
        "loss_scale": 0,
        "initial_scale_power": 16,
        "loss_scale_window": 1000,
        "hysteresis": 2,
        "min_loss_scale": 1
    },
    "gradient_clipping": 1.0,
    "train_batch_size": "auto",
    "train_micro_batch_size_per_gpu": "auto"
}

trainer = L.Trainer(
    strategy=DeepSpeedStrategy(config=config),
    accelerator="gpu",
    devices=8,
    precision="16-mixed"
)
```

### DeepSpeed Best Practices

1. **Use Stage 2 for models <10B parameters**
2. **Use Stage 3 for models >10B parameters**
3. **Enable offloading if GPU memory is insufficient**
4. **Tune `reduce_bucket_size` for communication efficiency**

## Comparison Table

| Feature | DDP | FSDP | DeepSpeed |
|---------|-----|------|-----------|
| Model Size | <500M params | 500M+ params | 500M+ params |
| Memory Efficiency | Low | High | Very High |
| Speed | Fastest | Fast | Fast |
| Setup Complexity | Simple | Medium | Complex |
| Offloading | No | CPU | CPU + Disk |
| Best For | Standard models | Large models | Very large models |
| Configuration | Minimal | Moderate | Extensive |

## Mixed Precision Training

Use mixed precision to speed up training and save memory:

```python
# FP16 mixed precision
trainer = L.Trainer(precision="16-mixed")

# BFloat16 mixed precision (A100, H100)
trainer = L.Trainer(precision="bf16-mixed")

# Full precision (default)
trainer = L.Trainer(precision="32-true")

# Double precision
trainer = L.Trainer(precision="64-true")
```

### Mixed Precision with Different Strategies

```python
# DDP + FP16
trainer = L.Trainer(
    strategy="ddp",
    accelerator="gpu",
    devices=4,
    precision="16-mixed"
)

# FSDP + BFloat16
trainer = L.Trainer(
    strategy="fsdp",
    accelerator="gpu",
    devices=8,
    precision="bf16-mixed"
)

# DeepSpeed + FP16
trainer = L.Trainer(
    strategy="deepspeed_stage_2",
    accelerator="gpu",
    devices=4,
    precision="16-mixed"
)
```

## Multi-Node Training

### SLURM

```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --gpus-per-node=4
#SBATCH --time=24:00:00

srun python train.py
```

```python
# train.py
trainer = L.Trainer(
    strategy="ddp",
    accelerator="gpu",
    devices=4,
    num_nodes=4
)
```

### Manual Multi-Node Setup

Node 0 (master):
```bash
python train.py --num_nodes=2 --node_rank=0 --master_addr=192.168.1.1 --master_port=12345
```

Node 1:
```bash
python train.py --num_nodes=2 --node_rank=1 --master_addr=192.168.1.1 --master_port=12345
```

```python
# train.py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--num_nodes", type=int, default=1)
parser.add_argument("--node_rank", type=int, default=0)
parser.add_argument("--master_addr", type=str, default="localhost")
parser.add_argument("--master_port", type=int, default=12345)
args = parser.parse_args()

trainer = L.Trainer(
    strategy="ddp",
    accelerator="gpu",
    devices=4,
    num_nodes=args.num_nodes
)
```

## Common Patterns

### Gradient Accumulation with DDP

```python
# Simulate larger batch size
trainer = L.Trainer(
    strategy="ddp",
    accelerator="gpu",
    devices=4,
    accumulate_grad_batches=4  # Effective batch size = batch_size * devices * 4
)
```

### Model Checkpoint with Distributed Training

```python
from lightning.pytorch.callbacks import ModelCheckpoint

checkpoint_callback = ModelCheckpoint(
    monitor="val_loss",
    save_top_k=3,
    mode="min"
)

trainer = L.Trainer(
    strategy="ddp",
    accelerator="gpu",
    devices=4,
    callbacks=[checkpoint_callback]
)
```

### Reproducibility in Distributed Training

```python
import lightning as L

L.seed_everything(42, workers=True)

trainer = L.Trainer(
    strategy="ddp",
    accelerator="gpu",
    devices=4,
    deterministic=True
)
```

## Troubleshooting

### NCCL Timeout

Increase timeout for slow networks:

```python
import os
os.environ["NCCL_TIMEOUT"] = "3600"  # 1 hour

trainer = L.Trainer(strategy="ddp", accelerator="gpu", devices=4)
```

### CUDA Out of Memory

Solutions:
1. Enable gradient checkpointing
2. Reduce batch size
3. Use FSDP or DeepSpeed
4. Enable CPU offloading
5. Use mixed precision

```python
# Option 1: Gradient checkpointing
class MyModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = MyTransformer()
        self.model.gradient_checkpointing_enable()

# Option 2: Smaller batch size
dm = MyDataModule(batch_size=16)  # Reduce from 32

# Option 3: FSDP with offloading
trainer = L.Trainer(
    strategy=FSDPStrategy(cpu_offload=True),
    precision="bf16-mixed"
)

# Option 4: Gradient accumulation
trainer = L.Trainer(accumulate_grad_batches=4)
```

### Distributed Sampler Issues

Lightning handles DistributedSampler automatically:

```python
# Don't do this
from torch.utils.data import DistributedSampler
sampler = DistributedSampler(dataset)  # Lightning does this automatically

# Just use shuffle
train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### Communication Overhead

Reduce communication with larger `find_unused_parameters`:

```python
trainer = L.Trainer(
    strategy=DDPStrategy(find_unused_parameters=False),
    accelerator="gpu",
    devices=4
)
```

## Best Practices

### 1. Start with Single GPU
Test your code on single GPU before scaling:

```python
# Debug on single GPU
trainer = L.Trainer(accelerator="gpu", devices=1, fast_dev_run=True)

# Then scale to multiple GPUs
trainer = L.Trainer(accelerator="gpu", devices=4, strategy="ddp")
```

### 2. Use Appropriate Strategy
- <500M params: Use DDP
- 500M-10B params: Use FSDP
- >10B params: Use DeepSpeed Stage 3

### 3. Enable Mixed Precision
Always use mixed precision for modern GPUs:

```python
trainer = L.Trainer(precision="bf16-mixed")  # A100, H100
trainer = L.Trainer(precision="16-mixed")    # V100, T4
```

### 4. Scale Hyperparameters
Adjust learning rate and batch size when scaling:

```python
# Linear scaling rule
lr = base_lr * num_gpus
```

### 5. Sync Metrics
Always sync metrics in distributed training:

```python
self.log("val_loss", loss, sync_dist=True)
```

### 6. Use Rank-Zero Operations
File I/O and expensive operations on main process only:

```python
from lightning.pytorch.utilities import rank_zero_only

@rank_zero_only
def save_predictions(self):
    torch.save(self.predictions, "predictions.pt")
```

### 7. Checkpoint Regularly
Save checkpoints to resume from failures:

```python
checkpoint_callback = ModelCheckpoint(
    monitor="val_loss",  # save_top_k > 1 needs a quantity to rank on
    save_top_k=3,
    save_last=True,  # Always save last for resuming
    every_n_epochs=5
)
```

### `references/lightning_module.md`

# LightningModule - Comprehensive Guide

## Overview

A `LightningModule` organizes PyTorch code into six logical sections without abstraction. The code remains pure PyTorch, just better organized. The Trainer handles device management, distributed sampling, and infrastructure while preserving full model control.

## Core Structure

```python
import lightning as L
import torch
import torch.nn.functional as F

class MyModel(L.LightningModule):
    def __init__(self, learning_rate=0.001):
        super().__init__()
        self.save_hyperparameters()  # Save init arguments
        self.model = YourNeuralNetwork()

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self.model(x)
        loss = F.cross_entropy(logits, y)
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self.model(x)
        loss = F.cross_entropy(logits, y)
        acc = (logits.argmax(dim=1) == y).float().mean()
        self.log("val_loss", loss)
        self.log("val_acc", acc)

    def test_step(self, batch, batch_idx):
        x, y = batch
        logits = self.model(x)
        loss = F.cross_entropy(logits, y)
        acc = (logits.argmax(dim=1) == y).float().mean()
        self.log("test_loss", loss)
        self.log("test_acc", acc)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.hparams.learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min')
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "monitor": "val_loss"
            }
        }
```

## Essential Methods

### Training Pipeline Methods

#### `training_step(batch, batch_idx)`
Computes the forward pass and returns the loss. Lightning automatically handles backward propagation and optimizer updates in automatic optimization mode.

**Parameters:**
- `batch` - Current training batch from the DataLoader
- `batch_idx` - Index of the current batch

**Returns:** Loss tensor (scalar) or dictionary with 'loss' key

**Example:**
```python
def training_step(self, batch, batch_idx):
    x, y = batch
    y_hat = self.model(x)
    loss = F.mse_loss(y_hat, y)

    # Log training metrics
    self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)
    self.log("learning_rate", self.optimizers().param_groups[0]['lr'])

    return loss
```

#### `validation_step(batch, batch_idx)`
Evaluates the model on validation data. Runs with gradients disabled and model in eval mode automatically.

**Parameters:**
- `batch` - Current validation batch
- `batch_idx` - Index of the current batch

**Returns:** Optional - Loss or dictionary of metrics

**Example:**
```python
def validation_step(self, batch, batch_idx):
    x, y = batch
    y_hat = self.model(x)
    loss = F.mse_loss(y_hat, y)

    # Lightning aggregates across validation batches automatically
    self.log("val_loss", loss, prog_bar=True)
    return loss
```

#### `test_step(batch, batch_idx)`
Evaluates the model on test data. Only run when explicitly called with `trainer.test()`. Use after training is complete, typically before publication.

**Parameters:**
- `batch` - Current test batch
- `batch_idx` - Index of the current batch

**Returns:** Optional - Loss or dictionary of metrics

#### `predict_step(batch, batch_idx, dataloader_idx=0)`
Runs inference on data. Called when using `trainer.predict()`.

**Parameters:**
- `batch` - Current batch
- `batch_idx` - Index of the current batch
- `dataloader_idx` - Index of dataloader (if multiple)

**Returns:** Predictions (any format you need)

**Example:**
```python
def predict_step(self, batch, batch_idx):
    x, y = batch
    return self.model(x)  # Return raw predictions
```

### Configuration Methods

#### `configure_optimizers()`
Returns optimizer(s) and optional learning rate scheduler(s).

**Return formats:**

1. **Single optimizer:**
```python
def configure_optimizers(self):
    return torch.optim.Adam(self.parameters(), lr=0.001)
```

2. **Optimizer + scheduler:**
```python
def configure_optimizers(self):
    optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10)
    return [optimizer], [scheduler]
```

3. **Advanced configuration with scheduler monitoring:**
```python
def configure_optimizers(self):
    optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer)
    return {
        "optimizer": optimizer,
        "lr_scheduler": {
            "scheduler": scheduler,
            "monitor": "val_loss",  # Metric to monitor
            "interval": "epoch",     # When to update (epoch/step)
            "frequency": 1,          # How often to update
            "strict": True           # Crash if monitored metric not found
        }
    }
```

4. **Multiple optimizers (for GANs, etc.):**
```python
def configure_optimizers(self):
    opt_g = torch.optim.Adam(self.generator.parameters(), lr=0.0002)
    opt_d = torch.optim.Adam(self.discriminator.parameters(), lr=0.0002)
    return [opt_g, opt_d]
```

#### `forward(*args, **kwargs)`
Standard PyTorch forward method. Use for inference or as part of training_step.

**Example:**
```python
def forward(self, x):
    return self.model(x)

def training_step(self, batch, batch_idx):
    x, y = batch
    y_hat = self(x)  # Uses forward()
    return F.mse_loss(y_hat, y)
```

### Logging and Metrics

#### `log(name, value, **kwargs)`
Records metrics with automatic epoch-level reduction across devices.

**Key parameters:**
- `name` - Metric name (string)
- `value` - Metric value (tensor or number)
- `on_step` - Log at current step (default: True in training_step, False otherwise)
- `on_epoch` - Log at epoch end (default: False in training_step, True otherwise)
- `prog_bar` - Display in progress bar (default: False)
- `logger` - Send to logger backends (default: True)
- `reduce_fx` - Reduction function: "mean", "sum", "max", "min" (default: "mean")
- `sync_dist` - Synchronize across devices in distributed training (default: False)

**Examples:**
```python
# Simple logging
self.log("train_loss", loss)

# Display in progress bar
self.log("accuracy", acc, prog_bar=True)

# Log per-step and per-epoch
self.log("loss", loss, on_step=True, on_epoch=True)

# Custom reduction for distributed training
self.log("batch_size", batch.size(0), reduce_fx="sum", sync_dist=True)
```

#### `log_dict(dictionary, **kwargs)`
Log multiple metrics simultaneously.

**Example:**
```python
metrics = {"train_loss": loss, "train_acc": acc, "learning_rate": lr}
self.log_dict(metrics, on_step=True, on_epoch=True)
```

#### `save_hyperparameters(*args, **kwargs)`
Stores initialization arguments for reproducibility and checkpoint restoration. Call in `__init__()`.

**Example:**
```python
def __init__(self, learning_rate, hidden_dim, dropout):
    super().__init__()
    self.save_hyperparameters()  # Saves all init args
    # Access via self.hparams.learning_rate, self.hparams.hidden_dim, etc.
```

## Key Properties

| Property | Description |
|----------|-------------|
| `self.current_epoch` | Current epoch number (0-indexed) |
| `self.global_step` | Total optimizer steps across all epochs |
| `self.device` | Current device (cuda:0, cpu, etc.) |
| `self.global_rank` | Process rank in distributed training (0 for main) |
| `self.local_rank` | GPU rank on current node |
| `self.hparams` | Saved hyperparameters (via save_hyperparameters) |
| `self.trainer` | Reference to parent Trainer instance |
| `self.automatic_optimization` | Whether to use automatic optimization (default: True) |

## Manual Optimization

For advanced use cases (GANs, reinforcement learning, multiple optimizers), disable automatic optimization:

```python
class GANModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.automatic_optimization = False
        self.generator = Generator()
        self.discriminator = Discriminator()

    def training_step(self, batch, batch_idx):
        opt_g, opt_d = self.optimizers()

        # Train generator
        opt_g.zero_grad()
        g_loss = self.compute_generator_loss(batch)
        self.manual_backward(g_loss)
        opt_g.step()

        # Train discriminator
        opt_d.zero_grad()
        d_loss = self.compute_discriminator_loss(batch)
        self.manual_backward(d_loss)
        opt_d.step()

        self.log_dict({"g_loss": g_loss, "d_loss": d_loss})

    def configure_optimizers(self):
        opt_g = torch.optim.Adam(self.generator.parameters(), lr=0.0002)
        opt_d = torch.optim.Adam(self.discriminator.parameters(), lr=0.0002)
        return [opt_g, opt_d]
```

## Important Lifecycle Hooks

### Setup and Teardown

#### `setup(stage)`
Called at the beginning of fit, validate, test, or predict. Useful for stage-specific setup.

**Parameters:**
- `stage` - 'fit', 'validate', 'test', or 'predict'

**Example:**
```python
def setup(self, stage):
    if stage == 'fit':
        # Setup training-specific components
        self.train_dataset = load_train_data()
    elif stage == 'test':
        # Setup test-specific components
        self.test_dataset = load_test_data()
```

#### `teardown(stage)`
Called at the end of fit, validate, test, or predict. Cleanup resources.

### Epoch Boundaries

#### `on_train_epoch_start()` / `on_train_epoch_end()`
Called at the beginning/end of each training epoch.

**Example:**
```python
def on_train_epoch_end(self):
    # Compute epoch-level metrics
    all_preds = torch.cat(self.training_step_outputs)
    epoch_metric = compute_custom_metric(all_preds)
    self.log("epoch_metric", epoch_metric)
    self.training_step_outputs.clear()  # Free memory
```

#### `on_validation_epoch_start()` / `on_validation_epoch_end()`
Called at the beginning/end of validation epoch.

#### `on_test_epoch_start()` / `on_test_epoch_end()`
Called at the beginning/end of test epoch.

### Gradient Hooks

#### `on_before_backward(loss)`
Called before loss.backward().

#### `on_after_backward()`
Called after loss.backward() but before optimizer step.

**Example - Gradient inspection:**
```python
def on_after_backward(self):
    # Log gradient norms
    grad_norm = torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=1.0)
    self.log("grad_norm", grad_norm)
```

### Checkpoint Hooks

#### `on_save_checkpoint(checkpoint)`
Customize checkpoint saving. Add extra state to save.

**Example:**
```python
def on_save_checkpoint(self, checkpoint):
    checkpoint['custom_state'] = self.custom_data
```

#### `on_load_checkpoint(checkpoint)`
Customize checkpoint loading. Restore extra state.

**Example:**
```python
def on_load_checkpoint(self, checkpoint):
    self.custom_data = checkpoint.get('custom_state', default_value)
```

## Best Practices

### 1. Device Agnosticism
Never use explicit `.cuda()` or `.cpu()` calls. Lightning handles device placement automatically.

**Bad:**
```python
x = x.cuda()
model = model.cuda()
```

**Good:**
```python
x = x.to(self.device)  # Inside LightningModule
# Or let Lightning handle it automatically
```

### 2. Distributed Training Safety
Don't manually create `DistributedSampler`. Lightning handles this automatically.

**Bad:**
```python
sampler = DistributedSampler(dataset)
DataLoader(dataset, sampler=sampler)
```

**Good:**
```python
DataLoader(dataset, shuffle=True)  # Lightning converts to DistributedSampler
```

### 3. Metric Aggregation
Use `self.log()` for automatic cross-device reduction rather than manual collection.

**Bad:**
```python
self.validation_outputs.append(loss)

def on_validation_epoch_end(self):
    avg_loss = torch.stack(self.validation_outputs).mean()
```

**Good:**
```python
self.log("val_loss", loss)  # Automatic aggregation
```

### 4. Hyperparameter Tracking
Always use `self.save_hyperparameters()` for easy model reloading.

**Example:**
```python
def __init__(self, learning_rate, hidden_dim):
    super().__init__()
    self.save_hyperparameters()

# Later: Load from checkpoint
model = MyModel.load_from_checkpoint("checkpoint.ckpt")
print(model.hparams.learning_rate)
```

### 5. Validation Placement
Run validation on a single device to ensure each sample is evaluated exactly once. Lightning handles this automatically with proper strategy configuration.

## Loading from Checkpoint

```python
# Load model with saved hyperparameters
model = MyModel.load_from_checkpoint("path/to/checkpoint.ckpt")

# Override hyperparameters if needed
model = MyModel.load_from_checkpoint(
    "path/to/checkpoint.ckpt",
    learning_rate=0.0001  # Override saved value
)

# Use for inference — disable training mode on the module
model.train(False)
predictions = model(data)
```

## Common Patterns

### Gradient Accumulation
Let Lightning handle gradient accumulation:

```python
trainer = L.Trainer(accumulate_grad_batches=4)
```

### Gradient Clipping
Configure in Trainer:

```python
trainer = L.Trainer(gradient_clip_val=0.5, gradient_clip_algorithm="norm")
```

### Mixed Precision Training
Configure precision in Trainer:

```python
trainer = L.Trainer(precision="16-mixed")  # or "bf16-mixed", "32-true"
```

### Learning Rate Warmup
Implement in configure_optimizers:

```python
def configure_optimizers(self):
    optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
    scheduler = {
        "scheduler": torch.optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=0.01,
            total_steps=self.trainer.estimated_stepping_batches
        ),
        "interval": "step"
    }
    return [optimizer], [scheduler]
```

### `references/logging.md`

# Logging - Comprehensive Guide

## Overview

PyTorch Lightning supports multiple logging integrations for experiment tracking and visualization. By default, Lightning uses TensorBoard, but you can easily switch to or combine multiple loggers.

## Supported Loggers

### TensorBoardLogger (Default)

Logs to local or remote file system in TensorBoard format.

**Installation:**
```bash
uv pip install tensorboard
```

**Usage:**
```python
from lightning.pytorch import loggers as pl_loggers

tb_logger = pl_loggers.TensorBoardLogger(
    save_dir="logs/",
    name="my_model",
    version="version_1",
    default_hp_metric=False
)

trainer = L.Trainer(logger=tb_logger)
```

**View logs:**
```bash
tensorboard --logdir logs/
```

### WandbLogger

Weights & Biases integration for cloud-based experiment tracking.

**Installation:**
```bash
uv pip install wandb
```

**Usage:**
```python
from lightning.pytorch import loggers as pl_loggers

wandb_logger = pl_loggers.WandbLogger(
    project="my-project",
    name="experiment-1",
    save_dir="logs/",
    log_model=True  # Log model checkpoints to W&B
)

trainer = L.Trainer(logger=wandb_logger)
```

**Features:**
- Cloud-based experiment tracking
- Model versioning
- Artifact management
- Collaborative features
- Hyperparameter sweeps

### MLFlowLogger

MLflow tracking integration.

**Installation:**
```bash
uv pip install mlflow
```

**Usage:**
```python
from lightning.pytorch import loggers as pl_loggers

mlflow_logger = pl_loggers.MLFlowLogger(
    experiment_name="my_experiment",
    tracking_uri="http://localhost:5000",
    run_name="run_1"
)

trainer = L.Trainer(logger=mlflow_logger)
```

### CometLogger

Comet.ml experiment tracking.

**Installation:**
```bash
uv pip install comet-ml
```

**Usage:**
```python
from lightning.pytorch import loggers as pl_loggers

comet_logger = pl_loggers.CometLogger(
    api_key="YOUR_API_KEY",
    project_name="my-project",
    experiment_name="experiment-1"
)

trainer = L.Trainer(logger=comet_logger)
```

### NeptuneLogger (removed in 2.6.4+)

`NeptuneLogger` was removed in lightning 2.6.4 ([release notes](https://github.com/Lightning-AI/pytorch-lightning/releases/tag/2.6.4)). Use WandbLogger, MLFlowLogger, or TensorBoardLogger instead.

### CSVLogger

Log to local file system in YAML and CSV format.

**Usage:**
```python
from lightning.pytorch import loggers as pl_loggers

csv_logger = pl_loggers.CSVLogger(
    save_dir="logs/",
    name="my_model",
    version="1"
)

trainer = L.Trainer(logger=csv_logger)
```

**Output files:**
- `metrics.csv` - All logged metrics
- `hparams.yaml` - Hyperparameters

## Logging Metrics

### Basic Logging

Use `self.log()` within your LightningModule:

```python
class MyModel(L.LightningModule):
    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.model(x)
        loss = F.cross_entropy(y_hat, y)

        # Log metric
        self.log("train_loss", loss)

        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.model(x)
        loss = F.cross_entropy(y_hat, y)
        acc = (y_hat.argmax(dim=1) == y).float().mean()

        # Log multiple metrics
        self.log("val_loss", loss)
        self.log("val_acc", acc)
```

### Logging Parameters

#### `on_step` (bool)
Log at current step. Default: True in training_step, False otherwise.

```python
self.log("loss", loss, on_step=True)
```

#### `on_epoch` (bool)
Accumulate and log at epoch end. Default: False in training_step, True otherwise.

```python
self.log("loss", loss, on_epoch=True)
```

#### `prog_bar` (bool)
Display in progress bar. Default: False.

```python
self.log("train_loss", loss, prog_bar=True)
```

#### `logger` (bool)
Send to logger backends. Default: True.

```python
self.log("internal_metric", value, logger=False)  # Don't log to external logger
```

#### `reduce_fx` (str or callable)
Reduction function: "mean", "sum", "max", "min". Default: "mean".

```python
self.log("batch_size", batch.size(0), reduce_fx="sum")
```

#### `sync_dist` (bool)
Synchronize metric across devices in distributed training. Default: False.

```python
self.log("loss", loss, sync_dist=True)
```

#### `rank_zero_only` (bool)
Only log from rank 0 process. Default: False.

```python
self.log("debug_metric", value, rank_zero_only=True)
```

### Complete Example

```python
def training_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)

    # Log per-step and per-epoch, display in progress bar
    self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)

    return loss

def validation_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)
    acc = self.compute_accuracy(batch)

    # Log epoch-level metrics
    self.log("val_loss", loss, on_epoch=True)
    self.log("val_acc", acc, on_epoch=True, prog_bar=True)
```

### Logging Multiple Metrics

Use `log_dict()` to log multiple metrics at once:

```python
def training_step(self, batch, batch_idx):
    loss, acc, f1 = self.compute_metrics(batch)

    metrics = {
        "train_loss": loss,
        "train_acc": acc,
        "train_f1": f1
    }

    self.log_dict(metrics, on_step=True, on_epoch=True)

    return loss
```

## Logging Hyperparameters

### Automatic Hyperparameter Logging

Use `save_hyperparameters()` in your model:

```python
class MyModel(L.LightningModule):
    def __init__(self, learning_rate, hidden_dim, dropout):
        super().__init__()
        # Automatically save and log hyperparameters
        self.save_hyperparameters()
```

### Manual Hyperparameter Logging

```python
# In LightningModule
class MyModel(L.LightningModule):
    def __init__(self, learning_rate):
        super().__init__()
        self.save_hyperparameters()

# Or manually with logger
trainer.logger.log_hyperparams({
    "learning_rate": 0.001,
    "batch_size": 32
})
```

## Logging Frequency

By default, Lightning logs every 50 training steps. Adjust with `log_every_n_steps`:

```python
trainer = L.Trainer(log_every_n_steps=10)
```

## Multiple Loggers

Use multiple loggers simultaneously:

```python
from lightning.pytorch import loggers as pl_loggers

tb_logger = pl_loggers.TensorBoardLogger("logs/")
wandb_logger = pl_loggers.WandbLogger(project="my-project")
csv_logger = pl_loggers.CSVLogger("logs/")

trainer = L.Trainer(logger=[tb_logger, wandb_logger, csv_logger])
```

## Advanced Logging

### Logging Images

```python
import torchvision

def validation_step(self, batch, batch_idx):
    x, y = batch
    y_hat = self.model(x)

    # Log first batch of images once per epoch
    if batch_idx == 0:
        # Create image grid
        grid = torchvision.utils.make_grid(x[:8])

        # Log to TensorBoard
        self.logger.experiment.add_image("val_images", grid, self.current_epoch)

        # Log to Wandb
        if isinstance(self.logger, pl_loggers.WandbLogger):
            import wandb
            self.logger.experiment.log({
                "val_images": [wandb.Image(img) for img in x[:8]]
            })
```

### Logging Histograms

```python
def on_train_epoch_end(self):
    # Log parameter histograms
    for name, param in self.named_parameters():
        self.logger.experiment.add_histogram(name, param, self.current_epoch)

        if param.grad is not None:
            self.logger.experiment.add_histogram(
                f"{name}_grad", param.grad, self.current_epoch
            )
```

### Logging Model Graph

```python
def on_train_start(self):
    # Log model architecture
    sample_input = torch.randn(1, 3, 224, 224).to(self.device)
    self.logger.experiment.add_graph(self.model, sample_input)
```

### Logging Custom Plots

```python
import matplotlib.pyplot as plt

def on_validation_epoch_end(self):
    # Create custom plot
    fig, ax = plt.subplots()
    ax.plot(self.validation_losses)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")

    # Log to TensorBoard
    self.logger.experiment.add_figure("loss_curve", fig, self.current_epoch)

    plt.close(fig)
```

### Logging Text

```python
def validation_step(self, batch, batch_idx):
    # Generate predictions
    predictions = self.generate_text(batch)

    # Log to TensorBoard
    self.logger.experiment.add_text(
        "predictions",
        f"Batch {batch_idx}: {predictions}",
        self.current_epoch
    )
```

### Logging Audio

```python
def validation_step(self, batch, batch_idx):
    audio = self.generate_audio(batch)

    # Log to TensorBoard (audio is tensor of shape [1, samples])
    self.logger.experiment.add_audio(
        "generated_audio",
        audio,
        self.current_epoch,
        sample_rate=22050
    )
```

## Accessing Logger in LightningModule

```python
class MyModel(L.LightningModule):
    def training_step(self, batch, batch_idx):
        # Access logger experiment object
        logger = self.logger.experiment

        # For TensorBoard
        if isinstance(self.logger, pl_loggers.TensorBoardLogger):
            logger.add_scalar("custom_metric", value, self.global_step)

        # For Wandb
        if isinstance(self.logger, pl_loggers.WandbLogger):
            logger.log({"custom_metric": value})

        # For MLflow
        if isinstance(self.logger, pl_loggers.MLFlowLogger):
            logger.log_metric("custom_metric", value)
```

## Custom Logger

Create a custom logger by inheriting from `Logger`:

```python
from lightning.pytorch.loggers import Logger
from lightning.pytorch.utilities import rank_zero_only

class MyCustomLogger(Logger):
    def __init__(self, save_dir):
        super().__init__()
        self.save_dir = save_dir
        self._name = "my_logger"
        self._version = "0.1"

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @rank_zero_only
    def log_metrics(self, metrics, step):
        # Log metrics to your backend
        print(f"Step {step}: {metrics}")

    @rank_zero_only
    def log_hyperparams(self, params):
        # Log hyperparameters
        print(f"Hyperparameters: {params}")

    @rank_zero_only
    def save(self):
        # Save logger state
        pass

    @rank_zero_only
    def finalize(self, status):
        # Cleanup when training ends
        pass

# Usage
custom_logger = MyCustomLogger(save_dir="logs/")
trainer = L.Trainer(logger=custom_logger)
```

## Best Practices

### 1. Log Both Step and Epoch Metrics

```python
# Good: Track both granular and aggregate metrics
self.log("train_loss", loss, on_step=True, on_epoch=True)
```

### 2. Use Progress Bar for Key Metrics

```python
# Show important metrics in progress bar
self.log("val_acc", acc, prog_bar=True)
```

### 3. Synchronize Metrics in Distributed Training

```python
# Ensure correct aggregation across GPUs
self.log("val_loss", loss, sync_dist=True)
```

### 4. Log Learning Rate

```python
from lightning.pytorch.callbacks import LearningRateMonitor

trainer = L.Trainer(callbacks=[LearningRateMonitor(logging_interval="step")])
```

### 5. Log Gradient Norms

```python
def on_after_backward(self):
    # Monitor gradient flow
    grad_norm = torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=float('inf'))
    self.log("grad_norm", grad_norm)
```

### 6. Use Descriptive Metric Names

```python
# Good: Clear naming convention
self.log("train/loss", loss)
self.log("train/accuracy", acc)
self.log("val/loss", val_loss)
self.log("val/accuracy", val_acc)
```

### 7. Log Hyperparameters

```python
# Always save hyperparameters for reproducibility
class MyModel(L.LightningModule):
    def __init__(self, **kwargs):
        super().__init__()
        self.save_hyperparameters()
```

### 8. Don't Log Too Frequently

```python
# Avoid logging every step for expensive operations
if batch_idx % 100 == 0:
    self.log_images(batch)
```

## Common Patterns

### Structured Logging

```python
def training_step(self, batch, batch_idx):
    loss, metrics = self.compute_loss_and_metrics(batch)

    # Organize logs with prefixes
    self.log("train/loss", loss)
    self.log_dict({f"train/{k}": v for k, v in metrics.items()})

    return loss

def validation_step(self, batch, batch_idx):
    loss, metrics = self.compute_loss_and_metrics(batch)

    self.log("val/loss", loss)
    self.log_dict({f"val/{k}": v for k, v in metrics.items()})
```

### Conditional Logging

```python
def training_step(self, batch, batch_idx):
    loss = self.compute_loss(batch)

    # Log expensive metrics less frequently
    if self.global_step % 100 == 0:
        expensive_metric = self.compute_expensive_metric(batch)
        self.log("expensive_metric", expensive_metric)

    self.log("train_loss", loss)
    return loss
```

### Multi-Task Logging

```python
def training_step(self, batch, batch_idx):
    x, y_task1, y_task2 = batch

    loss_task1 = self.compute_task1_loss(x, y_task1)
    loss_task2 = self.compute_task2_loss(x, y_task2)
    total_loss = loss_task1 + loss_task2

    # Log per-task metrics
    self.log_dict({
        "train/loss_task1": loss_task1,
        "train/loss_task2": loss_task2,
        "train/loss_total": total_loss
    })

    return total_loss
```

## Troubleshooting

### Metric Not Found Error

If you get "metric not found" errors with schedulers:

```python
# Make sure metric is logged with logger=True
self.log("val_loss", loss, logger=True)

# And configure scheduler to monitor it
def configure_optimizers(self):
    optimizer = torch.optim.Adam(self.parameters())
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer)
    return {
        "optimizer": optimizer,
        "lr_scheduler": {
            "scheduler": scheduler,
            "monitor": "val_loss"  # Must match logged metric name
        }
    }
```

### Metrics Not Syncing in Distributed Training

```python
# Enable sync_dist for proper aggregation
self.log("val_acc", acc, sync_dist=True)
```

### Logger Not Saving

```python
# Ensure logger has write permissions
trainer = L.Trainer(
    logger=pl_loggers.TensorBoardLogger("logs/"),
    default_root_dir="outputs/"  # Ensure directory exists and is writable
)
```

### `references/trainer.md`

# Trainer - Comprehensive Guide

## Overview

The Trainer automates training workflows after organizing PyTorch code into a LightningModule. It handles loop details, device management, callbacks, gradient operations, checkpointing, and distributed training automatically.

## Core Purpose

The Trainer manages:
- Automatically enabling/disabling gradients
- Running training, validation, and test dataloaders
- Calling callbacks at appropriate times
- Placing batches on correct devices
- Orchestrating distributed training
- Progress bars and logging
- Checkpointing and early stopping

## Main Methods

### `fit(model, train_dataloaders=None, val_dataloaders=None, datamodule=None)`
Runs the full training routine including optional validation.

**Parameters:**
- `model` - LightningModule to train
- `train_dataloaders` - Training DataLoader(s)
- `val_dataloaders` - Optional validation DataLoader(s)
- `datamodule` - Optional LightningDataModule (replaces dataloaders)

**Examples:**
```python
# With DataLoaders
trainer = L.Trainer(max_epochs=10)
trainer.fit(model, train_loader, val_loader)

# With DataModule
trainer.fit(model, datamodule=dm)

# Continue training from checkpoint
trainer.fit(model, train_loader, ckpt_path="checkpoint.ckpt")
```

### `validate(model=None, dataloaders=None, datamodule=None)`
Run validation loop without training.

**Example:**
```python
trainer = L.Trainer()
trainer.validate(model, val_loader)
```

### `test(model=None, dataloaders=None, datamodule=None)`
Run test loop. Only use before publishing results.

**Example:**
```python
trainer = L.Trainer()
trainer.test(model, test_loader)
```

### `predict(model=None, dataloaders=None, datamodule=None)`
Run inference on data and return predictions.

**Example:**
```python
trainer = L.Trainer()
predictions = trainer.predict(model, predict_loader)
```

## Essential Parameters

### Training Duration

#### `max_epochs` (int)
Maximum number of epochs to train. Default: 1000

```python
trainer = L.Trainer(max_epochs=100)
```

#### `min_epochs` (int)
Minimum number of epochs to train. Default: None

```python
trainer = L.Trainer(min_epochs=10, max_epochs=100)
```

#### `max_steps` (int)
Maximum number of optimizer steps. Overrides max_epochs. Default: -1 (unlimited)

```python
trainer = L.Trainer(max_steps=10000)
```

#### `max_time` (str or dict)
Maximum training time. Useful for time-limited clusters.

```python
# String format
trainer = L.Trainer(max_time="00:12:00:00")  # 12 hours

# Dictionary format
trainer = L.Trainer(max_time={"days": 1, "hours": 6})
```

### Hardware Configuration

#### `accelerator` (str or Accelerator)
Hardware to use: "cpu", "gpu", "tpu", "ipu", "hpu", "mps", or "auto". Default: "auto"

```python
trainer = L.Trainer(accelerator="gpu")
trainer = L.Trainer(accelerator="auto")  # Auto-detect available hardware
```

#### `devices` (int, list, or str)
Number or list of device indices to use.

```python
# Use 2 GPUs
trainer = L.Trainer(devices=2, accelerator="gpu")

# Use specific GPUs
trainer = L.Trainer(devices=[0, 2], accelerator="gpu")

# Use all available devices
trainer = L.Trainer(devices="auto", accelerator="gpu")

# CPU with 4 cores
trainer = L.Trainer(devices=4, accelerator="cpu")
```

#### `strategy` (str or Strategy)
Distributed training strategy: "ddp", "ddp_spawn", "fsdp", "deepspeed", etc. Default: "auto"

```python
# Data Distributed Parallel
trainer = L.Trainer(strategy="ddp", accelerator="gpu", devices=4)

# Fully Sharded Data Parallel
trainer = L.Trainer(strategy="fsdp", accelerator="gpu", devices=4)

# DeepSpeed
trainer = L.Trainer(strategy="deepspeed_stage_2", accelerator="gpu", devices=4)
```

#### `precision` (str or int)
Floating point precision: "32-true", "16-mixed", "bf16-mixed", "64-true", etc.

```python
# Mixed precision (FP16)
trainer = L.Trainer(precision="16-mixed")

# BFloat16 mixed precision
trainer = L.Trainer(precision="bf16-mixed")

# Full precision
trainer = L.Trainer(precision="32-true")
```

### Optimization Configuration

#### `gradient_clip_val` (float)
Gradient clipping value. Default: None

```python
# Clip gradients by norm
trainer = L.Trainer(gradient_clip_val=0.5)
```

#### `gradient_clip_algorithm` (str)
Gradient clipping algorithm: "norm" or "value". Default: "norm"

```python
trainer = L.Trainer(gradient_clip_val=0.5, gradient_clip_algorithm="norm")
```

#### `accumulate_grad_batches` (int or dict)
Accumulate gradients over N batches before optimizer step.

```python
# Accumulate over 4 batches
trainer = L.Trainer(accumulate_grad_batches=4)

# Different accumulation per epoch
trainer = L.Trainer(accumulate_grad_batches={0: 4, 5: 2, 10: 1})
```

### Validation Configuration

#### `check_val_every_n_epoch` (int)
Run validation every N epochs. Default: 1

```python
trainer = L.Trainer(check_val_every_n_epoch=10)
```

#### `val_check_interval` (int or float)
How often to check validation within a training epoch.

```python
# Check validation every 0.25 of training epoch
trainer = L.Trainer(val_check_interval=0.25)

# Check validation every 100 training batches
trainer = L.Trainer(val_check_interval=100)
```

#### `limit_val_batches` (int or float)
Limit validation batches.

```python
# Use only 10% of validation data
trainer = L.Trainer(limit_val_batches=0.1)

# Use only 50 validation batches
trainer = L.Trainer(limit_val_batches=50)

# Disable validation
trainer = L.Trainer(limit_val_batches=0)
```

#### `num_sanity_val_steps` (int)
Number of validation batches to run before training starts. Default: 2

```python
# Skip sanity check
trainer = L.Trainer(num_sanity_val_steps=0)

# Run 5 sanity validation steps
trainer = L.Trainer(num_sanity_val_steps=5)
```

### Logging and Progress

#### `logger` (Logger or list or bool)
Logger(s) to use for experiment tracking.

```python
from lightning.pytorch import loggers as pl_loggers

# TensorBoard logger
tb_logger = pl_loggers.TensorBoardLogger("logs/")
trainer = L.Trainer(logger=tb_logger)

# Multiple loggers
wandb_logger = pl_loggers.WandbLogger(project="my-project")
trainer = L.Trainer(logger=[tb_logger, wandb_logger])

# Disable logging
trainer = L.Trainer(logger=False)
```

#### `log_every_n_steps` (int)
How often to log within training steps. Default: 50

```python
trainer = L.Trainer(log_every_n_steps=10)
```

#### `enable_progress_bar` (bool)
Show progress bar. Default: True

```python
trainer = L.Trainer(enable_progress_bar=False)
```

### Callbacks

#### `callbacks` (list)
List of callbacks to use during training.

```python
from lightning.pytorch.callbacks import ModelCheckpoint, EarlyStopping

checkpoint_callback = ModelCheckpoint(
    monitor="val_loss",
    save_top_k=3,
    mode="min"
)

early_stop_callback = EarlyStopping(
    monitor="val_loss",
    patience=5,
    mode="min"
)

trainer = L.Trainer(callbacks=[checkpoint_callback, early_stop_callback])
```

### Checkpointing

#### `default_root_dir` (str)
Default directory for logs and checkpoints. Default: current working directory

```python
trainer = L.Trainer(default_root_dir="./experiments/")
```

#### `enable_checkpointing` (bool)
Enable automatic checkpointing. Default: True

```python
trainer = L.Trainer(enable_checkpointing=True)
```

### Debugging

#### `fast_dev_run` (bool or int)
Run a single batch (or N batches) through train/val/test for debugging.

```python
# Run 1 batch of train/val/test
trainer = L.Trainer(fast_dev_run=True)

# Run 5 batches of train/val/test
trainer = L.Trainer(fast_dev_run=5)
```

#### `limit_train_batches` (int or float)
Limit training batches.

```python
# Use only 25% of training data
trainer = L.Trainer(limit_train_batches=0.25)

# Use only 100 training batches
trainer = L.Trainer(limit_train_batches=100)
```

#### `limit_test_batches` (int or float)
Limit test batches.

```python
trainer = L.Trainer(limit_test_batches=0.5)
```

#### `overfit_batches` (int or float)
Overfit on a subset of data for debugging.

```python
# Overfit on 10 batches
trainer = L.Trainer(overfit_batches=10)

# Overfit on 1% of data
trainer = L.Trainer(overfit_batches=0.01)
```

#### `detect_anomaly` (bool)
Enable PyTorch anomaly detection for debugging NaNs. Default: False

```python
trainer = L.Trainer(detect_anomaly=True)
```

### Reproducibility

#### `deterministic` (bool or str)
Control deterministic behavior. Default: False

```python
import lightning as L

# Seed everything
L.seed_everything(42, workers=True)

# Fully deterministic (may impact performance)
trainer = L.Trainer(deterministic=True)

# Warn if non-deterministic operations detected
trainer = L.Trainer(deterministic="warn")
```

#### `benchmark` (bool)
Enable cudnn benchmarking for performance. Default: False

```python
trainer = L.Trainer(benchmark=True)
```

### Miscellaneous

#### `enable_model_summary` (bool)
Print model summary before training. Default: True

```python
trainer = L.Trainer(enable_model_summary=False)
```

#### `inference_mode` (bool)
Use torch.inference_mode() instead of torch.no_grad() for validation/test. Default: True

```python
trainer = L.Trainer(inference_mode=True)
```

#### `profiler` (str or Profiler)
Profile code for performance optimization. Options: "simple", "advanced", or custom Profiler.

```python
# Simple profiler
trainer = L.Trainer(profiler="simple")

# Advanced profiler
trainer = L.Trainer(profiler="advanced")
```

## Common Configurations

### Basic Training
```python
trainer = L.Trainer(
    max_epochs=100,
    accelerator="auto",
    devices="auto"
)
trainer.fit(model, train_loader, val_loader)
```

### Multi-GPU Training
```python
trainer = L.Trainer(
    max_epochs=100,
    accelerator="gpu",
    devices=4,
    strategy="ddp",
    precision="16-mixed"
)
trainer.fit(model, datamodule=dm)
```

### Production Training with Checkpoints
```python
from lightning.pytorch.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor

checkpoint_callback = ModelCheckpoint(
    dirpath="checkpoints/",
    filename="{epoch}-{val_loss:.2f}",
    monitor="val_loss",
    mode="min",
    save_top_k=3,
    save_last=True
)

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    mode="min"
)

lr_monitor = LearningRateMonitor(logging_interval="step")

trainer = L.Trainer(
    max_epochs=100,
    accelerator="gpu",
    devices=2,
    strategy="ddp",
    precision="16-mixed",
    callbacks=[checkpoint_callback, early_stop, lr_monitor],
    log_every_n_steps=10,
    gradient_clip_val=1.0
)

trainer.fit(model, datamodule=dm)
```

### Debug Configuration
```python
trainer = L.Trainer(
    fast_dev_run=True,          # Run 1 batch
    accelerator="cpu",
    enable_progress_bar=True,
    log_every_n_steps=1,
    detect_anomaly=True
)
trainer.fit(model, train_loader, val_loader)
```

### Research Configuration (Reproducibility)
```python
import lightning as L

L.seed_everything(42, workers=True)

trainer = L.Trainer(
    max_epochs=100,
    accelerator="gpu",
    devices=1,
    deterministic=True,
    benchmark=False,
    precision="32-true"
)
trainer.fit(model, datamodule=dm)
```

### Time-Limited Training (Cluster)
```python
trainer = L.Trainer(
    max_time={"hours": 23, "minutes": 30},  # SLURM time limit
    max_epochs=1000,
    callbacks=[ModelCheckpoint(save_last=True)]
)
trainer.fit(model, datamodule=dm)

# Resume from checkpoint
trainer.fit(model, datamodule=dm, ckpt_path="last.ckpt")
```

### Large Model Training (FSDP)
```python
from lightning.pytorch.strategies import FSDPStrategy

trainer = L.Trainer(
    max_epochs=100,
    accelerator="gpu",
    devices=8,
    strategy=FSDPStrategy(
        activation_checkpointing_policy={nn.TransformerEncoderLayer},
        cpu_offload=False
    ),
    precision="bf16-mixed",
    accumulate_grad_batches=4
)
trainer.fit(model, datamodule=dm)
```

## Resuming Training

### From Checkpoint
```python
# Resume from specific checkpoint
trainer.fit(model, datamodule=dm, ckpt_path="epoch=10-val_loss=0.23.ckpt")

# Resume from last checkpoint
trainer.fit(model, datamodule=dm, ckpt_path="last.ckpt")
```

### Finding Last Checkpoint
```python
from lightning.pytorch.callbacks import ModelCheckpoint

checkpoint_callback = ModelCheckpoint(save_last=True)
trainer = L.Trainer(callbacks=[checkpoint_callback])
trainer.fit(model, datamodule=dm)

# Get path to last checkpoint
last_checkpoint = checkpoint_callback.last_model_path
```

## Accessing Trainer from LightningModule

Inside a LightningModule, access the Trainer via `self.trainer`:

```python
class MyModel(L.LightningModule):
    def training_step(self, batch, batch_idx):
        # Access trainer properties
        current_epoch = self.trainer.current_epoch
        global_step = self.trainer.global_step
        max_epochs = self.trainer.max_epochs

        # Access callbacks
        for callback in self.trainer.callbacks:
            if isinstance(callback, ModelCheckpoint):
                print(f"Best model: {callback.best_model_path}")

        # Access logger
        self.trainer.logger.log_metrics({"custom": value})
```

## Trainer Attributes

| Attribute | Description |
|-----------|-------------|
| `trainer.current_epoch` | Current epoch (0-indexed) |
| `trainer.global_step` | Total optimizer steps |
| `trainer.max_epochs` | Maximum epochs configured |
| `trainer.max_steps` | Maximum steps configured |
| `trainer.callbacks` | List of callbacks |
| `trainer.logger` | Logger instance |
| `trainer.strategy` | Training strategy |
| `trainer.estimated_stepping_batches` | Estimated total steps for training |

## Best Practices

### 1. Start with Fast Dev Run
Always test with `fast_dev_run=True` before full training:

```python
trainer = L.Trainer(fast_dev_run=True)
trainer.fit(model, datamodule=dm)
```

### 2. Use Gradient Clipping
Prevent gradient explosions:

```python
trainer = L.Trainer(gradient_clip_val=1.0, gradient_clip_algorithm="norm")
```

### 3. Enable Mixed Precision
Speed up training on modern GPUs:

```python
trainer = L.Trainer(precision="16-mixed")  # or "bf16-mixed" for A100+
```

### 4. Save Checkpoints Properly
Always save the last checkpoint for resuming:

```python
checkpoint_callback = ModelCheckpoint(
    save_top_k=3,
    save_last=True,
    monitor="val_loss"
)
```

### 5. Monitor Learning Rate
Track LR changes with LearningRateMonitor:

```python
from lightning.pytorch.callbacks import LearningRateMonitor

trainer = L.Trainer(callbacks=[LearningRateMonitor(logging_interval="step")])
```

### 6. Use DataModule for Reproducibility
Encapsulate data logic in a DataModule:

```python
# Better than passing DataLoaders directly
trainer.fit(model, datamodule=dm)
```

### 7. Set Deterministic for Research
Ensure reproducibility for publications:

```python
L.seed_everything(42, workers=True)
trainer = L.Trainer(deterministic=True)
```

### `scripts/quick_trainer_setup.py`

```python
"""
Quick Trainer Setup Examples for PyTorch Lightning.

This script provides ready-to-use Trainer configurations for common use cases.
Copy and modify these configurations for your specific needs.
"""

import lightning as L
from lightning.pytorch.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    LearningRateMonitor,
    DeviceStatsMonitor,
    RichProgressBar,
)
from lightning.pytorch import loggers as pl_loggers
from lightning.pytorch.strategies import DDPStrategy, FSDPStrategy


# =============================================================================
# 1. BASIC TRAINING (Single GPU/CPU)
# =============================================================================

def basic_trainer():
    """
    Simple trainer for quick prototyping.
    Use for: Small models, debugging, single GPU training
    """
    trainer = L.Trainer(
        max_epochs=10,
        accelerator="auto",  # Automatically select GPU/CPU
        devices="auto",      # Use all available devices
        enable_progress_bar=True,
        logger=True,
    )
    return trainer


# =============================================================================
# 2. DEBUGGING CONFIGURATION
# =============================================================================

def debug_trainer():
    """
    Trainer for debugging with fast dev run and anomaly detection.
    Use for: Finding bugs, testing code quickly
    """
    trainer = L.Trainer(
        fast_dev_run=True,           # Run 1 batch through train/val/test
        accelerator="cpu",            # Use CPU for easier debugging
        detect_anomaly=True,          # Detect NaN/Inf in gradients
        log_every_n_steps=1,         # Log every step
        enable_progress_bar=True,
    )
    return trainer


# =============================================================================
# 3. PRODUCTION TRAINING (Single GPU)
# =============================================================================

def production_single_gpu_trainer(
    max_epochs=100,
    log_dir="logs",
    checkpoint_dir="checkpoints"
):
    """
    Production-ready trainer for single GPU with checkpointing and logging.
    Use for: Final training runs on single GPU
    """
    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        filename="{epoch:02d}-{val_loss:.2f}",
        monitor="val_loss",
        mode="min",
        save_top_k=3,
        save_last=True,
        verbose=True,
    )

    early_stop_callback = EarlyStopping(
        monitor="val_loss",
        patience=10,
        mode="min",
        verbose=True,
    )

    lr_monitor = LearningRateMonitor(logging_interval="step")

    # Logger
    tb_logger = pl_loggers.TensorBoardLogger(
        save_dir=log_dir,
        name="my_model",
    )

    # Trainer
    trainer = L.Trainer(
        max_epochs=max_epochs,
        accelerator="gpu",
        devices=1,
        precision="16-mixed",        # Mixed precision for speed
        callbacks=[
            checkpoint_callback,
            early_stop_callback,
            lr_monitor,
        ],
        logger=tb_logger,
        log_every_n_steps=50,
        gradient_clip_val=1.0,       # Clip gradients
        enable_progress_bar=True,
    )

    return trainer


# =============================================================================
# 4. MULTI-GPU TRAINING (DDP)
# =============================================================================

def multi_gpu_ddp_trainer(
    max_epochs=100,
    num_gpus=4,
    log_dir="logs",
    checkpoint_dir="checkpoints"
):
    """
    Multi-GPU training with Distributed Data Parallel.
    Use for: Models <500M parameters, standard deep learning models
    """
    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        filename="{epoch:02d}-{val_loss:.2f}",
        monitor="val_loss",
        mode="min",
        save_top_k=3,
        save_last=True,
    )

    early_stop_callback = EarlyStopping(
        monitor="val_loss",
        patience=10,
        mode="min",
    )

    lr_monitor = LearningRateMonitor(logging_interval="step")

    # Logger
    wandb_logger = pl_loggers.WandbLogger(
        project="my-project",
        save_dir=log_dir,
    )

    # Trainer
    trainer = L.Trainer(
        max_epochs=max_epochs,
        accelerator="gpu",
        devices=num_gpus,
        strategy=DDPStrategy(
            find_unused_parameters=False,
            gradient_as_bucket_view=True,
        ),
        precision="16-mixed",
        callbacks=[
            checkpoint_callback,
            early_stop_callback,
            lr_monitor,
        ],
        logger=wandb_logger,
        log_every_n_steps=50,
        gradient_clip_val=1.0,
        sync_batchnorm=True,         # Sync batch norm across GPUs
    )

    return trainer


# =============================================================================
# 5. LARGE MODEL TRAINING (FSDP)
# =============================================================================

def large_model_fsdp_trainer(
    max_epochs=100,
    num_gpus=8,
    log_dir="logs",
    checkpoint_dir="checkpoints"
):
    """
    Training for large models (500M+ parameters) with FSDP.
    Use for: Large transformers, models that don't fit in single GPU
    """
    import torch.nn as nn

    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        filename="{epoch:02d}-{val_loss:.2f}",
        monitor="val_loss",
        mode="min",
        save_top_k=3,
        save_last=True,
    )

    lr_monitor = LearningRateMonitor(logging_interval="step")

    # Logger
    wandb_logger = pl_loggers.WandbLogger(
        project="large-model",
        save_dir=log_dir,
    )

    # Trainer with FSDP
    trainer = L.Trainer(
        max_epochs=max_epochs,
        accelerator="gpu",
        devices=num_gpus,
        strategy=FSDPStrategy(
            sharding_strategy="FULL_SHARD",
            activation_checkpointing_policy={
                nn.TransformerEncoderLayer,
                nn.TransformerDecoderLayer,
            },
            cpu_offload=False,       # Set True if GPU memory insufficient
        ),
        precision="bf16-mixed",      # BFloat16 for A100/H100
        callbacks=[
            checkpoint_callback,
            lr_monitor,
        ],
        logger=wandb_logger,
        log_every_n_steps=10,
        gradient_clip_val=1.0,
        accumulate_grad_batches=4,   # Gradient accumulation
    )

    return trainer


# =============================================================================
# 6. VERY LARGE MODEL TRAINING (DeepSpeed)
# =============================================================================

def deepspeed_trainer(
    max_epochs=100,
    num_gpus=8,
    stage=3,
    log_dir="logs",
    checkpoint_dir="checkpoints"
):
    """
    Training for very large models with DeepSpeed.
    Use for: Models >10B parameters, maximum memory efficiency
    """
    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        filename="{epoch:02d}-{step:06d}",
        monitor="val_loss",          # Required: save_top_k > 1 needs a quantity
        mode="min",
        save_top_k=3,
        save_last=True,
        every_n_train_steps=1000,    # Save every N steps
    )

    lr_monitor = LearningRateMonitor(logging_interval="step")

    # Logger
    wandb_logger = pl_loggers.WandbLogger(
        project="very-large-model",
        save_dir=log_dir,
    )

    # Select DeepSpeed stage
    strategy = f"deepspeed_stage_{stage}"

    # Trainer
    trainer = L.Trainer(
        max_epochs=max_epochs,
        accelerator="gpu",
        devices=num_gpus,
        strategy=strategy,
        precision="16-mixed",
        callbacks=[
            checkpoint_callback,
            lr_monitor,
        ],
        logger=wandb_logger,
        log_every_n_steps=10,
        gradient_clip_val=1.0,
        accumulate_grad_batches=4,
    )

    return trainer


# =============================================================================
# 7. HYPERPARAMETER TUNING
# =============================================================================

def hyperparameter_tuning_trainer(max_epochs=50):
    """
    Lightweight trainer for hyperparameter search.
    Use for: Quick experiments, hyperparameter tuning
    """
    trainer = L.Trainer(
        max_epochs=max_epochs,
        accelerator="auto",
        devices=1,
        enable_checkpointing=False,  # Don't save checkpoints
        logger=False,                 # Disable logging
        enable_progress_bar=False,
        limit_train_batches=0.5,     # Use 50% of training data
        limit_val_batches=0.5,       # Use 50% of validation data
    )
    return trainer


# =============================================================================
# 8. OVERFITTING TEST
# =============================================================================

def overfit_test_trainer(num_batches=10):
    """
    Trainer for overfitting on small subset to verify model capacity.
    Use for: Testing if model can learn, debugging
    """
    trainer = L.Trainer(
        max_epochs=100,
        accelerator="auto",
        devices=1,
        overfit_batches=num_batches,  # Overfit on N batches
        log_every_n_steps=1,
        enable_progress_bar=True,
    )
    return trainer


# =============================================================================
# 9. TIME-LIMITED TRAINING (SLURM)
# =============================================================================

def time_limited_trainer(
    max_time_hours=23.5,
    max_epochs=1000,
    checkpoint_dir="checkpoints"
):
    """
    Training with time limit for SLURM clusters.
    Use for: Cluster jobs with time limits
    """
    from datetime import timedelta

    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        monitor="val_loss",          # Required: save_top_k > 1 needs a quantity
        mode="min",
        save_top_k=3,
        save_last=True,              # Important for resuming
        every_n_epochs=5,
    )

    trainer = L.Trainer(
        max_epochs=max_epochs,
        max_time=timedelta(hours=max_time_hours),
        accelerator="gpu",
        devices="auto",
        callbacks=[checkpoint_callback],
        log_every_n_steps=50,
    )

    return trainer


# =============================================================================
# 10. REPRODUCIBLE RESEARCH
# =============================================================================

def reproducible_trainer(seed=42, max_epochs=100):
    """
    Fully reproducible trainer for research papers.
    Use for: Publications, reproducible results
    """
    # Set seed
    L.seed_everything(seed, workers=True)

    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath="checkpoints",
        filename="{epoch:02d}-{val_loss:.2f}",
        monitor="val_loss",
        mode="min",
        save_top_k=3,
        save_last=True,
    )

    # Trainer
    trainer = L.Trainer(
        max_epochs=max_epochs,
        accelerator="gpu",
        devices=1,
        precision="32-true",         # Full precision for reproducibility
        deterministic=True,          # Use deterministic algorithms
        benchmark=False,             # Disable cudnn benchmarking
        callbacks=[checkpoint_callback],
        log_every_n_steps=50,
    )

    return trainer


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    from lightning.pytorch.accelerators import CUDAAccelerator

    # Trainer construction validates the requested hardware, so the GPU-only
    # configurations below can only be built where that hardware exists.
    cuda_devices = CUDAAccelerator.auto_device_count() if CUDAAccelerator.is_available() else 0

    print("PyTorch Lightning Trainer Configurations\n")

    # Example 1: Basic training
    print("1. Basic Trainer:")
    trainer = basic_trainer()
    print(f"   - Max epochs: {trainer.max_epochs}")
    print(f"   - Accelerator: {trainer.accelerator}")
    print()

    # Example 2: Debug training
    print("2. Debug Trainer:")
    trainer = debug_trainer()
    print(f"   - Fast dev run: {trainer.fast_dev_run}")
    print(f"   - Accelerator: {trainer.accelerator}")
    print()

    # Example 3: Production single GPU
    print("3. Production Single GPU Trainer:")
    if cuda_devices >= 1:
        trainer = production_single_gpu_trainer(max_epochs=100)
        print(f"   - Max epochs: {trainer.max_epochs}")
        print(f"   - Precision: {trainer.precision}")
        print(f"   - Callbacks: {len(trainer.callbacks)}")
    else:
        print("   - skipped: no CUDA GPU on this machine")
    print()

    # Example 4: Multi-GPU DDP
    print("4. Multi-GPU DDP Trainer:")
    if cuda_devices >= 4:
        trainer = multi_gpu_ddp_trainer(num_gpus=4)
        print(f"   - Strategy: {trainer.strategy}")
        print(f"   - Devices: {trainer.num_devices}")
    else:
        print(f"   - skipped: needs 4 CUDA GPUs, found {cuda_devices}")
    print()

    # Example 5: FSDP for large models
    print("5. FSDP Trainer for Large Models:")
    if cuda_devices >= 8:
        trainer = large_model_fsdp_trainer(num_gpus=8)
        print(f"   - Strategy: {trainer.strategy}")
        print(f"   - Precision: {trainer.precision}")
    else:
        print(f"   - skipped: needs 8 CUDA GPUs, found {cuda_devices}")
    print()

    print("\nTo use these configurations:")
    print("1. Import the desired function")
    print("2. Create trainer: trainer = production_single_gpu_trainer()")
    print("3. Train model: trainer.fit(model, datamodule=dm)")
```

### `scripts/template_datamodule.py`

```python
"""
Template for creating a PyTorch Lightning DataModule.

This template provides a complete boilerplate for building a LightningDataModule
with all essential methods and best practices for data handling.
"""

import lightning as L
from torch.utils.data import Dataset, DataLoader, random_split
import torch


class CustomDataset(Dataset):
    """
    Custom Dataset implementation.

    Replace this with your actual dataset implementation.
    """

    def __init__(self, data_path, transform=None):
        """
        Initialize the dataset.

        Args:
            data_path: Path to data directory
            transform: Optional transforms to apply
        """
        self.data_path = data_path
        self.transform = transform

        # Load your data here
        # self.data = load_data(data_path)
        # self.labels = load_labels(data_path)

        # Placeholder data
        self.data = torch.randn(1000, 3, 224, 224)
        self.labels = torch.randint(0, 10, (1000,))

    def __len__(self):
        """Return the size of the dataset."""
        return len(self.data)

    def __getitem__(self, idx):
        """
        Get a single item from the dataset.

        Args:
            idx: Index of the item

        Returns:
            Tuple of (data, label)
        """
        sample = self.data[idx]
        label = self.labels[idx]

        if self.transform:
            sample = self.transform(sample)

        return sample, label


class TemplateDataModule(L.LightningDataModule):
    """
    Template LightningDataModule for data handling.

    This class encapsulates all data processing steps:
    1. Download/prepare data (prepare_data)
    2. Create datasets (setup)
    3. Create dataloaders (train/val/test/predict_dataloader)

    Args:
        data_dir: Directory containing the data
        batch_size: Batch size for dataloaders
        num_workers: Number of workers for data loading
        train_val_split: Train/validation split ratio
        pin_memory: Whether to pin memory for faster GPU transfer
    """

    def __init__(
        self,
        data_dir: str = "./data",
        batch_size: int = 32,
        num_workers: int = 4,
        train_val_split: float = 0.8,
        pin_memory: bool = True,
    ):
        super().__init__()

        # Save hyperparameters
        self.save_hyperparameters()

        # Initialize as None (will be set in setup)
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
        self.predict_dataset = None

    def prepare_data(self):
        """
        Download and prepare data.

        This method is called only once and on a single process.
        Do not set state here (e.g., self.x = y) because it's not
        transferred to other processes.

        Use this for:
        - Downloading datasets
        - Tokenizing text
        - Saving processed data to disk
        """
        # Example: Download data if not exists
        # if not os.path.exists(self.hparams.data_dir):
        #     download_dataset(self.hparams.data_dir)

        # Example: Process and save data
        # process_and_save(self.hparams.data_dir)

        pass

    def setup(self, stage: str = None):
        """
        Create datasets for each stage.

        This method is called on every process in distributed training.
        Set state here (e.g., self.train_dataset = ...).

        Args:
            stage: Current stage ('fit', 'validate', 'test', or 'predict')
        """
        # Define transforms
        train_transform = self._get_train_transforms()
        test_transform = self._get_test_transforms()

        # Setup for training and validation
        if stage == "fit" or stage is None:
            # Load full dataset
            full_dataset = CustomDataset(
                self.hparams.data_dir, transform=train_transform
            )

            # Split into train and validation
            train_size = int(self.hparams.train_val_split * len(full_dataset))
            val_size = len(full_dataset) - train_size

            self.train_dataset, self.val_dataset = random_split(
                full_dataset,
                [train_size, val_size],
                generator=torch.Generator().manual_seed(42),
            )

            # Apply test transforms to validation set
            # (Note: random_split doesn't support different transforms,
            # you may need to implement a custom wrapper)

        # Setup for testing
        if stage == "test" or stage is None:
            self.test_dataset = CustomDataset(
                self.hparams.data_dir, transform=test_transform
            )

        # Setup for prediction
        if stage == "predict":
            self.predict_dataset = CustomDataset(
                self.hparams.data_dir, transform=test_transform
            )

    def _get_train_transforms(self):
        """
        Define training transforms/augmentations.

        Returns:
            Training transforms
        """
        # Example with torchvision:
        # from torchvision import transforms
        # return transforms.Compose([
        #     transforms.RandomHorizontalFlip(),
        #     transforms.RandomRotation(10),
        #     transforms.Normalize(mean=[0.485, 0.456, 0.406],
        #                         std=[0.229, 0.224, 0.225])
        # ])

        return None

    def _get_test_transforms(self):
        """
        Define test/validation transforms (no augmentation).

        Returns:
            Test/validation transforms
        """
        # Example with torchvision:
        # from torchvision import transforms
        # return transforms.Compose([
        #     transforms.Normalize(mean=[0.485, 0.456, 0.406],
        #                         std=[0.229, 0.224, 0.225])
        # ])

        return None

    def train_dataloader(self):
        """
        Create training dataloader.

        Returns:
            Training DataLoader
        """
        return DataLoader(
            self.train_dataset,
            batch_size=self.hparams.batch_size,
            shuffle=True,
            num_workers=self.hparams.num_workers,
            pin_memory=self.hparams.pin_memory,
            persistent_workers=True if self.hparams.num_workers > 0 else False,
            drop_last=True,  # Drop last incomplete batch
        )

    def val_dataloader(self):
        """
        Create validation dataloader.

        Returns:
            Validation DataLoader
        """
        return DataLoader(
            self.val_dataset,
            batch_size=self.hparams.batch_size,
            shuffle=False,
            num_workers=self.hparams.num_workers,
            pin_memory=self.hparams.pin_memory,
            persistent_workers=True if self.hparams.num_workers > 0 else False,
        )

    def test_dataloader(self):
        """
        Create test dataloader.

        Returns:
            Test DataLoader
        """
        return DataLoader(
            self.test_dataset,
            batch_size=self.hparams.batch_size,
            shuffle=False,
            num_workers=self.hparams.num_workers,
        )

    def predict_dataloader(self):
        """
        Create prediction dataloader.

        Returns:
            Prediction DataLoader
        """
        return DataLoader(
            self.predict_dataset,
            batch_size=self.hparams.batch_size,
            shuffle=False,
            num_workers=self.hparams.num_workers,
        )

    # Optional: State management for checkpointing

    def state_dict(self):
        """
        Save DataModule state for checkpointing.

        Returns:
            State dictionary
        """
        return {"train_val_split": self.hparams.train_val_split}

    def load_state_dict(self, state_dict):
        """
        Restore DataModule state from checkpoint.

        Args:
            state_dict: State dictionary
        """
        self.hparams.train_val_split = state_dict["train_val_split"]

    # Optional: Teardown for cleanup

    def teardown(self, stage: str = None):
        """
        Cleanup after training/testing/prediction.

        Args:
            stage: Current stage ('fit', 'validate', 'test', or 'predict')
        """
        # Clean up resources
        if stage == "fit":
            self.train_dataset = None
            self.val_dataset = None
        elif stage == "test":
            self.test_dataset = None
        elif stage == "predict":
            self.predict_dataset = None


# Example usage
if __name__ == "__main__":
    # Create DataModule
    dm = TemplateDataModule(
        data_dir="./data",
        batch_size=64,
        num_workers=8,
        train_val_split=0.8,
    )

    # Setup for training
    dm.prepare_data()
    dm.setup(stage="fit")

    # Get dataloaders
    train_loader = dm.train_dataloader()
    val_loader = dm.val_dataloader()

    print(f"Train dataset size: {len(dm.train_dataset)}")
    print(f"Validation dataset size: {len(dm.val_dataset)}")
    print(f"Train batches: {len(train_loader)}")
    print(f"Validation batches: {len(val_loader)}")

    # Example: Use with Trainer
    # from template_lightning_module import TemplateLightningModule
    # model = TemplateLightningModule()
    # trainer = L.Trainer(max_epochs=10)
    # trainer.fit(model, datamodule=dm)
```

### `scripts/template_lightning_module.py`

```python
"""
Template for creating a PyTorch Lightning Module.

This template provides a complete boilerplate for building a LightningModule
with all essential methods and best practices.
"""

import lightning as L
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau


class TemplateLightningModule(L.LightningModule):
    """
    Template LightningModule for building deep learning models.

    Args:
        learning_rate: Learning rate for optimizer
        hidden_dim: Hidden dimension size
        dropout: Dropout probability
    """

    def __init__(
        self,
        learning_rate: float = 0.001,
        hidden_dim: int = 256,
        dropout: float = 0.1,
    ):
        super().__init__()

        # Save hyperparameters (accessible via self.hparams)
        self.save_hyperparameters()

        # Define your model architecture
        self.model = nn.Sequential(
            nn.Linear(784, self.hparams.hidden_dim),
            nn.ReLU(),
            nn.Dropout(self.hparams.dropout),
            nn.Linear(self.hparams.hidden_dim, 10),
        )

        # Optional: Define metrics
        # from torchmetrics import Accuracy
        # self.train_accuracy = Accuracy(task="multiclass", num_classes=10)
        # self.val_accuracy = Accuracy(task="multiclass", num_classes=10)

    def forward(self, x):
        """
        Forward pass of the model.

        Args:
            x: Input tensor

        Returns:
            Model output
        """
        return self.model(x)

    def training_step(self, batch, batch_idx):
        """
        Training step (called for each training batch).

        Args:
            batch: Current batch of data
            batch_idx: Index of the current batch

        Returns:
            Loss tensor
        """
        x, y = batch

        # Forward pass
        logits = self(x)
        loss = F.cross_entropy(logits, y)

        # Calculate accuracy (optional)
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()

        # Log metrics
        self.log("train/loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log("train/acc", acc, on_step=True, on_epoch=True)
        self.log("learning_rate", self.optimizers().param_groups[0]["lr"])

        return loss

    def validation_step(self, batch, batch_idx):
        """
        Validation step (called for each validation batch).

        Args:
            batch: Current batch of data
            batch_idx: Index of the current batch
        """
        x, y = batch

        # Forward pass
        logits = self(x)
        loss = F.cross_entropy(logits, y)

        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()

        # Log metrics (automatically aggregated across batches)
        self.log("val/loss", loss, on_epoch=True, prog_bar=True, sync_dist=True)
        self.log("val/acc", acc, on_epoch=True, prog_bar=True, sync_dist=True)

    def test_step(self, batch, batch_idx):
        """
        Test step (called for each test batch).

        Args:
            batch: Current batch of data
            batch_idx: Index of the current batch
        """
        x, y = batch

        # Forward pass
        logits = self(x)
        loss = F.cross_entropy(logits, y)

        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()

        # Log metrics
        self.log("test/loss", loss, on_epoch=True)
        self.log("test/acc", acc, on_epoch=True)

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        """
        Prediction step (called for each prediction batch).

        Args:
            batch: Current batch of data
            batch_idx: Index of the current batch
            dataloader_idx: Index of the dataloader (if multiple)

        Returns:
            Predictions
        """
        x, y = batch
        logits = self(x)
        preds = torch.argmax(logits, dim=1)
        return preds

    def configure_optimizers(self):
        """
        Configure optimizers and learning rate schedulers.

        Returns:
            Optimizer and scheduler configuration
        """
        # Define optimizer
        optimizer = Adam(
            self.parameters(),
            lr=self.hparams.learning_rate,
            weight_decay=1e-5,
        )

        # Define scheduler. PyTorch removed the schedulers' `verbose` argument;
        # use LearningRateMonitor or the logged learning_rate metric instead.
        scheduler = ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=0.5,
            patience=5,
        )

        # Return configuration
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "monitor": "val/loss",
                "interval": "epoch",
                "frequency": 1,
            },
        }

    # Optional: Add custom methods for model-specific logic

    def on_train_epoch_end(self):
        """Called at the end of each training epoch."""
        # Example: Log custom metrics
        pass

    def on_validation_epoch_end(self):
        """Called at the end of each validation epoch."""
        # Example: Compute epoch-level metrics
        pass


# Example usage
if __name__ == "__main__":
    # Create model
    model = TemplateLightningModule(
        learning_rate=0.001,
        hidden_dim=256,
        dropout=0.1,
    )

    # Create trainer
    trainer = L.Trainer(
        max_epochs=10,
        accelerator="auto",
        devices="auto",
        logger=True,
    )

    # Train (you need to provide train_dataloader and val_dataloader)
    # trainer.fit(model, train_dataloader, val_dataloader)

    n_parameters = sum(p.numel() for p in model.parameters())
    print(f"Model created with {n_parameters:,} parameters")
    print(f"Hyperparameters: {model.hparams}")
```
