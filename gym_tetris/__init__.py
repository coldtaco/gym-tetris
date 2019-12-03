import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='Tetris-v0',
    entry_point='gym_tetris.envs:Tetris',
    max_episode_steps=100000,
    reward_threshold=99999999999,
    nondeterministic = True,
)
register(
    id='Tetris-v1',
    entry_point='gym_tetris.envs:TetrisSimple',
    max_episode_steps=100000,
    reward_threshold= 9999999999,
    nondeterministic = True,
)