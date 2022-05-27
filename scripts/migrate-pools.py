from util.nebula import nebulaClient
from util.astro import astroClient

if __name__ == '__main__':
    nebula = nebulaClient()
    astro = astroClient()

    pools = nebula.list_pools()
    for pool in pools:
        astro.create_pool(
            name=pool['name'],
            slots=pool['slots'],
            description=pool['description']
        )
