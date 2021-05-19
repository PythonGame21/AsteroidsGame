import shelve


class Save:
    def __init__(self):
        self.file = shelve.open('data')

    def save(self, game_state):
        self.file['game'] = game_state

    def get(self):
        return self.file['game']

    def __del__(self):
        self.file.close()
