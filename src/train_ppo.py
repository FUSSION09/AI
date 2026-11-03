"""
Phase 3: PPO Reinforcement Learning Agent Training & Evaluation
Trains the primary execution agent using Stable-Baselines3 PPO on the custom Gymnasium environment.
All checkpoints and logs stored strictly inside d:\AI.
"""

from pathlib import Path
import numpy as np
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor

from config import CHECKPOINTS_DIR, BASE_DIR
from rl_environment import OperationalTaskEnv

MODEL_SAVE_PATH = CHECKPOINTS_DIR / "ppo_operational_agent"

def train_ppo_agent(total_timesteps: int = 25000):
    print(f"[Phase 3] Instantiating custom Gymnasium environment...")
    raw_env = OperationalTaskEnv()
    env = Monitor(raw_env)

    print(f"[Phase 3] Configuring PPO Policy (MlpPolicy, clip_range=0.2, lr=3e-4)...")
    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        verbose=1,
    )

    print(f"[Phase 3] Starting PPO training for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps)

    # Save model
    print(f"[Phase 3] Saving trained PPO model to: {MODEL_SAVE_PATH}.zip")
    model.save(str(MODEL_SAVE_PATH))

    return model, raw_env

def run_evaluation_episode(model, env: OperationalTaskEnv):
    print("\n" + "="*75)
    print("DEMONSTRATION RUN: PPO Policy Autonomous Strategy Execution")
    print("="*75)
    
    obs, info = env.reset()
    done = False
    total_reward = 0.0

    print("Initial State Observation:")
    env.render()
    print("-" * 75)

    step_count = 0
    while not done:
        step_count += 1
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(int(action))
        total_reward += reward
        done = terminated or truncated

        action_name = info["action_name"]
        print(f"[{step_count:02d}] Action Chosen: {action_name:<28} | Reward: {reward:+6.1f} | Outcome: {info['status']}")
        env.render()

    print("="*75)
    print(f"Episode Completed | Total Reward: {total_reward:.2f} | Final Status: {info['status']}")
    print("="*75)

if __name__ == "__main__":
    trained_model, eval_env = train_ppo_agent(total_timesteps=20000)
    run_evaluation_episode(trained_model, eval_env)

