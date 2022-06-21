from util.nebula import nebulaClient
from util.astro import astroClient

if __name__ == '__main__':
    nebula = nebulaClient()
    astro = astroClient()

    existing_target_pools = []
    [existing_target_pools.append(pool['name']) for pool in astro.list_pools()]

    pools = nebula.list_pools()
    for pool in pools:

        if 'description' in pool:
            description = pool['description']
        else:
            description = ''

        if pool['name'] in existing_target_pools:
            astro.update_pool(
                name=pool['name'],
                slots=pool['slots'],
                description=description
            )
        else:
            astro.create_pool(
                name=pool['name'],
                slots=pool['slots'],
                description=description
            )

