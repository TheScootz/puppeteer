config = {
    # List of props to include, with any initialization parameters.
    'stageprops': {
        'baseutils': {},
        'chanutils': {
            'admin': {
                'username': 'root',
                'hostname': 'example.org',
            },
        },
        'logutils': {},
    },
    # Global configuration inheritted by puppets.  Any values
    # not overwritten individually will be used by the puppets.
    'global': {
        
    },
    # Unique name of the puppet and its individual configuration.
    # Global configuration is inherited.
    'puppets': {
        'Marionette': {
            # Host and port that this puppet uses to connect.
            'host': "irc.network.org",
            'port': 6667,
            # List of nicknames to try. The '?' character is replaced
            # with a random number in range 0-9 inclusive.
            'nickname': [
                "Marionette",
                "Puppet??",
                "Puppet???",
            ],
            # Username and realname to provide on connection.
            'username': "m???",
            'realname': "Strings attached",
            # List of channels to join on connection.
            'channels': [
                "#puppetshow",
            ],
            # List of enabled stageprops for the puppet.
            # Each can use per-puppet configuration as well as
            # global configuration.
            # Props configurations listed here must be included
            # in the 'stageprops' option to have any effect.
            'stageprops': {
                'baseutils': {},
                'chanutils': {},
                'logutils': {},
            }
        }
    },
}

