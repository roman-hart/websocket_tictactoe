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
        self.players = None, None  # self / opponent
        self._[self.id] = self

    async def register(self, msg):
        if msg and msg.isalpha():
            print('registred')
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
            self.game = opponent.game = Game()
            self.players = opponent.players = self, opponent
            await opponent.ws.send(f'You were invited to the game wish {self.name}')
            return True

    async def answer(self, msg):
        num = self.game.step % 2
        if self.players[num] != self:
            return 'Now we are waiting for your opponent to move!'
        waiting_player = self.players[abs(num - 1)]
        er = self.game.check_move_str(msg)
        if er:
            return er
        message = await self.game.move(int(msg)-1)
        if waiting_player:
            if waiting_player != self:
                await waiting_player.ws.send(message + '\nYour move:')
            else:
                message += f'\nYour move again:'
        else:
            message += await self.game.move(self.game.smart_move(self.game.m, *self.game.sets[num]))
            message += '\nYour next move: '
        return message

    @staticmethod
    async def processing():
        while True:
            for u in User._.values():
                await u.ws.send('ping')
            await asyncio.sleep(15)

    @staticmethod
    async def send_id(id_, msg):
        await User._[id_].ws.send(msg)

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
            ans += u.name + ' \n'
        ans += 'Bot \n'
        return ans


async def processing(ws, path):
    async for message in ws:
        j = json.loads(message)
        print(json.dumps(j))
        u = await User.get(j['id'], ws)
        msg = j['message'].lower()
        if not u.game:
            ans = 'Who do you want to play with? Type their name\n' + await User.names_str()
            if not u.name or u.name == 'User':
                if await u.register(msg):
                    msg += '1'
                    ans += u.name
                else:
                    ans = 'What is your name?'
            elif await u.connect(msg):
                ans = f'Successfully connected. Insert \'exit\' if you want leave the game.\n' \
                          f'Now make your first move (send a number from 1 to 9):'
        elif msg == 'exit':
            opponent = u.players[0] if u.players[0] != u else u.players[1]
            ans = 'You has escaped the game...'
            u.game = opponent.game = None
            u.players = opponent.players = None, None
            if opponent and opponent != u:
                await opponent.ws.send(u.name + ' has escaped the game...')
                opponent.game = None
                opponent.players = None, None
        else:
            ans = await u.answer(msg)
        await u.ws.send(ans)


if __name__ == '__main__':
    start_server = websockets.serve(processing, "0.0.0.0", 8888)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(start_server, User.processing()))
    loop.run_forever()
