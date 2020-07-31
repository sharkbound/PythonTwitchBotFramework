from typing import TYPE_CHECKING
from ..cached_property import cached_property

if TYPE_CHECKING:
    from twitchbot import PubSubData

__all__ = [
    'PubSubPointRedemption'
]

class PubSubPointRedemption:
    def __init__(self, data: 'PubSubData'):
        self.data: 'PubSubData' = data

    @property
    def redemption_id(self) -> str:
        return self.data.channel_point_redemption_dict.get('id', '')

    @cached_property
    def user_dict(self) -> dict:
        return self.data.channel_point_redemption_dict.get('user', {})

    @property
    def user_id(self) -> str:
        return self.user_dict.get('id', '')

    @property
    def user_login_name(self) -> str:
        return self.user_dict.get('login', '')

    @property
    def user_display_name(self) -> str:
        return self.user_dict.get('display_name', '')

    @property
    def channel_id(self) -> str:
        return self.data.channel_point_redemption_dict.get('channel_id', '')

    @cached_property
    def reward_dict(self) -> dict:
        return self.data.channel_point_redemption_dict.get('reward', {})

    @property
    def reward_id(self) -> str:
        return self.reward_dict.get('id', '')

    @property
    def reward_channel_id(self) -> str:
        return self.reward_dict.get('channel_id', '')

    @property
    def reward_title(self) -> str:
        return self.reward_dict.get('title', '')

    @property
    def reward_prompt(self) -> str:
        return self.reward_dict.get('prompt', '')

    @property
    def reward_cost(self) -> int:
        return self.reward_dict.get('cost', 0)

    @property
    def is_reward_user_input_required(self) -> bool:
        return self.reward_dict.get('is_user_input_required', False)

    @property
    def is_reward_sub_only(self) -> bool:
        return self.reward_dict.get('is_sub_only', False)

    @property
    def reward_image(self) -> str:
        return self.reward_dict.get('image', '') or ''

    @cached_property
    def default_image_dict(self) -> dict:
        return self.reward_dict.get('default_image', {})

    @property
    def default_image_1x(self) -> str:
        return self.default_image_dict.get('url_1x', '') or ''

    @property
    def default_image_2x(self) -> str:
        return self.default_image_dict.get('url_2x', '') or ''

    @property
    def default_image_4x(self) -> str:
        return self.default_image_dict.get('url_4x', '') or ''

    @property
    def reward_background_color(self) -> str:
        return self.reward_dict.get('background_color', '')

    @property
    def is_reward_enabled(self) -> bool:
        return self.reward_dict.get('is_enabled', False)

    @property
    def is_reward_paused(self) -> bool:
        return self.reward_dict.get('is_paused', False)

    @property
    def is_reward_in_stock(self) -> bool:
        return self.reward_dict.get('is_in_stock', False)

    @property
    def should_reward_redemption_skip_request_queue(self) -> bool:
        return self.reward_dict.get('should_redemptions_skip_request_queue', False)

    @property
    def reward_template_id(self) -> str:
        return self.reward_dict.get('template_id', '') or ''

    @property
    def redemption_status(self) -> str:
        return self.data.channel_point_redemption_dict.get('status', '')

    @property
    def is_reward_max_per_stream_enabled(self) -> bool:
        return self.reward_dict.get('max_per_stream', {}).get('is_enabled', False)

    @property
    def reward_max_per_stream(self) -> int:
        return self.reward_dict.get('max_per_stream', {}).get('max_per_stream', 0)
