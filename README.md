![docker image](https://github.com/exciting/sol-oasis/actions/workflows/docker-publish.yml/badge.svg)


# exciting's NOMAD Oasis Distribution

This is the NOMAD Oasis distribution of exciting.
Below are instructions for how to [deploy this distribution](#deploying-the-distribution)
and how to customize it through [adding plugins](#adding-a-plugin).

> [!IMPORTANT]
> Depending on the settings of the owner of this repository, the distributed image might
> be private and require authentication to pull.
> If you want to keep the image private you need to configure and use a personal access
> token (PAT) according to the instructions in the GitHub docs [here](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-with-a-personal-access-token-classic).
> If you want to make the image public (recommended), you should make sure that your
> organization settings allow public packages and make this package public after building it.
> You can read more about this in the GitHub docs [here](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility).

> [!TIP]
> In order for others to find and learn from your distribution we in FAIRmat would
> greatly appreciate it if you would add the topic `nomad-distribution` by clicking the
> ⚙️ next to "About" on the main GitHub page for this repository.

In this README you will find instructions for:
1. [Deploying the distribution](#deploying-the-distribution)
2. [Adding a plugin](#adding-a-plugin)
3. [Using the jupyter image](#the-jupyter-image)
4. [Updating the distribution from the template](#updating-the-distribution-from-the-template)
5. [Solving common issues](#faqtrouble-shooting)

## Access control

The NOMAD Oasis of the SOL group uses a list of allowed users to control access to the service. The NOMAD user names of allowed users are contained in a local file with the name `allowed-users.yaml`, which is stored in the `config` directory. To increase security, this file is not checked in to git. To create the `nomad.yaml` configuration file, please use the script `scripts/update_users.py`. It uses the template file `configs/nomad-template.yaml` and the users file `configs/allowed-users.yaml`, merges them, and **overwrites** `config/nomad.yaml`.

## Environment file

This configuration uses an `.env`-file. The parameters that need to be specified are:

```bash
CERT_LOCAL_PATH=<local_path_of_active_certificate_file>

MONGO_INITDB_ROOT_USERNAME=<admin_username_for_jobflow_mongo_db>
MONGO_INITDB_ROOT_PASSWORD=<admin_password_for_jobflow_mongo_db>
```

## Jobflow-remote database

This Oasis additionally runs a container for hosting a [`mongo` database](https://www.mongodb.com/) for [`jobflow remote`](https://matgenix.github.io/jobflow-remote/). The database is password protected and only registered users have access. To add users, please create the file `configs/jobflow-users.js` with the following content:

```js
db = db.getSiblingDB('<unique_database_name_for_user>');
if (!db.getUser("<user_name>")) {
  db.createUser({
    user: "<user_name>",
    pwd: "<user_password>",
    roles: [ { role: "readWrite", db: "<unique_database_name_for_user>" } ]
  });
} else {
  print("User already exists.");
}
```

For each user, add an individual block. Then, connect to the running container via:

```bash
docker exec -ti jobflow_db bash
```

and type in the console:

```bash
mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD
```

Then, load the user configuration file with:

```js
load('/jobflow/jobflow-users.js')
```

The script should create users that are missing and print to the console if the user exists. You can then leave the mongo shell by typing:

```js
exit
```

and leave the container by typing:

```bash
exit
```

To add more users later, just repeat the steps by adding the corresponding blocks to the file (`configs/jobflow-users.js`), restarting the container with:

```bash
docker restart jobflow_db
```

and following the steps above.

## Using the ssl configuration

By default, this Oasis uses SSL encrypted commutication. It uses the `nginx` configuration file `configs/nomad.ssl.conf`. In this example, a self-signed certificate is used. In a production evironment, replace the certificate and key names in `configs/nomad.ssl.conf` and `nginx.full.conf` with the actual key file names. 

## Deploying the distribution

Below are instructions for how to deploy this NOMAD Oasis distribution
[for a new Oasis](#for-a-new-oasis) and [for an existing Oasis](#for-an-existing-oasis)

### For a new Oasis

1. Make sure you have [docker](https://docs.docker.com/engine/install/) installed.
   Docker nowadays comes with `docker compose` built in. Prior, you needed to
   install the stand-alone [docker-compose](https://docs.docker.com/compose/install/).

2. Clone the repository or download the repository as a zip file.

    ```sh
    git clone https://github.com/exciting/sol-oasis.git
    cd sol-oasis
    ```

    or

    ```sh
    curl-L -o sol-oasis.zip "https://github.com/exciting/sol-oasis/archive/main.zip"
    unzip sol-oasis.zip
    cd sol-oasis
    ```

3. _On Linux only,_ recursively change the owner of the `.volumes` directory to the nomad user (1000)

    ```sh
    sudo chown -R 1000 .volumes
    ```

4. Pull the images specified in the `docker-compose.yaml`

    Note that the image needs to be public or you need to provide a PAT (see "Important" note above).

    ```sh
    docker compose pull
    ```

5. And run it with docker compose in detached (--detach or -d) mode

    ```sh
    docker compose up -d
    ```

6. Optionally you can now test that NOMAD is running with

    ```
    curl localhost/nomad-oasis/alive
    ```

7. Finally, open [http://localhost/nomad-oasis](http://localhost/nomad-oasis) in your browser to start using your new NOMAD Oasis.

#### Updating the image
1. Whenever you update your image you need to shut down NOMAD using

    ```sh
    docker compose down
    ```

    and then repeat steps 4. and 5. above.
   
2. You can remove unused images to free up space by running

    ```sh
    docker image prune -a
    ```

#### NOMAD Remote Tools Hub (NORTH)

To run NORTH (the NOMAD Remote Tools Hub), the `hub` container needs to run docker and
the container has to be run under the docker group. You need to replace the default group
id `991` in the `docker-compose.yaml`'s `hub` section with your systems docker group id.
Run `id` if you are a docker user, or `getent group | grep docker` to find your
systems docker gid. The user id 1000 is used as the nomad user inside all containers.

Please see the [Jupyter image](#the-jupyter-image) section below for more information on the jupyter NORTH image being generated in this repository.

You can find more details on setting up and maintaining an Oasis in the NOMAD docs here:
[nomad-lab.eu/prod/v1/docs/oasis/install.html](https://nomad-lab.eu/prod/v1/docs/oasis/install.html)

### For an existing Oasis

If you already have an Oasis running you only need to change the image being pulled in
your `docker-compose.yaml` with `ghcr.io/exciting/sol-oasis:main` for the services
`worker`, `app`, `north`, and `logtransfer`.

If you want to use the `nomad.yaml` from this repository you also need to comment out
the inclusion of the `nomad.yaml` under the volumes key of those services in the
`docker-compose.yaml`.

```yaml
volumes:
  # - ./configs/nomad.yaml:/app/nomad.yaml
```

To run the new image you can follow steps 5. and 6. [above](#for-a-new-oasis).

## Adding a plugin

To add a new plugin to the docker image you should add it to the plugins table in the [`pyproject.toml`](pyproject.toml) file.

Here you can put either plugins distributed to PyPI, e.g.

```toml
[project.optional-dependencies]
plugins = [
  "nomad-material-processing>=1.0.0",
]
```

or plugins in a git repository with either the commit hash

```toml
[project.optional-dependencies]
plugins = [
  "nomad-measurements @ git+https://github.com/FAIRmat-NFDI/nomad-measurements.git@71b7e8c9bb376ce9e8610aba9a20be0b5bce6775",
]
```

or with a tag

```toml
[project.optional-dependencies]
plugins = [
  "nomad-measurements @ git+https://github.com/FAIRmat-NFDI/nomad-measurements.git@v0.0.4"
]
```

To add a plugin in a subdirectory of a git repository you can use the `subdirectory` option, e.g.

```toml
[project.optional-dependencies]
plugins = [
  "ikz_pld_plugin @ git+https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas.git@30fc90843428d1b36a1d222874803abae8b1cb42#subdirectory=PVD/PLD/jeremy_ikz/ikz_pld_plugin"
]
```

Once the changes have been committed to the main branch, the new image will automatically
be generated.

## The Jupyter image

In addition to the Docker image for running the oasis, this repository also builds a custom NORTH image for running a jupyter hub with the installed plugins.
This image has been added to the [`configs/nomad.yaml`](configs/nomad.yaml) during the initialization of this repository and should therefore already be available in your Oasis under "Analyze / NOMAD Remote Tools Hub / jupyter"

The image is quite large and might cause a timeout the first time it is run. In order to avoid this you can pre pull the image with:

```
docker pull ghcr.io/exciting/sol-oasis/jupyter:main
```

If you want additional python packages to be available to all users in the jupyter hub you can add those to the jupyter table in the [`pyproject.toml`](pyproject.toml):

```toml
[project.optional-dependencies]
jupyter = [
  "voila",
  "ipyaggrid",
  "ipysheet",
  "ipydatagrid",
  "jupyter-flex",
]
```


## Updating the distribution from the template

In order to update an existing distribution with any potential changes in the template you can add a new `git remote` for the template and merge with that one while allowing for unrelated histories:

```
git remote add template https://github.com/FAIRmat-NFDI/nomad-distro-template
git fetch template
git merge template/main --allow-unrelated-histories
```

Most likely this will result in some merge conflicts which will need to be resolved. At the very least the `Dockerfile` and GitHub workflows should be taken from "theirs":

```
git checkout --theirs Dockerfile
git checkout --theirs .github/workflows/docker-publish.yml
```

For detailed instructions on how to resolve the merge conflicts between different version we refer you to the latest template release [notes](https://github.com/FAIRmat-NFDI/nomad-distro-template/releases/latest)

Once the merge conflicts are resolved you should add the changes and commit them

```
git add -A
git commit -m "Updated to new distribution version"
```

Ideally all workflows should be triggered automatically but you might need to run the initialization one manually by navigating to the "Actions" tab at the top, clicking "Template Repository Initialization" on the left side, and triggering it by clicking "Run workflow" under the "Run workflow" button on the right.

## FAQ/Trouble shooting

_I get an_ `Error response from daemon: Head "https://ghcr.io/v2/exciting/sol-oasis/manifests/main": unauthorized`
_when trying to pull my docker image._

Most likely you have not made the package public or provided a personal access token (PAT).
You can read how to make your package public in the GitHub docs [here](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility)
or how to configure a PAT (if you want to keep the distribution private) in the GitHub
docs [here](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-with-a-personal-access-token-classic).
