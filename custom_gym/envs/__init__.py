from gym.envs.registration import register

register(id='SkiingGame-v0',
	entry_point='envs.custom_env_dir:SkiingGame'
)
