class LinkStateDB:
    def __init__(self, router):
        self.router = router
        self.neighbours = router.connections.copy().values()

    def copy(self):
        return LinkStateDB(self.router)
