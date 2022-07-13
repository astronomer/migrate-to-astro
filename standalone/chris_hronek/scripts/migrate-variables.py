from util.nebula import nebulaClient
from util.astro import astroClient

if __name__ == '__main__':
    nebula = nebulaClient()
    astro = astroClient()

    existing_target_vars = []
    [existing_target_vars.append(variable['key']) for variable in astro.list_variables()]

    for variable in nebula.get_variables():
        if variable['key'] in existing_target_vars:
            astro.update_variable(
                key=variable['key'],
                value=variable['value']
            )
        else:
            astro.create_variable(
                key=variable['key'],
                value=variable['value']
            )
