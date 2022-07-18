class COMMS:
    '''Improved class to store data'''

    def __init__(self):
        self.target_info = {}

    def update_data(self,submarine,time_now,alive = True):
        self.target_info[submarine.indexer] = (submarine.alert_list[0].loc,time_now,alive)
