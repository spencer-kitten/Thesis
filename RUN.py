from Simulator import *


def RUN(n_targets, n_merchants, n_submarines, seeds, max_samples,plots = False, gif = False, tweet = False):
    '''n_targets,n_merchants,n_submarines,seeds,max_samples,tweet = False
    files exported to Killed_Targets.csv'''

    # Set number of replications
    max_samples = seeds + max_samples

    while seeds < max_samples:
        '''Runs a simulation instance. Appends data to Killed_Targets.csv. '''

        Targets, Merchants, Submarines = Simulator(n_targets,n_merchants,n_submarines,12,1e5,plots,gif,seeds)

        Killed_Targets = {}
        for sub in Submarines:
            Killed_Targets[str(sub.indexer)] = len(sub.tracked)

        Killed_Targets = pd.DataFrame(Killed_Targets, index = [0])
        Killed_Targets.to_csv('Killed_Targets.csv', mode = 'a')
        seeds += 1

        # Printing for status updates for user
        status_string = ("Run %d complete" % seeds)
        print(status_string)

    # Concatenate data and save
    Killed_Targets = pd.read_csv('Killed_Targets.csv')
    Killed_Targets = Killed_Targets.iloc[::2]
    Killed_Targets = Killed_Targets.reset_index()
    Killed_Targets = Killed_Targets.drop(['Unnamed: 0', 'index'], axis = 1)
    Killed_Targets.to_csv('Killed_Targets.csv', mode = 'w')

    # Update Spencer
    if tweet == True:
        status_string = ("Run complete")
        api.update_status(status_string)
