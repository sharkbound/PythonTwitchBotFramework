from .baseapi import Api
from ..enums import UserType
from .. import util


class UserInfoApi(Api):
    def __init__(self, client_id: str, user: str):
        super().__init__(client_id, user)

        self.id = 0
        self.login = ''
        self.display_name = ''
        self.type = UserType.NORMAL
        self.description = ''
        self.profile_image_url = ''
        self.offline_image_url = ''
        self.view_count = ''

    async def update(self, log=False):
        data = await util.get_user_data(self.user, self.headers)

        try:
            self.id = data['id']
            self.login = data['login']
            self.display_name = data['display_name']
            self.type = UserType(data['type'])
            self.description = data['description']
            self.profile_image_url = data['profile_image_url']
            self.offline_image_url = data['offline_image_url']
            self.view_count = data['view_count']

        except KeyError:
            if log:
                print(f'[USER INFO API] failed to update data for {self.user}')
