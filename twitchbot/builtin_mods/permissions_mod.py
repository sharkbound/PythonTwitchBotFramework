from twitchbot import Mod, perms, Message, Command


class PermissionsMod(Mod):
    name = 'permissions_mod'

    async def on_permission_check(self, msg: Message, cmd: Command) -> bool:
        if not cmd.permission:
            return True

        return perms.has_permission(msg.channel_name, msg.author, cmd.permission)
