# The sad network

There are two "servers" being run in the current project:
1. Kademlia DHT server storing `username -> ip:port` pairs
2. HTTP server written in django to serve profile content

The django project is located in `http_server`, and is following the
django tutorial.

`kad_server.py` holds the kademlia server, which just tells us what
URL to perform our REST api requests against.

# Running the code

`sad.py` is the gateway to launching the entire application. It
launches both of the servers mentioned above as separate processes. It
relies on reading a toml file to know what mode to launch in, and what
user to connect as.

Configurations can be found in `profile/*.toml`. A *bootstrap*
configuration needs to be run first, the rest of the configurations
should be set to *join*.

The `cwheezer.toml` config is a bootstrap example, and `jneutron.toml`
is a join example. Run cwheezer first.

The run command is trivial:
```
PYTHONPATH=. python3.7 sad.py /Users/AShafer/csc/CSC724/playground/profile/cwheezer.toml
```

*NOTE*: for simplicity the path to the config file should be an
 *absolute* path. Things are still a little rough around the edges.

*Note*: for now this needs to be run from this directory, the
 `PYTHONPATH` will tell the http server where to find `kad_client`.

The kademlia client will be axed soon, so eventually this will not be
needed.

# Configuration

More options soon to follow.

## Bootstrapping a new network
Let's walk through an example config, `cwheezer.toml`:

```
[account]
username='cwheezer'
fullname='Carl Wheezer'

[connection]
action='bootstrap'
network_port=7777
profile_port=8000
```

The account section outlines who we are. `username` is important, it
is the name you are accessable on the network with. This and the
`fullname` are what other users will see you as.

The connection section tells the program:
* What the `action` we should perform is. In this case we want to
bootstrap (create) a new network without any other users.
* The `network_port` that the Kademlia server should be reachable on.
* The `profile_port` that the HTTP server should listen on. It will
listen on `0.0.0.0:profile_port`.

## Joining a network
Let's walk through an example config, `cwheezer.toml`:

```
[account]
username='jneutron'
fullname='Jimmy Neutron'

[connection]
action='join'
network_port=7778
profile_port=8001
neighbor_ip='localhost'
neighbor_port=7777
```

Most of the options are the exact same as the bootstrap example, but
there are a few new ones.

The neighbor node is the node we want to join off of. We need to know
the node in advance, realistically this means you should know the
other human and they told you their ip/port.
* `neighbor_ip` - the ip address of the node to join
* `neighbor_port` - the port of the *kademlia* server of the node to
join.
 * This should be the same as the neighbor node's `network_port`.