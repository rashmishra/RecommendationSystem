# Rex: SGX decentralized recommender
The source code for a decentralized recommender system that uses Intel SGX to ensure user privacy and shares data rather than models is available in this repository.

# Dependencies and compilation
If your machine has SGX support, you need the [Intel SGX SDK](https://01.org/intel-software-guard-extensions) to run Rex. Used version [2.9.1](https://01.org/intel-softwareguard-extensions/downloads/intel-sgx-linux-2.9.1-release).
To use remote attestation, you also need [DCAP](https://www.intel.com/content/www/us/en/developer/articles/guide/intel-software-guard-extensions-data-center-attestation-primitives-quick-install-guide.html). Used version [1.8](https://01.org/intel-softwareguard-extensions/downloads/intel-sgx-dcap-1.8-release).

Alternatively, you may still test a non-SGX version of Rex (without security or attestation) and a simulation environment of the same decentralized recommender if you do not have access to SGX servers.

On Ubuntu, you can meet all non-SGX requirements with the following command:
```
$ sudo apt install build-essential libboost-all-dev libzmq3-dev
```
Be sure that you have also fetched the submodules:
```
git submodule update --init --recursive
```
To compile, simple type:
```
$ make
```

# SGX Decentralized recommender
```
$ ./bin/rex -?
Usage: rex [OPTION...]
Rex SGX Recommender: data sharing inside enclaves

  -d, --dpsgd                Switch to DPSGD. Default: RMW.
  -e, --epochs=howmany       Number of epochs. Deafult 10.
  -f, --filename=filename    Input data file.
  -h, --share_howmany=howmany   Number of ratings shared by node in each
                             iteration.
  -l, --local=number         Local iterations. Default: 1.
  -m, --machines="host1 host2:port2 [...]"
                             List of machines in host:port format, separated by
                             space and enclosed by quotes. In case no port is
                             provided, default port 4444 is assumed. All nodes
                             should provide this list in the same order.
  -p, --port=port            Listening port
  -s, --sharedata            Share raw data.
  -u, --steps_per_iteration=steps
                             Number of local steps in each iteration or epoch.
  -x, --disable_model_sharing   Disable sharing of models. Enables data sharing
                             by default.
  -?, --help                 Give this help list
      --usage                Give a short usage message
  -V, --version              Print program version
```

# Decentralized recommender: simulation environment
```
$ ./bin/local_decentralized_training -?
Usage: local_decentralized_training [OPTION...]
MF decentralized training: PoC to check implementation correctness

  -d, --dpsgd                Switch to DPSGD. Default: RMW.
  -e, --epochs=howmany       Number of epochs. Deafult 100.
  -f, --filename=filename    Input data file.
  -h, --share_howmany=howmany   Number of ratings shared by node in each
                             iteration.
  -l, --local=number         Local iterations. Default: 1.
  -m, --sharedmemory         Switch to shared memory communication. You cannot
                             get network measurements in this mode.
  -n, --num_nodes=num_nodes  Number of nodes in the graph.
  -o, --outdir=directory     Output log directory. Default 'out'.
  -r, --randomgraph          Switch to Random Graph. Default: Small World.
  -s, --sharedata            Share raw data.
  -u, --steps_per_iteration=steps
                             Number of local steps in each iteration or epoch.
  -x, --disable_model_sharing   Disable sharing of models. Enables data sharing
                             by default.
  -?, --help                 Give this help list
      --usage                Give a short usage message
  -V, --version              Print program version
```


# Code
Rashmi Mishra
