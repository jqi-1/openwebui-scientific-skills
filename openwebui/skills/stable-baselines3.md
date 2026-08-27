---
name: stable-baselines3
description: Production-ready reinforcement learning algorithms (PPO, SAC, DQN, TD3, DDPG, A2C) with scikit-learn-like API. Use for standard RL experiments, quick prototyping, and well-documented algorithm implementations. Best for single-agent RL with Gymnasium environments. For high-performance parallel training, multi-agent systems, or custom vectorized environments, use pufferlib instead.
---

# Stable Baselines3

## Overview

Stable Baselines3 (SB3) is a PyTorch-based library providing reliable implementations of reinforcement learning algorithms. This skill provides comprehensive guidance for training RL agents, creating custom environments, implementing callbacks, and optimizing training workflows using SB3's unified API.

**Current upstream:** SB3 **2.8.0** (April 2026). Docs: [stable-baselines3.readthedocs.io](https://stable-baselines3.readthedocs.io/en/master/).

## Installation

Tested against **stable-baselines3 2.8.0**. Requires **Python 3.10+** (3.9 dropped in 2.8.0) and **PyTorch >= 2.3**.

```bash
# Basic installation
uv pip install "stable-baselines3>=2.8"

# With extra dependencies (TensorBoard, ale-py for Atari, etc.)
uv pip install "stable-baselines3[extra]>=2.8"
```

On zsh, quote brackets: `uv pip install 'stable-baselines3[extra]>=2.8'`.

For MuJoCo continuous-control benchmarks:

```bash
uv pip install "gymnasium[mujoco]"
```

Check your version:

```python
import stable_baselines3
print(stable_baselines3.__version__)
```

## Related Projects

- **[SB3-Contrib](https://github.com/Stable-Baselines-Team/stable-baselines3-contrib)**: experimental algorithms (MaskablePPO, CrossQ, QR-DQN, RecurrentPPO) — separate `sb3-contrib` package
- **[RL Baselines3 Zoo](https://github.com/DLR-RM/rl-baselines3-zoo)**: pre-trained agents, hyperparameters, training scripts
- **[SBX](https://github.com/araffin/sbx)**: SB3 + JAX implementations for users who prefer JAX over PyTorch

## Core Capabilities

### 1. Training RL Agents

**Basic Training Pattern:**

```python
import gymnasium as gym
from stable_baselines3 import PPO

# Create environment
env = gym.make("CartPole-v1")

# Initialize agent (device="cpu" is often faster for MlpPolicy on small envs)
model = PPO("MlpPolicy", env, verbose=1)

# Train the agent
model.learn(total_timesteps=10000)

# Save the model
model.save("ppo_cartpole")

# Load the model (without prior instantiation)
model = PPO.load("ppo_cartpole", env=env)
```

**Important Notes:**
- `total_timesteps` is a lower bound; actual training may exceed this due to batch collection
- Use `model.load()` as a static method, not on an existing instance
- The replay buffer is NOT saved with the model to save space

**Algorithm Selection:**
Use `references/algorithms.md` for detailed algorithm characteristics and selection guidance. Quick reference:
- **PPO/A2C**: General-purpose, supports all action space types, good for multiprocessing
- **SAC/TD3**: Continuous control, off-policy, sample-efficient
- **DQN**: Discrete actions, off-policy
- **HER**: Goal-conditioned tasks

See `scripts/train_rl_agent.py` for a complete training template with best practices.

### 2. Custom Environments

**Requirements:**
Custom environments must inherit from `gymnasium.Env` and implement:
- `__init__()`: Define action_space and observation_space
- `reset(seed, options)`: Return initial observation and info dict
- `step(action)`: Return observation, reward, terminated, truncated, info
- `render()`: Visualization (optional)
- `close()`: Cleanup resources

**Key Constraints:**
- Image observations must be `np.uint8` in range [0, 255]
- Use channel-first format when possible (channels, height, width)
- SB3 normalizes images automatically by dividing by 255
- Set `normalize_images=False` in policy_kwargs if pre-normalized
- SB3 does NOT support `Discrete` or `MultiDiscrete` spaces with `start!=0`

**Validation:**
```python
from stable_baselines3.common.env_checker import check_env

check_env(env, warn=True)
```

See `scripts/custom_env_template.py` for a complete custom environment template and `references/custom_environments.md` for comprehensive guidance.

### 3. Vectorized Environments

**Purpose:**
Vectorized environments run multiple environment instances in parallel, accelerating training and enabling certain wrappers (frame-stacking, normalization).

**Types:**
- **DummyVecEnv**: Sequential execution on current process (for lightweight environments)
- **SubprocVecEnv**: Parallel execution across processes (for compute-heavy environments)

**Quick Setup:**
```python
from stable_baselines3.common.env_util import make_vec_env

# Create 4 parallel environments
env = make_vec_env("CartPole-v1", n_envs=4, vec_env_cls=SubprocVecEnv)

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=25000)
```

**Off-Policy Optimization:**
When using multiple environments with off-policy algorithms (SAC, TD3, DQN), set `gradient_steps=-1` to perform one gradient update per environment step, balancing wall-clock time and sample efficiency.

**API Differences:**
- `reset()` returns only observations (info available in `vec_env.reset_infos`)
- `step()` returns 4-tuple: `(obs, rewards, dones, infos)` not 5-tuple
- Environments auto-reset after episodes
- Terminal observations available via `infos[env_idx]["terminal_observation"]`

See `references/vectorized_envs.md` for detailed information on wrappers and advanced usage.

### 4. Callbacks for Monitoring and Control

**Purpose:**
Callbacks enable monitoring metrics, saving checkpoints, implementing early stopping, and custom training logic without modifying core algorithms.

**Common Callbacks:**
- **EvalCallback**: Evaluate periodically and save best model
- **CheckpointCallback**: Save model checkpoints at intervals
- **StopTrainingOnRewardThreshold**: Stop when target reward reached
- **ProgressBarCallback**: Display training progress with timing

**Custom Callback Structure:**
```python
from stable_baselines3.common.callbacks import BaseCallback

class CustomCallback(BaseCallback):
    def _on_training_start(self):
        # Called before first rollout
        pass

    def _on_step(self):
        # Called after each environment step
        # Return False to stop training
        return True

    def _on_rollout_end(self):
        # Called at end of rollout
        pass
```

**Available Attributes:**
- `self.model`: The RL algorithm instance
- `self.num_timesteps`: Total environment steps
- `self.training_env`: The training environment

**Chaining Callbacks:**
```python
from stable_baselines3.common.callbacks import CallbackList

callback = CallbackList([eval_callback, checkpoint_callback, custom_callback])
model.learn(total_timesteps=10000, callback=callback)
```

See `references/callbacks.md` for comprehensive callback documentation.

### 5. Model Persistence and Inspection

**Saving and Loading:**
```python
# Save model
model.save("model_name")

# Save normalization statistics (if using VecNormalize)
vec_env.save("vec_normalize.pkl")

# Load model
model = PPO.load("model_name", env=env)

# Load normalization statistics
vec_env = VecNormalize.load("vec_normalize.pkl", vec_env)
```

**Parameter Access:**
```python
# Get parameters
params = model.get_parameters()

# Set parameters
model.set_parameters(params)

# Access PyTorch state dict
state_dict = model.policy.state_dict()
```

### 6. Evaluation and Recording

**Evaluation:**
```python
from stable_baselines3.common.evaluation import evaluate_policy

mean_reward, std_reward = evaluate_policy(
    model,
    env,
    n_eval_episodes=10,
    deterministic=True
)
```

**Video Recording:**
```python
from stable_baselines3.common.vec_env import VecVideoRecorder

# Wrap environment with video recorder
env = VecVideoRecorder(
    env,
    "videos/",
    record_video_trigger=lambda x: x % 2000 == 0,
    video_length=200
)
```

See `scripts/evaluate_agent.py` for a complete evaluation and recording template.

### 7. Advanced Features

**Learning Rate Schedules:**
```python
def linear_schedule(initial_value):
    def func(progress_remaining):
        # progress_remaining goes from 1 to 0
        return progress_remaining * initial_value
    return func

model = PPO("MlpPolicy", env, learning_rate=linear_schedule(0.001))
```

**Multi-Input Policies (Dict Observations):**
```python
model = PPO("MultiInputPolicy", env, verbose=1)
```
Use when observations are dictionaries (e.g., combining images with sensor data).

**Hindsight Experience Replay:**
```python
from stable_baselines3 import SAC, HerReplayBuffer

model = SAC(
    "MultiInputPolicy",
    env,
    replay_buffer_class=HerReplayBuffer,
    replay_buffer_kwargs=dict(
        n_sampled_goal=4,
        goal_selection_strategy="future",
    ),
)
```

**TensorBoard Integration:**
```python
model = PPO("MlpPolicy", env, tensorboard_log="./tensorboard/")
model.learn(total_timesteps=10000)
```

## Workflow Guidance

**Starting a New RL Project:**

1. **Define the problem**: Identify observation space, action space, and reward structure
2. **Choose algorithm**: Use `references/algorithms.md` for selection guidance
3. **Create/adapt environment**: Use `scripts/custom_env_template.py` if needed
4. **Validate environment**: Always run `check_env()` before training
5. **Set up training**: Use `scripts/train_rl_agent.py` as starting template
6. **Add monitoring**: Implement callbacks for evaluation and checkpointing
7. **Optimize performance**: Consider vectorized environments for speed
8. **Evaluate and iterate**: Use `scripts/evaluate_agent.py` for assessment

**Common Issues:**

- **Memory errors**: Reduce `buffer_size` for off-policy algorithms or use fewer parallel environments
- **Slow training**: Consider SubprocVecEnv for parallel environments
- **Unstable training**: Try different algorithms, tune hyperparameters, or check reward scaling
- **Import errors**: Ensure `stable_baselines3` is installed: `uv pip install 'stable-baselines3[extra]>=2.8'`

## Resources

### scripts/
- `train_rl_agent.py`: Complete training script template with best practices
- `evaluate_agent.py`: Agent evaluation and video recording template
- `custom_env_template.py`: Custom Gym environment template

### references/
- `algorithms.md`: Detailed algorithm comparison and selection guide
- `custom_environments.md`: Comprehensive custom environment creation guide
- `callbacks.md`: Complete callback system reference
- `vectorized_envs.md`: Vectorized environment usage and wrappers

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/stable-baselines3/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/algorithms.md`

# Stable Baselines3 Algorithm Reference

This document provides detailed characteristics of all RL algorithms in Stable Baselines3 to help select the right algorithm for specific tasks.

## Algorithm Comparison Table

| Algorithm | Type | Action Space | Sample Efficiency | Training Speed | Use Case |
|-----------|------|--------------|-------------------|----------------|----------|
| **PPO** | On-Policy | All | Medium | Fast | General-purpose, stable |
| **A2C** | On-Policy | All | Low | Very Fast | Quick prototyping, multiprocessing |
| **SAC** | Off-Policy | Continuous | High | Medium | Continuous control, sample-efficient |
| **TD3** | Off-Policy | Continuous | High | Medium | Continuous control, deterministic |
| **DDPG** | Off-Policy | Continuous | High | Medium | Continuous control (use TD3 instead) |
| **DQN** | Off-Policy | Discrete | Medium | Medium | Discrete actions, Atari games |
| **HER** | Off-Policy | All | Very High | Medium | Goal-conditioned tasks |
| **RecurrentPPO** | On-Policy | All | Medium | Slow | Partial observability (POMDP) |

## Detailed Algorithm Characteristics

### PPO (Proximal Policy Optimization)

**Overview:** General-purpose on-policy algorithm with good performance across many tasks.

**Strengths:**
- Stable and reliable training
- Works with all action space types (Discrete, Box, MultiDiscrete, MultiBinary)
- Good balance between sample efficiency and training speed
- Excellent for multiprocessing with vectorized environments
- Easy to tune

**Weaknesses:**
- Less sample-efficient than off-policy methods
- Requires many environment interactions

**Best For:**
- General-purpose RL tasks
- When stability is important
- When you have cheap environment simulations
- Tasks with continuous or discrete actions

**Hyperparameter Guidance:**
- `n_steps`: 2048-4096 for continuous, 128-256 for Atari
- `learning_rate`: 3e-4 is a good default
- `n_epochs`: 10 for continuous, 4 for Atari
- `batch_size`: 64
- `gamma`: 0.99 (0.995-0.999 for long episodes)

### A2C (Advantage Actor-Critic)

**Overview:** Synchronous variant of A3C, simpler than PPO but less stable.

**Strengths:**
- Very fast training (simpler than PPO)
- Works with all action space types
- Good for quick prototyping
- Memory efficient

**Weaknesses:**
- Less stable than PPO
- Requires careful hyperparameter tuning
- Lower sample efficiency

**Best For:**
- Quick experimentation
- When training speed is critical
- Simple environments

**Hyperparameter Guidance:**
- `n_steps`: 5-256 depending on task
- `learning_rate`: 7e-4
- `gamma`: 0.99

### SAC (Soft Actor-Critic)

**Overview:** Off-policy algorithm with entropy regularization, state-of-the-art for continuous control.

**Strengths:**
- Excellent sample efficiency
- Very stable training
- Automatic entropy tuning
- Good exploration through stochastic policy
- State-of-the-art for robotics

**Weaknesses:**
- Only supports continuous action spaces (Box)
- Slower wall-clock time than on-policy methods
- More complex hyperparameters

**Best For:**
- Continuous control (robotics, physics simulations)
- When sample efficiency is critical
- Expensive environment simulations
- Tasks requiring good exploration

**Hyperparameter Guidance:**
- `learning_rate`: 3e-4
- `buffer_size`: 1M for most tasks
- `learning_starts`: 10000
- `batch_size`: 256
- `tau`: 0.005 (target network update rate)
- `train_freq`: 1 with `gradient_steps=-1` for best performance

### TD3 (Twin Delayed DDPG)

**Overview:** Improved DDPG with double Q-learning and delayed policy updates.

**Strengths:**
- High sample efficiency
- Deterministic policy (good for deployment)
- More stable than DDPG
- Good for continuous control

**Weaknesses:**
- Only supports continuous action spaces (Box)
- Less exploration than SAC
- Requires careful tuning

**Best For:**
- Continuous control tasks
- When deterministic policies are preferred
- Sample-efficient learning

**Hyperparameter Guidance:**
- `learning_rate`: 1e-3
- `buffer_size`: 1M
- `learning_starts`: 10000
- `batch_size`: 100
- `policy_delay`: 2 (update policy every 2 critic updates)

### DDPG (Deep Deterministic Policy Gradient)

**Overview:** Early off-policy continuous control algorithm.

**Strengths:**
- Continuous action space support
- Off-policy learning

**Weaknesses:**
- Less stable than TD3 or SAC
- Sensitive to hyperparameters
- Generally outperformed by TD3

**Best For:**
- Legacy compatibility
- **Recommendation:** Use TD3 instead for new projects

### DQN (Deep Q-Network)

**Overview:** Classic off-policy algorithm for discrete action spaces.

**Strengths:**
- Sample-efficient for discrete actions
- Experience replay enables reuse of past data
- Proven success on Atari games

**Weaknesses:**
- Only supports discrete action spaces
- Can be unstable without proper tuning
- Overestimation bias

**Best For:**
- Discrete action tasks
- Atari games and similar environments
- When sample efficiency matters

**Hyperparameter Guidance:**
- `learning_rate`: 1e-4
- `buffer_size`: 100K-1M depending on task
- `learning_starts`: 50000 for Atari
- `batch_size`: 32
- `exploration_fraction`: 0.1
- `exploration_final_eps`: 0.05

**Variants:**
- **QR-DQN**: Distributional RL version for better value estimates (SB3-Contrib)
- **Maskable DQN**: For environments with action masking (SB3-Contrib)

### HER (Hindsight Experience Replay)

**Overview:** Not a standalone algorithm but a replay buffer strategy for goal-conditioned tasks.

**Strengths:**
- Dramatically improves learning in sparse reward settings
- Learns from failures by relabeling goals
- Works with any off-policy algorithm (SAC, TD3, DQN)

**Weaknesses:**
- Only for goal-conditioned environments
- Requires specific observation structure (Dict with "observation", "achieved_goal", "desired_goal")

**Best For:**
- Goal-conditioned tasks (robotics manipulation, navigation)
- Sparse reward environments
- Tasks where goal is clear but reward is binary

**Usage:**
```python
from stable_baselines3 import SAC, HerReplayBuffer

model = SAC(
    "MultiInputPolicy",
    env,
    replay_buffer_class=HerReplayBuffer,
    replay_buffer_kwargs=dict(
        n_sampled_goal=4,
        goal_selection_strategy="future",  # or "episode", "final"
    ),
)
```

### RecurrentPPO

**Overview:** PPO with LSTM policy for handling partial observability.

**Strengths:**
- Handles partial observability (POMDP)
- Can learn temporal dependencies
- Good for memory-required tasks

**Weaknesses:**
- Slower training than standard PPO
- More complex to tune
- Requires sequential data

**Best For:**
- Partially observable environments
- Tasks requiring memory (e.g., navigation without full map)
- Time-series problems

## Algorithm Selection Guide

### Decision Tree

1. **What is your action space?**
   - **Continuous (Box)** → Consider PPO, SAC, or TD3
   - **Discrete** → Consider PPO, A2C, or DQN
   - **MultiDiscrete/MultiBinary** → Use PPO or A2C

2. **Is sample efficiency critical?**
   - **Yes (expensive simulations)** → Use off-policy: SAC, TD3, DQN, or HER
   - **No (cheap simulations)** → Use on-policy: PPO, A2C

3. **Do you need fast wall-clock training?**
   - **Yes** → Use PPO or A2C with vectorized environments
   - **No** → Any algorithm works

4. **Is the task goal-conditioned with sparse rewards?**
   - **Yes** → Use HER with SAC or TD3
   - **No** → Continue with standard algorithms

5. **Is the environment partially observable?**
   - **Yes** → Use RecurrentPPO
   - **No** → Use standard algorithms

### Quick Recommendations

- **Starting out / General tasks:** PPO
- **Continuous control / Robotics:** SAC
- **Discrete actions / Atari:** DQN or PPO
- **Goal-conditioned / Sparse rewards:** SAC + HER
- **Fast prototyping:** A2C
- **Sample efficiency critical:** SAC, TD3, or DQN
- **Partial observability:** RecurrentPPO

## Training Configuration Tips

### For On-Policy Algorithms (PPO, A2C)

```python
# Use vectorized environments for speed
env = make_vec_env(env_id, n_envs=8, vec_env_cls=SubprocVecEnv)

model = PPO(
    "MlpPolicy",
    env,
    n_steps=2048,  # Collect this many steps per environment before update
    batch_size=64,
    n_epochs=10,
    learning_rate=3e-4,
    gamma=0.99,
    device="cpu",  # Often faster than GPU for small MLP tasks
)
```

### For Off-Policy Algorithms (SAC, TD3, DQN)

```python
# Fewer environments, but use gradient_steps=-1 for efficiency
env = make_vec_env(env_id, n_envs=4)

model = SAC(
    "MlpPolicy",
    env,
    buffer_size=1_000_000,
    learning_starts=10000,
    batch_size=256,
    train_freq=1,
    gradient_steps=-1,  # Do 1 gradient step per env step (4 with 4 envs)
    learning_rate=3e-4,
)
```

## Common Pitfalls

1. **Using DQN with continuous actions** - DQN only works with discrete actions
2. **Not using vectorized environments with PPO/A2C** - Wastes potential speedup
3. **Using too few environments** - On-policy methods need many samples
4. **Using too large replay buffer** - Can cause memory issues
5. **Not tuning learning rate** - Critical for stable training
6. **Ignoring reward scaling** - Normalize rewards for better learning
7. **Wrong policy type** - Use "CnnPolicy" for images, "MultiInputPolicy" for dict observations

## Performance Benchmarks

Approximate expected performance (mean reward) on common benchmarks. Numbers are **indicative only** — actual results vary significantly with hyperparameters, training time, and random seed.

### Continuous Control (MuJoCo, Gymnasium v4)
- **HalfCheetah-v4**: PPO ~1800, SAC ~12000, TD3 ~9500
- **Hopper-v4**: PPO ~2500, SAC ~3600, TD3 ~3600
- **Walker2d-v4**: PPO ~3000, SAC ~5500, TD3 ~5000

### Discrete Control (Atari)
- **Breakout**: PPO ~400, DQN ~300
- **Pong**: PPO ~20, DQN ~20
- **Space Invaders**: PPO ~1000, DQN ~800

*Note: Performance varies significantly with hyperparameters and training time.*

## SB3-Contrib (Experimental Algorithms)

These algorithms live in the separate **[sb3-contrib](https://github.com/Stable-Baselines-Team/stable-baselines3-contrib)** package, not core SB3:

| Algorithm | Use Case |
|-----------|----------|
| **MaskablePPO** | Discrete actions with action masking (invalid moves masked out) |
| **CrossQ** | Continuous control; sample-efficient off-policy (added SB3-Contrib 2.4+) |
| **QR-DQN** | Distributional DQN for better value estimates |
| **RecurrentPPO** | Partial observability (POMDP) with LSTM policy |
| **TQC** | Continuous control with distributional critics |

Install with `uv pip install sb3-contrib`.

## Additional Resources

- **RL Baselines3 Zoo**: Collection of pre-trained agents and hyperparameters: https://github.com/DLR-RM/rl-baselines3-zoo
- **Hyperparameter Tuning**: Use Optuna for systematic tuning
- **Custom Policies**: Extend base policies for custom network architectures
- **PPO + MlpPolicy on CPU**: For small MLP tasks (CartPole, Pendulum), `device="cpu"` often trains faster than GPU

### `references/callbacks.md`

# Stable Baselines3 Callback System

This document provides comprehensive information about the callback system in Stable Baselines3 for monitoring and controlling training.

## Overview

Callbacks are functions called at specific points during training to:
- Monitor training metrics
- Save checkpoints
- Implement early stopping
- Log custom metrics
- Adjust hyperparameters dynamically
- Trigger evaluations

## Built-in Callbacks

### EvalCallback

Evaluates the agent periodically and saves the best model.

```python
from stable_baselines3.common.callbacks import EvalCallback

eval_callback = EvalCallback(
    eval_env,                                    # Separate evaluation environment
    best_model_save_path="./logs/best_model/",  # Where to save best model
    log_path="./logs/eval/",                    # Where to save evaluation logs
    eval_freq=10000,                            # Evaluate every N steps
    n_eval_episodes=5,                          # Number of episodes per evaluation
    deterministic=True,                         # Use deterministic actions
    render=False,                               # Render during evaluation
    verbose=1,
    warn=True,
)

model.learn(total_timesteps=100000, callback=eval_callback)
```

**Key Features:**
- Automatically saves best model based on mean reward
- Logs evaluation metrics to TensorBoard
- Can stop training if reward threshold reached

**Important:** Callback frequencies (`eval_freq`, `save_freq`) are measured in **environment steps per sub-environment**, not total timesteps across all parallel envs. Divide by `n_envs` to align with total training timesteps:

```python
# With 4 parallel environments, divide eval_freq by n_envs
eval_freq = 10000 // 4  # Evaluate every 10000 total environment steps
```

### CheckpointCallback

Saves model checkpoints at regular intervals.

```python
from stable_baselines3.common.callbacks import CheckpointCallback

checkpoint_callback = CheckpointCallback(
    save_freq=10000,                     # Save every N steps
    save_path="./logs/checkpoints/",     # Directory for checkpoints
    name_prefix="rl_model",              # Prefix for checkpoint files
    save_replay_buffer=True,             # Save replay buffer (off-policy only)
    save_vecnormalize=True,              # Save VecNormalize stats
    verbose=2,
)

model.learn(total_timesteps=100000, callback=checkpoint_callback)
```

**Output Files:**
- `rl_model_10000_steps.zip` - Model at 10k steps
- `rl_model_20000_steps.zip` - Model at 20k steps
- etc.

**Important:** `save_freq` is in **environment steps per sub-environment**; divide by `n_envs` for total-timestep alignment (same as `EvalCallback` above).

### LogEveryNTimesteps

Dumps training logs every N timesteps (added SB3 2.6.0). Useful when the algorithm's built-in `log_interval` is too coarse.

```python
from stable_baselines3.common.callbacks import LogEveryNTimesteps

log_callback = LogEveryNTimesteps(n_steps=1000)

# Pass log_interval=None to avoid interference with the algorithm's default logging
model = PPO("MlpPolicy", env, log_interval=None, verbose=1)
model.learn(total_timesteps=100000, callback=log_callback)
```

### StopTrainingOnRewardThreshold

Stops training when mean reward exceeds a threshold.

```python
from stable_baselines3.common.callbacks import StopTrainingOnRewardThreshold

stop_callback = StopTrainingOnRewardThreshold(
    reward_threshold=200,  # Stop when mean reward >= 200
    verbose=1,
)

# Must be used with EvalCallback
eval_callback = EvalCallback(
    eval_env,
    callback_on_new_best=stop_callback,  # Trigger when new best found
    eval_freq=10000,
    n_eval_episodes=5,
)

model.learn(total_timesteps=1000000, callback=eval_callback)
```

### StopTrainingOnNoModelImprovement

Stops training if model doesn't improve for N evaluations.

```python
from stable_baselines3.common.callbacks import StopTrainingOnNoModelImprovement

stop_callback = StopTrainingOnNoModelImprovement(
    max_no_improvement_evals=10,  # Stop after 10 evals with no improvement
    min_evals=20,                 # Minimum evaluations before stopping
    verbose=1,
)

# Use with EvalCallback
eval_callback = EvalCallback(
    eval_env,
    callback_after_eval=stop_callback,
    eval_freq=10000,
)

model.learn(total_timesteps=1000000, callback=eval_callback)
```

### StopTrainingOnMaxEpisodes

Stops training after a maximum number of episodes.

```python
from stable_baselines3.common.callbacks import StopTrainingOnMaxEpisodes

stop_callback = StopTrainingOnMaxEpisodes(
    max_episodes=1000,  # Stop after 1000 episodes
    verbose=1,
)

model.learn(total_timesteps=1000000, callback=stop_callback)
```

### ProgressBarCallback

Displays a progress bar during training (requires tqdm).

```python
from stable_baselines3.common.callbacks import ProgressBarCallback

progress_callback = ProgressBarCallback()

model.learn(total_timesteps=100000, callback=progress_callback)
```

**Output:**
```
100%|██████████| 100000/100000 [05:23<00:00, 309.31it/s]
```

## Creating Custom Callbacks

### BaseCallback Structure

```python
from stable_baselines3.common.callbacks import BaseCallback

class CustomCallback(BaseCallback):
    """
    Custom callback template.
    """

    def __init__(self, verbose=0):
        super().__init__(verbose)
        # Custom initialization

    def _init_callback(self) -> None:
        """
        Called once when training starts.
        Useful for initialization that requires access to model/env.
        """
        pass

    def _on_training_start(self) -> None:
        """
        Called before the first rollout starts.
        """
        pass

    def _on_rollout_start(self) -> None:
        """
        Called before collecting new samples (on-policy algorithms).
        """
        pass

    def _on_step(self) -> bool:
        """
        Called after every step in the environment.

        Returns:
            bool: If False, training will be stopped.
        """
        return True  # Continue training

    def _on_rollout_end(self) -> None:
        """
        Called after rollout ends (on-policy algorithms).
        """
        pass

    def _on_training_end(self) -> None:
        """
        Called at the end of training.
        """
        pass
```

### Useful Attributes

Inside callbacks, you have access to:

- **`self.model`**: The RL algorithm instance
- **`self.training_env`**: The training environment
- **`self.n_calls`**: Number of times `_on_step()` was called
- **`self.num_timesteps`**: Total number of environment steps
- **`self.locals`**: Local variables from the algorithm (varies by algorithm)
- **`self.globals`**: Global variables from the algorithm
- **`self.logger`**: Logger for TensorBoard/CSV logging
- **`self.parent`**: Parent callback (if used in CallbackList)

## Custom Callback Examples

### Example 1: Log Custom Metrics

```python
class LogCustomMetricsCallback(BaseCallback):
    """
    Log custom metrics to TensorBoard.
    """

    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []

    def _on_step(self) -> bool:
        # Check if episode ended
        if self.locals["dones"][0]:
            # Log episode reward
            episode_reward = self.locals["infos"][0].get("episode", {}).get("r", 0)
            self.episode_rewards.append(episode_reward)

            # Log to TensorBoard
            self.logger.record("custom/episode_reward", episode_reward)
            self.logger.record("custom/mean_reward_last_100",
                             np.mean(self.episode_rewards[-100:]))

        return True
```

### Example 2: Adjust Learning Rate

```python
class LinearScheduleCallback(BaseCallback):
    """
    Linearly decrease learning rate during training.
    """

    def __init__(self, initial_lr=3e-4, final_lr=3e-5, verbose=0):
        super().__init__(verbose)
        self.initial_lr = initial_lr
        self.final_lr = final_lr

    def _on_step(self) -> bool:
        # Calculate progress (0 to 1)
        progress = self.num_timesteps / self.locals["total_timesteps"]

        # Linear interpolation
        new_lr = self.initial_lr + (self.final_lr - self.initial_lr) * progress

        # Update learning rate
        for param_group in self.model.policy.optimizer.param_groups:
            param_group["lr"] = new_lr

        # Log learning rate
        self.logger.record("train/learning_rate", new_lr)

        return True
```

### Example 3: Early Stopping on Moving Average

```python
class EarlyStoppingCallback(BaseCallback):
    """
    Stop training if moving average of rewards doesn't improve.
    """

    def __init__(self, check_freq=10000, min_reward=200, window=100, verbose=0):
        super().__init__(verbose)
        self.check_freq = check_freq
        self.min_reward = min_reward
        self.window = window
        self.rewards = []

    def _on_step(self) -> bool:
        # Collect episode rewards
        if self.locals["dones"][0]:
            reward = self.locals["infos"][0].get("episode", {}).get("r", 0)
            self.rewards.append(reward)

        # Check every check_freq steps
        if self.n_calls % self.check_freq == 0 and len(self.rewards) >= self.window:
            mean_reward = np.mean(self.rewards[-self.window:])
            if self.verbose > 0:
                print(f"Mean reward: {mean_reward:.2f}")

            if mean_reward >= self.min_reward:
                if self.verbose > 0:
                    print(f"Stopping: reward threshold reached!")
                return False  # Stop training

        return True  # Continue training
```

### Example 4: Save Best Model by Custom Metric

```python
class SaveBestModelCallback(BaseCallback):
    """
    Save model when custom metric is best.
    """

    def __init__(self, check_freq=1000, save_path="./best_model/", verbose=0):
        super().__init__(verbose)
        self.check_freq = check_freq
        self.save_path = save_path
        self.best_score = -np.inf

    def _init_callback(self) -> None:
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:
            # Calculate custom metric (example: policy entropy)
            custom_metric = self.locals.get("entropy_losses", [0])[-1]

            if custom_metric > self.best_score:
                self.best_score = custom_metric
                if self.verbose > 0:
                    print(f"New best! Saving model to {self.save_path}")
                self.model.save(os.path.join(self.save_path, "best_model"))

        return True
```

### Example 5: Log Environment-Specific Information

```python
class EnvironmentInfoCallback(BaseCallback):
    """
    Log custom info from environment.
    """

    def _on_step(self) -> bool:
        # Access info dict from environment
        info = self.locals["infos"][0]

        # Log custom metrics from environment
        if "distance_to_goal" in info:
            self.logger.record("env/distance_to_goal", info["distance_to_goal"])

        if "success" in info:
            self.logger.record("env/success_rate", info["success"])

        return True
```

## Chaining Multiple Callbacks

Use `CallbackList` to combine multiple callbacks:

```python
from stable_baselines3.common.callbacks import CallbackList

callback_list = CallbackList([
    eval_callback,
    checkpoint_callback,
    progress_callback,
    custom_callback,
])

model.learn(total_timesteps=100000, callback=callback_list)
```

Or pass a list directly:

```python
model.learn(
    total_timesteps=100000,
    callback=[eval_callback, checkpoint_callback, custom_callback]
)
```

## Event-Based Callbacks

Callbacks can trigger other callbacks on specific events:

```python
from stable_baselines3.common.callbacks import EventCallback

# Stop training when reward threshold reached
stop_callback = StopTrainingOnRewardThreshold(reward_threshold=200)

# Evaluate periodically and trigger stop_callback when new best found
eval_callback = EvalCallback(
    eval_env,
    callback_on_new_best=stop_callback,  # Triggered when new best model
    eval_freq=10000,
)
```

## Logging to TensorBoard

Use `self.logger.record()` to log metrics:

```python
class TensorBoardCallback(BaseCallback):
    def _on_step(self) -> bool:
        # Log scalar
        self.logger.record("custom/my_metric", value)

        # Log multiple metrics
        self.logger.record("custom/metric1", value1)
        self.logger.record("custom/metric2", value2)

        # Logger automatically writes to TensorBoard
        return True
```

**View in TensorBoard:**
```bash
tensorboard --logdir ./logs/
```

## Advanced Patterns

### Curriculum Learning

```python
class CurriculumCallback(BaseCallback):
    """
    Increase task difficulty over time.
    """

    def __init__(self, difficulty_schedule, verbose=0):
        super().__init__(verbose)
        self.difficulty_schedule = difficulty_schedule

    def _on_step(self) -> bool:
        # Update environment difficulty based on progress
        progress = self.num_timesteps / self.locals["total_timesteps"]

        for threshold, difficulty in self.difficulty_schedule:
            if progress >= threshold:
                self.training_env.env_method("set_difficulty", difficulty)

        return True
```

### Population-Based Training

```python
class PopulationBasedCallback(BaseCallback):
    """
    Adjust hyperparameters based on performance.
    """

    def __init__(self, check_freq=10000, verbose=0):
        super().__init__(verbose)
        self.check_freq = check_freq
        self.performance_history = []

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:
            # Evaluate performance
            perf = self._evaluate_performance()
            self.performance_history.append(perf)

            # Adjust hyperparameters if performance plateaus
            if len(self.performance_history) >= 3:
                recent = self.performance_history[-3:]
                if max(recent) - min(recent) < 0.01:  # Plateau detected
                    self._adjust_hyperparameters()

        return True

    def _adjust_hyperparameters(self):
        # Example: increase learning rate
        for param_group in self.model.policy.optimizer.param_groups:
            param_group["lr"] *= 1.2
```

## Debugging Tips

### Print Available Attributes

```python
class DebugCallback(BaseCallback):
    def _on_step(self) -> bool:
        if self.n_calls == 1:
            print("Available in self.locals:")
            for key in self.locals.keys():
                print(f"  {key}: {type(self.locals[key])}")
        return True
```

### Common Issues

1. **Callback not being called:**
   - Ensure callback is passed to `model.learn()`
   - Check that `_on_step()` returns `True`

2. **AttributeError in callback:**
   - Not all attributes available in all callbacks
   - Use `self.locals.get("key", default)` for safety

3. **Memory leaks:**
   - Don't store large arrays in callback state
   - Clear buffers periodically

4. **Performance impact:**
   - Minimize computation in `_on_step()` (called every step)
   - Use `check_freq` to limit expensive operations

## Best Practices

1. **Use appropriate callback timing:**
   - `_on_step()`: For metrics that change every step
   - `_on_rollout_end()`: For metrics computed over rollouts
   - `_init_callback()`: For one-time initialization

2. **Log efficiently:**
   - Don't log every step (hurts performance)
   - Aggregate metrics and log periodically

3. **Handle vectorized environments:**
   - Remember that `dones`, `infos`, etc. are arrays
   - Check `dones[i]` for each environment

4. **Test callbacks independently:**
   - Create simple test cases
   - Verify callback behavior before long training runs

5. **Document custom callbacks:**
   - Clear docstrings
   - Example usage in comments

## Additional Resources

- Official SB3 Callbacks Guide: https://stable-baselines3.readthedocs.io/en/master/guide/callbacks.html
- Callback API Reference: https://stable-baselines3.readthedocs.io/en/master/common/callbacks.html
- TensorBoard Documentation: https://www.tensorflow.org/tensorboard

### `references/custom_environments.md`

# Creating Custom Environments for Stable Baselines3

This guide provides comprehensive information for creating custom Gymnasium environments compatible with Stable Baselines3.

## Environment Structure

### Required Methods

Every custom environment must inherit from `gymnasium.Env` and implement:

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class CustomEnv(gym.Env):
    def __init__(self):
        """Initialize environment, define action_space and observation_space"""
        super().__init__()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        """Reset environment to initial state"""
        super().reset(seed=seed)
        observation = self.observation_space.sample()
        info = {}
        return observation, info

    def step(self, action):
        """Execute one timestep"""
        observation = self.observation_space.sample()
        reward = 0.0
        terminated = False  # Episode ended naturally
        truncated = False   # Episode ended due to time limit
        info = {}
        return observation, reward, terminated, truncated, info

    def render(self):
        """Visualize environment (optional)"""
        pass

    def close(self):
        """Cleanup resources (optional)"""
        pass
```

### Method Details

#### `__init__(self, ...)`

**Purpose:** Initialize the environment and define spaces.

**Requirements:**
- Must call `super().__init__()`
- Must define `self.action_space`
- Must define `self.observation_space`

**Example:**
```python
def __init__(self, grid_size=10, max_steps=100):
    super().__init__()
    self.grid_size = grid_size
    self.max_steps = max_steps
    self.current_step = 0

    # Define spaces
    self.action_space = spaces.Discrete(4)
    self.observation_space = spaces.Box(
        low=0, high=grid_size-1, shape=(2,), dtype=np.float32
    )
```

#### `reset(self, seed=None, options=None)`

**Purpose:** Reset the environment to an initial state.

**Requirements:**
- Must call `super().reset(seed=seed)`
- Must return `(observation, info)` tuple
- Observation must match `observation_space`
- Info must be a dictionary (can be empty)

**Example:**
```python
def reset(self, seed=None, options=None):
    super().reset(seed=seed)

    # Initialize state
    self.agent_pos = self.np_random.integers(0, self.grid_size, size=2)
    self.goal_pos = self.np_random.integers(0, self.grid_size, size=2)
    self.current_step = 0

    observation = self._get_observation()
    info = {"episode": "started"}

    return observation, info
```

#### `step(self, action)`

**Purpose:** Execute one timestep in the environment.

**Requirements:**
- Must return 5-tuple: `(observation, reward, terminated, truncated, info)`
- Action must be valid according to `action_space`
- Observation must match `observation_space`
- Reward should be a float
- Terminated: True if episode ended naturally (goal reached, failure, etc.)
- Truncated: True if episode ended due to time limit
- Info must be a dictionary

**Example:**
```python
def step(self, action):
    # Apply action
    self.agent_pos += self._action_to_direction(action)
    self.agent_pos = np.clip(self.agent_pos, 0, self.grid_size - 1)
    self.current_step += 1

    # Calculate reward
    distance = np.linalg.norm(self.agent_pos - self.goal_pos)
    goal_reached = distance < 1.0

    if goal_reached:
        reward = 100.0
    else:
        reward = -distance * 0.1

    # Check termination conditions
    terminated = goal_reached
    truncated = self.current_step >= self.max_steps

    observation = self._get_observation()
    info = {"distance": distance, "steps": self.current_step}

    return observation, reward, terminated, truncated, info
```

## Space Types

### Discrete

For discrete actions (e.g., {0, 1, 2, 3}).

```python
self.action_space = spaces.Discrete(4)  # 4 actions: 0, 1, 2, 3
```

**Important:** SB3 does NOT support `Discrete` spaces with `start != 0`. Always start from 0.

### Box (Continuous)

For continuous values within a range.

```python
# 1D continuous action in [-1, 1]
self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)

# 2D position observation
self.observation_space = spaces.Box(
    low=0, high=10, shape=(2,), dtype=np.float32
)

# 3D RGB image (channel-first format)
self.observation_space = spaces.Box(
    low=0, high=255, shape=(3, 84, 84), dtype=np.uint8
)
```

**Important for Images:**
- Must be `dtype=np.uint8` in range [0, 255]
- Use **channel-first** format: (channels, height, width)
- SB3 automatically normalizes by dividing by 255
- Set `normalize_images=False` in policy_kwargs if pre-normalized

### MultiDiscrete

For multiple discrete variables.

```python
# Two discrete variables: first with 3 options, second with 4 options
self.action_space = spaces.MultiDiscrete([3, 4])
```

**Important (SB3 2.8+ env checker):** If your `MultiDiscrete` space uses multi-dimensional arrays (not a flat vector), the env checker will warn you. Use a wrapper to flatten the space or reshape observations/actions to match SB3's expected 1D layout. See the [SB3 custom env guide](https://stable-baselines3.readthedocs.io/en/master/guide/custom_env.html) for the recommended wrapper pattern.

### MultiBinary

For binary vectors.

```python
# 5 binary flags
self.action_space = spaces.MultiBinary(5)  # e.g., [0, 1, 1, 0, 1]
```

### Dict

For dictionary observations (e.g., combining image with sensors).

```python
self.observation_space = spaces.Dict({
    "image": spaces.Box(low=0, high=255, shape=(3, 64, 64), dtype=np.uint8),
    "vector": spaces.Box(low=-10, high=10, shape=(4,), dtype=np.float32),
    "discrete": spaces.Discrete(3),
})
```

**Important:** When using Dict observations, use `"MultiInputPolicy"` instead of `"MlpPolicy"`.

```python
model = PPO("MultiInputPolicy", env, verbose=1)
```

### Tuple

For tuple observations (less common).

```python
self.observation_space = spaces.Tuple((
    spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32),
    spaces.Discrete(3),
))
```

## Important Constraints and Best Practices

### Data Types

- **Observations:** Use `np.float32` for continuous values
- **Images:** Use `np.uint8` in range [0, 255]
- **Rewards:** Return Python float or `np.float32`
- **Terminated/Truncated:** Return Python bool

### Random Number Generation

Always use `self.np_random` for reproducibility:

```python
def reset(self, seed=None, options=None):
    super().reset(seed=seed)
    # Use self.np_random instead of np.random
    random_pos = self.np_random.integers(0, 10, size=2)
    random_float = self.np_random.random()
```

### Episode Termination

- **Terminated:** Natural ending (goal reached, agent died, etc.)
- **Truncated:** Artificial ending (time limit, external interrupt)

```python
def step(self, action):
    # ... environment logic ...

    goal_reached = self._check_goal()
    time_limit_exceeded = self.current_step >= self.max_steps

    terminated = goal_reached  # Natural ending
    truncated = time_limit_exceeded  # Time limit

    return observation, reward, terminated, truncated, info
```

### Info Dictionary

Use the info dict for debugging and logging:

```python
info = {
    "episode_length": self.current_step,
    "distance_to_goal": distance,
    "success": goal_reached,
    "total_reward": self.cumulative_reward,
}
```

**Special Keys:**
- `"terminal_observation"`: Automatically added by VecEnv when episode ends

## Advanced Features

### Metadata

Provide rendering information:

```python
class CustomEnv(gym.Env):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": 30,
    }

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        # ...
```

### Render Modes

```python
def render(self):
    if self.render_mode == "human":
        # Print or display for human viewing
        print(f"Agent at {self.agent_pos}")

    elif self.render_mode == "rgb_array":
        # Return numpy array (height, width, 3) for video recording
        canvas = np.zeros((500, 500, 3), dtype=np.uint8)
        # Draw environment on canvas
        return canvas
```

### Goal-Conditioned Environments (for HER)

For Hindsight Experience Replay, use specific observation structure:

```python
self.observation_space = spaces.Dict({
    "observation": spaces.Box(low=-10, high=10, shape=(3,), dtype=np.float32),
    "achieved_goal": spaces.Box(low=-10, high=10, shape=(3,), dtype=np.float32),
    "desired_goal": spaces.Box(low=-10, high=10, shape=(3,), dtype=np.float32),
})

def compute_reward(self, achieved_goal, desired_goal, info):
    """Required for HER environments"""
    distance = np.linalg.norm(achieved_goal - desired_goal)
    return -distance
```

## Environment Validation

Always validate your environment before training:

```python
from stable_baselines3.common.env_checker import check_env

env = CustomEnv()
check_env(env, warn=True)
```

**Common Validation Errors:**

1. **"Observation is not within bounds"**
   - Check that observations stay within defined space
   - Ensure correct dtype (np.float32 for Box spaces)

2. **"Reset should return tuple"**
   - Return `(observation, info)`, not just observation

3. **"Step should return 5-tuple"**
   - Return `(obs, reward, terminated, truncated, info)`

4. **"Action is out of bounds"**
   - Verify action_space definition matches expected actions

5. **"Observation/Action dtype mismatch"**
   - Ensure observations match space dtype (usually np.float32)

## Environment Registration

Register your environment with Gymnasium:

```python
import gymnasium as gym
from gymnasium.envs.registration import register

register(
    id="MyCustomEnv-v0",
    entry_point="my_module:CustomEnv",
    max_episode_steps=200,
    kwargs={"grid_size": 10},  # Default kwargs
)

# Now can use with gym.make
env = gym.make("MyCustomEnv-v0")
```

## Testing Custom Environments

### Basic Testing

```python
def test_environment(env, n_episodes=5):
    """Test environment with random actions"""
    for episode in range(n_episodes):
        obs, info = env.reset()
        episode_reward = 0
        done = False
        steps = 0

        while not done:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            done = terminated or truncated

        print(f"Episode {episode+1}: Reward={episode_reward:.2f}, Steps={steps}")
```

### Training Test

```python
from stable_baselines3 import PPO

def train_test(env, timesteps=10000):
    """Quick training test"""
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=timesteps)

    # Evaluate
    obs, info = env.reset()
    for _ in range(100):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
```

## Common Patterns

### Grid World

```python
class GridWorldEnv(gym.Env):
    def __init__(self, size=10):
        super().__init__()
        self.size = size
        self.action_space = spaces.Discrete(4)  # up, down, left, right
        self.observation_space = spaces.Box(0, size-1, shape=(2,), dtype=np.float32)
```

### Continuous Control

```python
class ContinuousEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32)
```

### Image-Based Environment

```python
class VisionEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(4)
        # Channel-first: (channels, height, width)
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(3, 84, 84), dtype=np.uint8
        )
```

### Multi-Modal Environment

```python
class MultiModalEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Dict({
            "image": spaces.Box(0, 255, shape=(3, 64, 64), dtype=np.uint8),
            "sensors": spaces.Box(-10, 10, shape=(4,), dtype=np.float32),
        })
```

## Performance Considerations

### Efficient Observation Generation

```python
# Pre-allocate arrays
def __init__(self):
    # ...
    self._obs_buffer = np.zeros(self.observation_space.shape, dtype=np.float32)

def _get_observation(self):
    # Reuse buffer instead of allocating new array
    self._obs_buffer[0] = self.agent_x
    self._obs_buffer[1] = self.agent_y
    return self._obs_buffer
```

### Vectorization

Make environment operations vectorizable:

```python
# Good: Uses numpy operations
def step(self, action):
    direction = np.array([[0,1], [0,-1], [1,0], [-1,0]])[action]
    self.pos = np.clip(self.pos + direction, 0, self.size-1)

# Avoid: Python loops when possible
# for i in range(len(self.agents)):
#     self.agents[i].update()
```

## Troubleshooting

### "Observation out of bounds"
- Check that all observations are within defined space
- Verify correct dtype (np.float32 vs np.float64)

### "NaN or Inf in observation/reward"
- Add checks: `assert np.isfinite(reward)`
- Use `VecCheckNan` wrapper to catch issues

### "Policy doesn't learn"
- Check reward scaling (normalize rewards)
- Verify observation normalization
- Ensure reward signal is meaningful
- Check if exploration is sufficient

### "Training crashes"
- Validate environment with `check_env()`
- Check for race conditions in custom env
- Verify action/observation spaces are consistent

## Additional Resources

- Template: See `scripts/custom_env_template.py`
- Gymnasium Documentation: https://gymnasium.farama.org/
- SB3 Custom Env Guide: https://stable-baselines3.readthedocs.io/en/master/guide/custom_env.html

### `references/vectorized_envs.md`

# Vectorized Environments in Stable Baselines3

This document provides comprehensive information about vectorized environments in Stable Baselines3 for efficient parallel training.

## Overview

Vectorized environments stack multiple independent environment instances into a single environment that processes actions and observations in batches. Instead of interacting with one environment at a time, you interact with `n` environments simultaneously.

**Benefits:**
- **Speed:** Parallel execution significantly accelerates training
- **Sample efficiency:** Collect more diverse experiences faster
- **Required for:** Frame stacking and normalization wrappers
- **Better for:** On-policy algorithms (PPO, A2C)

## VecEnv Types

### DummyVecEnv

Executes environments sequentially on the current Python process.

```python
from stable_baselines3.common.vec_env import DummyVecEnv

# Method 1: Using make_vec_env
from stable_baselines3.common.env_util import make_vec_env

env = make_vec_env("CartPole-v1", n_envs=4, vec_env_cls=DummyVecEnv)

# Method 2: Manual creation
def make_env():
    def _init():
        return gym.make("CartPole-v1")
    return _init

env = DummyVecEnv([make_env() for _ in range(4)])
```

**When to use:**
- Lightweight environments (CartPole, simple grids)
- When multiprocessing overhead > computation time
- Debugging (easier to trace errors)
- Single-threaded environments

**Performance:** No actual parallelism (sequential execution).

### SubprocVecEnv

Executes each environment in a separate process, enabling true parallelism.

```python
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env

env = make_vec_env("CartPole-v1", n_envs=8, vec_env_cls=SubprocVecEnv)
```

**When to use:**
- Computationally expensive environments (physics simulations, 3D games)
- When environment computation time justifies multiprocessing overhead
- When you need true parallel execution

**Important:** Requires wrapping code in `if __name__ == "__main__":` when using forkserver or spawn:

```python
if __name__ == "__main__":
    env = make_vec_env("CartPole-v1", n_envs=8, vec_env_cls=SubprocVecEnv)
    model = PPO("MlpPolicy", env)
    model.learn(total_timesteps=100000)
```

**Performance:** True parallelism across CPU cores.

## Quick Setup with make_vec_env

The easiest way to create vectorized environments:

```python
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv

# Basic usage
env = make_vec_env("CartPole-v1", n_envs=4)

# With SubprocVecEnv
env = make_vec_env("CartPole-v1", n_envs=8, vec_env_cls=SubprocVecEnv)

# With custom environment kwargs
env = make_vec_env(
    "MyEnv-v0",
    n_envs=4,
    env_kwargs={"difficulty": "hard", "max_steps": 500}
)

# With custom seed
env = make_vec_env("CartPole-v1", n_envs=4, seed=42)
```

## API Differences from Standard Gym

Vectorized environments have a different API than standard Gym environments:

### reset()

**Standard Gym:**
```python
obs, info = env.reset()
```

**VecEnv:**
```python
obs = env.reset()  # Returns only observations (numpy array)
# Access info via env.reset_infos (list of dicts)
infos = env.reset_infos
```

**Seeding and options:** Call `vec_env.seed(seed=seed)` and/or `vec_env.set_options(options)` before the initial `reset()`. Seed and options are discarded after each `reset()` call.

**Truncation vs termination:** When an episode ends, check `infos[env_idx]["TimeLimit.truncated"]` to distinguish timeout/truncation from natural termination. Bootstrap value targets when `TimeLimit.truncated` is True or when the episode has not ended.

### step()

**Standard Gym:**
```python
obs, reward, terminated, truncated, info = env.step(action)
```

**VecEnv:**
```python
obs, rewards, dones, infos = env.step(actions)
# Returns 4-tuple instead of 5-tuple
# dones = terminated | truncated
# actions is an array of shape (n_envs,) or (n_envs, action_dim)
```

### Auto-reset

**VecEnv automatically resets environments when episodes end:**

```python
obs = env.reset()  # Shape: (n_envs, obs_dim)
for _ in range(1000):
    actions = env.action_space.sample()  # Shape: (n_envs,)
    obs, rewards, dones, infos = env.step(actions)
    # If dones[i] is True, env i was automatically reset
    # Final observation before reset available in infos[i]["terminal_observation"]
```

### Terminal Observations

When an episode ends, access the true final observation:

```python
obs, rewards, dones, infos = env.step(actions)

for i, done in enumerate(dones):
    if done:
        # The obs[i] is already the reset observation
        # True terminal observation is in info
        terminal_obs = infos[i]["terminal_observation"]
        print(f"Episode ended with terminal observation: {terminal_obs}")
```

## Training with Vectorized Environments

### On-Policy Algorithms (PPO, A2C)

On-policy algorithms benefit greatly from vectorization:

```python
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv

# Create vectorized environment
env = make_vec_env("CartPole-v1", n_envs=8, vec_env_cls=SubprocVecEnv)

# Train
model = PPO("MlpPolicy", env, verbose=1, n_steps=128)
model.learn(total_timesteps=100000)

# With n_envs=8 and n_steps=128:
# - Collects 8*128=1024 steps per rollout
# - Updates after every 1024 steps
```

**Rule of thumb:** Use 4-16 parallel environments for on-policy methods.

### Off-Policy Algorithms (SAC, TD3, DQN)

Off-policy algorithms can use vectorization but benefit less:

```python
from stable_baselines3 import SAC
from stable_baselines3.common.env_util import make_vec_env

# Use fewer environments (1-4)
env = make_vec_env("Pendulum-v1", n_envs=4)

# Set gradient_steps=-1 for efficiency
model = SAC(
    "MlpPolicy",
    env,
    verbose=1,
    train_freq=1,
    gradient_steps=-1,  # Do 1 gradient step per env step (4 total with 4 envs)
)
model.learn(total_timesteps=50000)
```

**Rule of thumb:** Use 1-4 parallel environments for off-policy methods.

## Wrappers for Vectorized Environments

### VecNormalize

Normalizes observations and rewards using running statistics.

```python
from stable_baselines3.common.vec_env import VecNormalize

env = make_vec_env("Pendulum-v1", n_envs=4)

# Wrap with normalization
env = VecNormalize(
    env,
    norm_obs=True,        # Normalize observations
    norm_reward=True,     # Normalize rewards
    clip_obs=10.0,        # Clip normalized observations
    clip_reward=10.0,     # Clip normalized rewards
    gamma=0.99,           # Discount factor for reward normalization
)

# Train
model = PPO("MlpPolicy", env)
model.learn(total_timesteps=50000)

# Save model AND normalization statistics
model.save("ppo_pendulum")
env.save("vec_normalize.pkl")

# Load for evaluation
env = make_vec_env("Pendulum-v1", n_envs=1)
env = VecNormalize.load("vec_normalize.pkl", env)
env.training = False  # Don't update stats during evaluation
env.norm_reward = False  # Don't normalize rewards during evaluation

model = PPO.load("ppo_pendulum", env=env)
```

**When to use:**
- Continuous control tasks (especially MuJoCo)
- When observation scales vary widely
- When rewards have high variance

**Important:**
- Statistics are NOT saved with model - save separately
- Disable training and reward normalization during evaluation

### VecFrameStack

Stacks observations from multiple consecutive frames.

```python
from stable_baselines3.common.vec_env import VecFrameStack

env = make_vec_env("PongNoFrameskip-v4", n_envs=8)

# Stack 4 frames
env = VecFrameStack(env, n_stack=4)

# Now observations have shape: (n_envs, n_stack, height, width)
model = PPO("CnnPolicy", env)
model.learn(total_timesteps=1000000)
```

**When to use:**
- Atari games (stack 4 frames)
- Environments where velocity information is needed
- Partial observability problems

### VecVideoRecorder

Records videos of agent behavior.

```python
from stable_baselines3.common.vec_env import VecVideoRecorder

env = make_vec_env("CartPole-v1", n_envs=1)

# Record videos
env = VecVideoRecorder(
    env,
    video_folder="./videos/",
    record_video_trigger=lambda x: x % 2000 == 0,  # Record every 2000 steps
    video_length=200,  # Max video length
    name_prefix="training"
)

model = PPO("MlpPolicy", env)
model.learn(total_timesteps=10000)
```

**Output:** MP4 videos in `./videos/` directory.

### VecCheckNan

Checks for NaN or infinite values in observations and rewards.

```python
from stable_baselines3.common.vec_env import VecCheckNan

env = make_vec_env("CustomEnv-v0", n_envs=4)

# Add NaN checking (useful for debugging)
env = VecCheckNan(env, raise_exception=True, warn_once=True)

model = PPO("MlpPolicy", env)
model.learn(total_timesteps=10000)
```

**When to use:**
- Debugging custom environments
- Catching numerical instabilities
- Validating environment implementation

### VecTransposeImage

Transposes image observations from (height, width, channels) to (channels, height, width).

```python
from stable_baselines3.common.vec_env import VecTransposeImage

env = make_vec_env("PongNoFrameskip-v4", n_envs=4)

# Convert HWC to CHW format
env = VecTransposeImage(env)

model = PPO("CnnPolicy", env)
```

**When to use:**
- When environment returns images in HWC format
- SB3 expects CHW format for CNN policies

## Advanced Usage

### Custom VecEnv

Create custom vectorized environment:

```python
from stable_baselines3.common.vec_env import DummyVecEnv
import gymnasium as gym

class CustomVecEnv(DummyVecEnv):
    def step_wait(self):
        # Custom logic before/after stepping
        obs, rewards, dones, infos = super().step_wait()
        # Modify observations/rewards/etc
        return obs, rewards, dones, infos
```

### Environment Method Calls

Call methods on wrapped environments:

```python
env = make_vec_env("MyEnv-v0", n_envs=4)

# Call method on all environments
env.env_method("set_difficulty", "hard")

# Call method on specific environment
env.env_method("reset_level", indices=[0, 2])

# Get attribute from all environments
levels = env.get_attr("current_level")
```

### Setting Attributes

```python
# Set attribute on all environments
env.set_attr("difficulty", "hard")

# Set attribute on specific environments
env.set_attr("max_steps", 1000, indices=[1, 3])
```

### Checking Attributes

```python
# Check if attribute exists on all sub-environments (added SB3 2.6.0)
if env.has_attr("current_level"):
    levels = env.get_attr("current_level")
```

## Performance Optimization

### Choosing Number of Environments

**On-Policy (PPO, A2C):**
```python
# General rule: 4-16 environments
# More environments = faster data collection
n_envs = 8
env = make_vec_env("CartPole-v1", n_envs=n_envs)

# Adjust n_steps to maintain same rollout length
# Total steps per rollout = n_envs * n_steps
model = PPO("MlpPolicy", env, n_steps=128)  # 8*128 = 1024 steps/rollout
```

**Off-Policy (SAC, TD3, DQN):**
```python
# General rule: 1-4 environments
# More doesn't help as much (replay buffer provides diversity)
n_envs = 4
env = make_vec_env("Pendulum-v1", n_envs=n_envs)

model = SAC("MlpPolicy", env, gradient_steps=-1)  # 1 grad step per env step
```

### CPU Core Utilization

```python
import multiprocessing

# Use one less than total cores (leave one for Python main process)
n_cpus = multiprocessing.cpu_count() - 1
env = make_vec_env("MyEnv-v0", n_envs=n_cpus, vec_env_cls=SubprocVecEnv)
```

### Memory Considerations

```python
# Large replay buffer + many environments = high memory usage
# Reduce buffer size if memory constrained
model = SAC(
    "MlpPolicy",
    env,
    buffer_size=100_000,  # Reduced from 1M
)
```

## Common Issues

### Issue: "Can't pickle local object"

**Cause:** SubprocVecEnv requires picklable environments.

**Solution:** Define environment creation outside class/function:

```python
# Bad
def train():
    def make_env():
        return gym.make("CartPole-v1")
    env = SubprocVecEnv([make_env for _ in range(4)])

# Good
def make_env():
    return gym.make("CartPole-v1")

if __name__ == "__main__":
    env = SubprocVecEnv([make_env for _ in range(4)])
```

### Issue: Different behavior between single and vectorized env

**Cause:** Auto-reset in vectorized environments.

**Solution:** Handle terminal observations correctly:

```python
obs, rewards, dones, infos = env.step(actions)
for i, done in enumerate(dones):
    if done:
        terminal_obs = infos[i]["terminal_observation"]
        # Process terminal_obs if needed
```

### Issue: Slower with SubprocVecEnv than DummyVecEnv

**Cause:** Environment too lightweight (multiprocessing overhead > computation).

**Solution:** Use DummyVecEnv for simple environments:

```python
# For CartPole, use DummyVecEnv
env = make_vec_env("CartPole-v1", n_envs=8, vec_env_cls=DummyVecEnv)
```

### Issue: Training crashes with SubprocVecEnv

**Cause:** Environment not properly isolated or has shared state.

**Solution:**
- Ensure environment has no shared global state
- Wrap code in `if __name__ == "__main__":`
- Use DummyVecEnv for debugging

## Best Practices

1. **Use appropriate VecEnv type:**
   - DummyVecEnv: Simple environments (CartPole, basic grids)
   - SubprocVecEnv: Complex environments (MuJoCo, Unity, 3D games)

2. **Adjust hyperparameters for vectorization:**
   - Divide `eval_freq`, `save_freq` by `n_envs` in callbacks
   - Maintain same `n_steps * n_envs` for on-policy algorithms

3. **Save normalization statistics:**
   - Always save VecNormalize stats with model
   - Disable training during evaluation

4. **Monitor memory usage:**
   - More environments = more memory
   - Reduce buffer size if needed

5. **Test with DummyVecEnv first:**
   - Easier debugging
   - Ensure environment works before parallelizing

## Examples

### Basic Training Loop

```python
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv

# Create vectorized environment
env = make_vec_env("CartPole-v1", n_envs=8, vec_env_cls=SubprocVecEnv)

# Train
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)

# Evaluate
obs = env.reset()
for _ in range(1000):
    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, dones, infos = env.step(action)
```

### With Normalization

```python
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import VecNormalize

# Create and normalize
env = make_vec_env("Pendulum-v1", n_envs=4)
env = VecNormalize(env, norm_obs=True, norm_reward=True)

# Train
model = PPO("MlpPolicy", env)
model.learn(total_timesteps=50000)

# Save both
model.save("model")
env.save("vec_normalize.pkl")

# Load for evaluation
eval_env = make_vec_env("Pendulum-v1", n_envs=1)
eval_env = VecNormalize.load("vec_normalize.pkl", eval_env)
eval_env.training = False
eval_env.norm_reward = False

model = PPO.load("model", env=eval_env)
```

## Additional Resources

- Official SB3 VecEnv Guide: https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html
- VecEnv API Reference: https://stable-baselines3.readthedocs.io/en/master/common/vec_env.html
- Multiprocessing Best Practices: https://docs.python.org/3/library/multiprocessing.html

### `scripts/custom_env_template.py`

```python
"""
Template for creating custom Gymnasium environments compatible with Stable Baselines3.

This template demonstrates:
- Proper Gymnasium environment structure
- Observation and action space definition
- Step and reset implementation
- Validation with SB3's env_checker
- Registration with Gymnasium
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np


class CustomEnv(gym.Env):
    """
    Custom Gymnasium Environment Template.

    This is a template for creating custom environments that work with
    Stable Baselines3. Modify the observation space, action space, reward
    function, and state transitions to match your specific problem.

    Example:
        A simple grid world where the agent tries to reach a goal position.
    """

    # Optional: Provide metadata for rendering modes
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, grid_size=5, render_mode=None):
        """
        Initialize the environment.

        Args:
            grid_size: Size of the grid world (grid_size x grid_size)
            render_mode: How to render ('human', 'rgb_array', or None)
        """
        super().__init__()

        self.grid_size = grid_size
        self.render_mode = render_mode

        # Define action space
        # Example: 4 discrete actions (up, down, left, right)
        self.action_space = spaces.Discrete(4)

        # Define observation space
        # Example: 2D position [x, y] in continuous space
        # Note: Use np.float32 for observations (SB3 recommendation)
        self.observation_space = spaces.Box(
            low=0,
            high=grid_size - 1,
            shape=(2,),
            dtype=np.float32,
        )

        # Alternative observation spaces:
        # 1. Discrete: spaces.Discrete(n)
        # 2. Multi-discrete: spaces.MultiDiscrete([n1, n2, ...])
        # 3. Multi-binary: spaces.MultiBinary(n)
        # 4. Box (continuous): spaces.Box(low=, high=, shape=, dtype=np.float32)
        # 5. Dict: spaces.Dict({"key1": space1, "key2": space2})

        # For image observations (e.g., 84x84 RGB image):
        # self.observation_space = spaces.Box(
        #     low=0,
        #     high=255,
        #     shape=(3, 84, 84),  # (channels, height, width) - channel-first
        #     dtype=np.uint8,
        # )

        # Initialize state
        self._agent_position = None
        self._goal_position = None

    def reset(self, seed=None, options=None):
        """
        Reset the environment to initial state.

        Args:
            seed: Random seed for reproducibility
            options: Additional options (optional)

        Returns:
            observation: Initial observation
            info: Additional information dictionary
        """
        # Set seed for reproducibility
        super().reset(seed=seed)

        # Initialize agent position randomly
        self._agent_position = self.np_random.integers(0, self.grid_size, size=2)

        # Initialize goal position (different from agent)
        self._goal_position = self.np_random.integers(0, self.grid_size, size=2)
        while np.array_equal(self._agent_position, self._goal_position):
            self._goal_position = self.np_random.integers(0, self.grid_size, size=2)

        observation = self._get_obs()
        info = self._get_info()

        return observation, info

    def step(self, action):
        """
        Execute one step in the environment.

        Args:
            action: Action to take

        Returns:
            observation: New observation
            reward: Reward for this step
            terminated: Whether episode has ended (goal reached)
            truncated: Whether episode was truncated (time limit, etc.)
            info: Additional information dictionary
        """
        # Map action to direction (0: up, 1: down, 2: left, 3: right)
        direction = np.array([
            [-1, 0],  # up
            [1, 0],   # down
            [0, -1],  # left
            [0, 1],   # right
        ])[action]

        # Update agent position (clip to stay within grid)
        self._agent_position = np.clip(
            self._agent_position + direction,
            0,
            self.grid_size - 1,
        )

        # Check if goal is reached
        terminated = np.array_equal(self._agent_position, self._goal_position)

        # Calculate reward
        if terminated:
            reward = 1.0  # Goal reached
        else:
            # Negative reward based on distance to goal (encourages efficiency)
            distance = np.linalg.norm(self._agent_position - self._goal_position)
            reward = -0.1 * distance

        # Episode not truncated in this example (no time limit)
        truncated = False

        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, truncated, info

    def _get_obs(self):
        """
        Get current observation.

        Returns:
            observation: Current state as defined by observation_space
        """
        # Return agent position as observation
        return self._agent_position.astype(np.float32)

        # For dict observations:
        # return {
        #     "agent": self._agent_position.astype(np.float32),
        #     "goal": self._goal_position.astype(np.float32),
        # }

    def _get_info(self):
        """
        Get additional information (for debugging/logging).

        Returns:
            info: Dictionary with additional information
        """
        return {
            "agent_position": self._agent_position,
            "goal_position": self._goal_position,
            "distance_to_goal": np.linalg.norm(
                self._agent_position - self._goal_position
            ),
        }

    def render(self):
        """
        Render the environment.

        Returns:
            Rendered frame (if render_mode is 'rgb_array')
        """
        if self.render_mode == "human":
            # Print simple text-based rendering
            grid = np.zeros((self.grid_size, self.grid_size), dtype=str)
            grid[:, :] = "."
            grid[tuple(self._agent_position)] = "A"
            grid[tuple(self._goal_position)] = "G"

            print("\n" + "=" * (self.grid_size * 2 + 1))
            for row in grid:
                print(" ".join(row))
            print("=" * (self.grid_size * 2 + 1) + "\n")

        elif self.render_mode == "rgb_array":
            # Return RGB array for video recording
            # This is a placeholder - implement proper rendering as needed
            canvas = np.zeros((
                self.grid_size * 50,
                self.grid_size * 50,
                3
            ), dtype=np.uint8)
            # Draw agent and goal on canvas
            # ... (implement visual rendering)
            return canvas

    def close(self):
        """
        Clean up environment resources.
        """
        pass


# Optional: Register the environment with Gymnasium
# This allows creating the environment with gym.make("CustomEnv-v0")
gym.register(
    id="CustomEnv-v0",
    entry_point=__name__ + ":CustomEnv",
    max_episode_steps=100,
)


def validate_environment():
    """
    Validate the custom environment with SB3's env_checker.
    """
    from stable_baselines3.common.env_checker import check_env

    print("Validating custom environment...")
    env = CustomEnv()
    check_env(env, warn=True)
    print("Environment validation passed!")


def test_environment():
    """
    Test the custom environment with random actions.
    """
    print("Testing environment with random actions...")
    env = CustomEnv(render_mode="human")

    obs, info = env.reset()
    print(f"Initial observation: {obs}")
    print(f"Initial info: {info}")

    for step in range(10):
        action = env.action_space.sample()  # Random action
        obs, reward, terminated, truncated, info = env.step(action)

        print(f"\nStep {step + 1}:")
        print(f"  Action: {action}")
        print(f"  Observation: {obs}")
        print(f"  Reward: {reward:.3f}")
        print(f"  Terminated: {terminated}")
        print(f"  Info: {info}")

        env.render()

        if terminated or truncated:
            print("Episode finished!")
            break

    env.close()


def train_on_custom_env():
    """
    Train a PPO agent on the custom environment.
    """
    from stable_baselines3 import PPO

    print("Training PPO agent on custom environment...")

    # Create environment
    env = CustomEnv()

    # Validate first
    from stable_baselines3.common.env_checker import check_env
    check_env(env, warn=True)

    # Train agent
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)

    # Test trained agent
    obs, info = env.reset()
    for _ in range(20):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            print(f"Goal reached! Final reward: {reward}")
            break

    env.close()


if __name__ == "__main__":
    # Validate the environment
    validate_environment()

    # Test with random actions
    # test_environment()

    # Train an agent
    # train_on_custom_env()
```

### `scripts/evaluate_agent.py`

```python
"""
Template script for evaluating trained RL agents with Stable Baselines3.

This template demonstrates:
- Loading trained models
- Evaluating performance with statistics
- Recording videos of agent behavior
- Visualizing agent performance
"""

import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.vec_env import DummyVecEnv, VecVideoRecorder, VecNormalize
import os


def evaluate_agent(
    model_path,
    env_id="CartPole-v1",
    n_eval_episodes=10,
    deterministic=True,
    render=False,
    record_video=False,
    video_folder="./videos/",
    vec_normalize_path=None,
):
    """
    Evaluate a trained RL agent.

    Args:
        model_path: Path to the saved model
        env_id: Gymnasium environment ID
        n_eval_episodes: Number of episodes to evaluate
        deterministic: Use deterministic actions
        render: Render the environment during evaluation
        record_video: Record videos of the agent
        video_folder: Folder to save videos
        vec_normalize_path: Path to VecNormalize statistics (if used during training)

    Returns:
        mean_reward: Mean episode reward
        std_reward: Standard deviation of episode rewards
    """
    # Load the trained model
    print(f"Loading model from {model_path}...")
    model = PPO.load(model_path)

    # Create evaluation environment
    if render:
        env = gym.make(env_id, render_mode="human")
    else:
        env = gym.make(env_id)

    # Wrap in DummyVecEnv for consistency
    env = DummyVecEnv([lambda: env])

    # Load VecNormalize statistics if they were used during training
    if vec_normalize_path and os.path.exists(vec_normalize_path):
        print(f"Loading VecNormalize statistics from {vec_normalize_path}...")
        env = VecNormalize.load(vec_normalize_path, env)
        env.training = False  # Don't update statistics during evaluation
        env.norm_reward = False  # Don't normalize rewards during evaluation

    # Set up video recording if requested
    if record_video:
        os.makedirs(video_folder, exist_ok=True)
        env = VecVideoRecorder(
            env,
            video_folder,
            record_video_trigger=lambda x: x == 0,  # Record all episodes
            video_length=1000,  # Max video length
            name_prefix=f"eval-{env_id}",
        )
        print(f"Recording videos to {video_folder}...")

    # Evaluate the agent
    print(f"Evaluating for {n_eval_episodes} episodes...")
    mean_reward, std_reward = evaluate_policy(
        model,
        env,
        n_eval_episodes=n_eval_episodes,
        deterministic=deterministic,
        render=False,  # VecEnv doesn't support render parameter
        return_episode_rewards=False,
    )

    print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")

    # Cleanup
    env.close()

    return mean_reward, std_reward


def watch_agent(
    model_path,
    env_id="CartPole-v1",
    n_episodes=5,
    deterministic=True,
    vec_normalize_path=None,
):
    """
    Watch a trained agent play (with rendering).

    Args:
        model_path: Path to the saved model
        env_id: Gymnasium environment ID
        n_episodes: Number of episodes to watch
        deterministic: Use deterministic actions
        vec_normalize_path: Path to VecNormalize statistics (if used during training)
    """
    # Load the trained model
    print(f"Loading model from {model_path}...")
    model = PPO.load(model_path)

    # Create environment with rendering
    env = gym.make(env_id, render_mode="human")

    # Load VecNormalize statistics if needed
    obs_normalization = None
    if vec_normalize_path and os.path.exists(vec_normalize_path):
        print(f"Loading VecNormalize statistics from {vec_normalize_path}...")
        # For rendering, we'll manually apply normalization
        dummy_env = DummyVecEnv([lambda: gym.make(env_id)])
        vec_env = VecNormalize.load(vec_normalize_path, dummy_env)
        obs_normalization = vec_env
        dummy_env.close()

    # Run episodes
    for episode in range(n_episodes):
        obs, info = env.reset()
        episode_reward = 0
        done = False
        step = 0

        print(f"\nEpisode {episode + 1}/{n_episodes}")

        while not done:
            # Apply observation normalization if needed
            if obs_normalization:
                obs_normalized = obs_normalization.normalize_obs(obs)
            else:
                obs_normalized = obs

            # Get action from model
            action, _states = model.predict(obs_normalized, deterministic=deterministic)

            # Take step in environment
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            episode_reward += reward
            step += 1

        print(f"Episode reward: {episode_reward:.2f} ({step} steps)")

    env.close()


def compare_models(
    model_paths,
    env_id="CartPole-v1",
    n_eval_episodes=10,
    deterministic=True,
):
    """
    Compare performance of multiple trained models.

    Args:
        model_paths: List of paths to saved models
        env_id: Gymnasium environment ID
        n_eval_episodes: Number of episodes to evaluate each model
        deterministic: Use deterministic actions
    """
    results = {}

    for model_path in model_paths:
        print(f"\nEvaluating {model_path}...")
        mean_reward, std_reward = evaluate_agent(
            model_path,
            env_id=env_id,
            n_eval_episodes=n_eval_episodes,
            deterministic=deterministic,
        )
        results[model_path] = {"mean": mean_reward, "std": std_reward}

    # Print comparison
    print("\n" + "=" * 60)
    print("Model Comparison Results")
    print("=" * 60)
    for model_path, stats in results.items():
        print(f"{model_path}: {stats['mean']:.2f} +/- {stats['std']:.2f}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    # Example 1: Evaluate a trained model
    model_path = "./models/best_model/best_model.zip"
    evaluate_agent(
        model_path=model_path,
        env_id="CartPole-v1",
        n_eval_episodes=10,
        deterministic=True,
    )

    # Example 2: Record videos of agent behavior
    # evaluate_agent(
    #     model_path=model_path,
    #     env_id="CartPole-v1",
    #     n_eval_episodes=5,
    #     deterministic=True,
    #     record_video=True,
    #     video_folder="./videos/",
    # )

    # Example 3: Watch agent play with rendering
    # watch_agent(
    #     model_path=model_path,
    #     env_id="CartPole-v1",
    #     n_episodes=3,
    #     deterministic=True,
    # )

    # Example 4: Compare multiple models
    # compare_models(
    #     model_paths=[
    #         "./models/model_100k.zip",
    #         "./models/model_200k.zip",
    #         "./models/best_model/best_model.zip",
    #     ],
    #     env_id="CartPole-v1",
    #     n_eval_episodes=10,
    # )

    # Example 5: Evaluate with VecNormalize statistics
    # evaluate_agent(
    #     model_path="./models/best_model/best_model.zip",
    #     env_id="Pendulum-v1",
    #     n_eval_episodes=10,
    #     vec_normalize_path="./models/vec_normalize.pkl",
    # )
```

### `scripts/train_rl_agent.py`

```python
"""
Template script for training RL agents with Stable Baselines3.

This template demonstrates best practices for:
- Setting up training with proper monitoring
- Using callbacks for evaluation and checkpointing
- Vectorized environments for efficiency
- TensorBoard integration
- Model saving and loading
"""

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import (
    EvalCallback,
    CheckpointCallback,
    CallbackList,
)
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
import os


def train_agent(
    env_id="CartPole-v1",
    algorithm=PPO,
    policy="MlpPolicy",
    n_envs=4,
    total_timesteps=100000,
    eval_freq=10000,
    save_freq=10000,
    log_dir="./logs/",
    save_path="./models/",
):
    """
    Train an RL agent with best practices.

    Args:
        env_id: Gymnasium environment ID
        algorithm: SB3 algorithm class (PPO, SAC, DQN, etc.)
        policy: Policy type ("MlpPolicy", "CnnPolicy", "MultiInputPolicy")
        n_envs: Number of parallel environments
        total_timesteps: Total training timesteps
        eval_freq: Frequency of evaluation (in timesteps)
        save_freq: Frequency of model checkpoints (in timesteps)
        log_dir: Directory for logs and TensorBoard
        save_path: Directory for model checkpoints
    """
    # Create directories
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(save_path, exist_ok=True)
    eval_log_dir = os.path.join(log_dir, "eval")
    os.makedirs(eval_log_dir, exist_ok=True)

    # Create training environment (vectorized for efficiency)
    print(f"Creating {n_envs} parallel training environments...")
    env = make_vec_env(
        env_id,
        n_envs=n_envs,
        vec_env_cls=SubprocVecEnv,  # Use SubprocVecEnv for parallel execution
        # vec_env_cls=DummyVecEnv,  # Use DummyVecEnv for lightweight environments
    )

    # Optional: Add normalization wrapper for better performance
    # Uncomment for continuous control tasks
    # env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.0)

    # Create separate evaluation environment
    print("Creating evaluation environment...")
    eval_env = make_vec_env(env_id, n_envs=1)
    # If using VecNormalize, wrap eval env but set training=False
    # eval_env = VecNormalize(eval_env, training=False, norm_reward=False)

    # Set up callbacks
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=os.path.join(save_path, "best_model"),
        log_path=eval_log_dir,
        eval_freq=eval_freq // n_envs,  # Adjust for number of environments
        n_eval_episodes=10,
        deterministic=True,
        render=False,
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=save_freq // n_envs,  # Adjust for number of environments
        save_path=save_path,
        name_prefix="rl_model",
        save_replay_buffer=False,  # Set True for off-policy algorithms if needed
    )

    callback = CallbackList([eval_callback, checkpoint_callback])

    # Initialize the agent
    print(f"Initializing {algorithm.__name__} agent...")
    model = algorithm(
        policy,
        env,
        verbose=1,
        tensorboard_log=log_dir,
        # Algorithm-specific hyperparameters can be added here
        # learning_rate=3e-4,
        # n_steps=2048,  # For PPO/A2C
        # batch_size=64,
        # gamma=0.99,
    )

    # Train the agent
    print(f"Training for {total_timesteps} timesteps...")
    model.learn(
        total_timesteps=total_timesteps,
        callback=callback,
        tb_log_name=f"{algorithm.__name__}_{env_id}",
    )

    # Save final model
    final_model_path = os.path.join(save_path, "final_model")
    print(f"Saving final model to {final_model_path}...")
    model.save(final_model_path)

    # Save VecNormalize statistics if used
    # env.save(os.path.join(save_path, "vec_normalize.pkl"))

    print("Training complete!")
    print(f"Best model saved at: {os.path.join(save_path, 'best_model')}")
    print(f"Final model saved at: {final_model_path}")
    print(f"TensorBoard logs: {log_dir}")
    print(f"Run 'tensorboard --logdir {log_dir}' to view training progress")

    # Cleanup
    env.close()
    eval_env.close()

    return model


if __name__ == "__main__":
    # Example: Train PPO on CartPole
    train_agent(
        env_id="CartPole-v1",
        algorithm=PPO,
        policy="MlpPolicy",
        n_envs=4,
        total_timesteps=100000,
    )

    # Example: Train SAC on continuous control task
    # from stable_baselines3 import SAC
    # train_agent(
    #     env_id="Pendulum-v1",
    #     algorithm=SAC,
    #     policy="MlpPolicy",
    #     n_envs=4,
    #     total_timesteps=50000,
    # )

    # Example: Train DQN on discrete task
    # from stable_baselines3 import DQN
    # train_agent(
    #     env_id="LunarLander-v3",
    #     algorithm=DQN,
    #     policy="MlpPolicy",
    #     n_envs=1,  # DQN typically uses single env
    #     total_timesteps=100000,
    # )
```
