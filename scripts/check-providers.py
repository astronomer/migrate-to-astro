from util.nebula import nebulaClient
from util.astro import astroClient

if __name__ == '__main__':
    nebula = nebulaClient()
    astro = astroClient()
    missing_providers, nebula_providers, astro_providers = [], [], []

    [nebula_providers.append(f"{provider['package_name']}") for provider in nebula.list_providers()]
    [astro_providers.append(f"{provider['package_name']}") for provider in astro.list_providers()]

    for provider in nebula_providers:
        if provider not in astro_providers:
            missing_providers.append(provider)

    missing_providers.remove("apache-airflow-providers-mysql") #mysql throwing all sorts of errors with new image
    if len(missing_providers) == 0:
        msg = "No providers missing!"
    else:
        msg = "\nPlease add the following providers:\n"
        for provider in missing_providers: msg += f"{provider}\n"

    print(msg)
