class LinkStateDB:
    def __init__(self, router):
        self.router = router
        self.neighbours = router.connections.copy()

    def copy(self):
        return LinkStateDB(self.router)
