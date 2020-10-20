import asyncio
import json
import websockets
from tictactoe import Game


class User:
    _ = dict()

    def __init__(self, id_, webs):
        self.id = id_
        self.ws = webs
        self.name = 'User'
        self.game = None
        self.players = None, None  # first player / second player
        self._[self.id] = self

    async def register(self, msg):
        if msg and msg.isalpha():
            self.name = msg.capitalize()
            return True

    async def connect(self, msg):
        if msg == 'bot':
            self.game = Game()
            self.players = self, 0
            return True
        opponent = None
        for u in User._.values():
            if u.name.lower() == msg and not u.game:
                opponent = u
        if opponent:
            await opponent.send(f'You were invited to the game with {self.name}')
            self.game = opponent.game = Game()
            self.players = opponent.players = self, opponent
            return True

    async def answer(self, msg):
        n = self.game.step % 2
        if self.players[n] != self:
            return 'Now we are waiting for your opponent to move!'
        waiting_player = self.players[abs(n - 1)]
        er = self.game.check_move_str(msg)
        if er:
            return er
        message = await self.game.move(int(msg)-1)
        if waiting_player:
            await waiting_player.send(message + 'Your move:' if self.game.step % 2 != n else message)
        else:
            message += await self.game.move(self.game.smart_move(self.game.m, *self.game.sets[not n])) + '\nYour move: '
        return message + 'Your move:' if self.game.step % 2 == n else message

    async def disconnect(self):
        opponent = self.players[int(not self.players.index(self))]
        if opponent:
            await User._disconnect(opponent)
            await opponent.send(f'{self.name} has escaped the game.')
        await User._disconnect(self)
        return 'You have escaped the game.'

    async def send(self, msg):
        if self.ws:
            try:
                await self.ws.send(msg)
            except:
                try:
                    opponent = self.players[int(not self.players.index(self))]
                    await User._disconnect(self)
                    if opponent:
                        await User._disconnect(opponent)
                        await opponent.ws.send(f'We\'ve lost connection with {self.name}...')
                        User._.pop(self.id)
                except:
                    pass  # User._.pop(opponent.id)

    @staticmethod
    async def _disconnect(u):
        u.game = None
        u.players = None, None

    @staticmethod
    async def processing():
        while True:
            for u in User._.values():
                await u.send('ping')
            await asyncio.sleep(15)

    @staticmethod
    async def get(id_, ws=None):
        if id_ not in User._:
            User(id_, ws)
        u = User._[id_]
        if ws:
            u.ws = ws
        return u

    @staticmethod
    async def names_str():
        ans = 'Here you can see all our available for game users:\n'
        for u in User._.values():
            if u.game or not u.name or u.name == 'User':
                continue
            ans += '-> ' + u.name + ' \n'
        ans += '-> Bot \n'
        return ans


async def processing(ws, path):
    async for message in ws:
        try:
            j = json.loads(message)
            u = await User.get(j['id'], ws)
            msg = j['message'].lower()
            if not u.game:
                ans = 'Who do you want to play with? Type their name or wait till someone invites you.\n' \
                      + await User.names_str()
                if not u.name or u.name == 'User':
                    if await u.register(msg):
                        msg += '1'
                        ans += '-> ' + u.name + '\n'
                    else:
                        ans = 'What is your name? Text only.'
                elif await u.connect(msg):
                    ans = f'Successfully connected. Insert \'exit\' if you want leave the game.\n' \
                              f'Now make your first move (send a number from 1 to 9):'
            elif msg == 'exit':
                ans = await u.disconnect()
            else:
                ans = await u.answer(msg)
            await u.send(ans)
        except json.decoder.JSONDecodeError:
            await ws.send('Error: Message should contain json objects!')
        except KeyError:
            await ws.send('Error: PLease, be aware to include \'id\' and \'message\' keys in your message!')


if __name__ == '__main__':
    start_server = websockets.serve(processing, "0.0.0.0", 8888)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(start_server, User.processing()))
    loop.run_forever()
