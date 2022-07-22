import os
from os import listdir
from os.path import isfile, join

from copy import deepcopy
import logging
import pkgutil
import importlib
import inspect
import sys
import warnings

from redbaron import RedBaron, Node

logging.basicConfig(level=logging.DEBUG)

warnings.filterwarnings("error")

class AirflowV2Upgrader():
    def __init__(self, dag_dir: str = None, out_dir: str = None):
        self.common_dag_class_imports = [
            "airflow.hooks",
            "airflow.operators",
            "airflow.sensors",
            "airflow.providers",
        ]
        self.class_import_map = {}
        self.dag_directory = {}
        self.dag_dir = dag_dir
        self.out_dir = out_dir
        
        LOG_FORMAT = (
            "[%(name)s] [%(levelname)s] %(message)s"
        )
        LOG_LEVEL = logging.INFO
        airflow_logger = logging.getLogger("airflow_modules")
        airflow_logger.setLevel(LOG_LEVEL)
        ch = logging.StreamHandler(LOG_LEVEL)
        ch.setFormatter(LOG_FORMAT)
        airflow_logger.addHandler(ch)
        self.airflow_logger = airflow_logger

        upgrader_logger = logging.getLogger("upgrader")
        upgrader_logger.setLevel(LOG_LEVEL)
        upgrader_logger.addHandler(ch)
        self.upgrader_logger = upgrader_logger

        #TODO Give control over fixers to run
        self._fixers = [
            "fix_imports",
            "fix_access_controls",
            "fix_xcom_push",
            "fix_xcom_pull",
            "update_dag_name",
            #TODO Worker Queues
        ]
        self._reports = [
            #TODO Async Optimizations
            #TODO Worker Queues
        ]
    

    def _get_class_import_map(self, root_module) -> dict:
        found_packages = list(pkgutil.iter_modules(root_module.__path__))
        if len(found_packages) == 0:
            return {}
        action_names = [(name.split('.')[-1], ispkg) for _, name, ispkg in found_packages]
        importer = found_packages[0][0]
        class_import_map = {}
        for x, name, ispkg in found_packages:
            if "example" in name:
                continue
            elif ispkg:
                try:
                    module = importlib.import_module(root_module.__name__ + f".{name}")
                except:
                    breakpoint()
                submodule_class_import_map = self._get_class_import_map(module)
                class_import_map = {**submodule_class_import_map, **class_import_map}
            
            else:
                try:
                    module = importlib.import_module(root_module.__name__ + f".{name}")
                    if root_module.__name__ + f".{name}" not in sys.modules:
                        continue
                    else:
                        classes = inspect.getmembers(module, inspect.isclass)
                        for class_name, c in classes:
                            if c.__module__ != f"{root_module.__name__}.{name}":
                                continue
                            class_import_map[class_name] = {
                                "value": f"{root_module.__name__}.{name}",
                                "targets": class_name,
                            }
                except DeprecationWarning as err:
                    logging.debug(f"Skip depricated module {root_module.__name__}.{name}: {err}")
                except ModuleNotFoundError as err:
                    logging.error(f"Cannot load modules from {root_module.__name__}.{name}: {err}")
                except UserWarning as err:
                    continue
        return class_import_map
    
    def generate_import_map(self):
        class_import_map = {}
        for common_dag_class_import in self.common_dag_class_imports:
            root_module = importlib.import_module(common_dag_class_import)
            class_import_map = {**self._get_class_import_map(root_module), **class_import_map}
        self.class_import_map = class_import_map

    def fix_imports(self, red: RedBaron):
        import_nodes = red.find_all("FromImportNode")
        import_nodes = import_nodes.filter(lambda x: x.name.dumps() == "airflow")
        # it might be better only act against certain import paths like 
        #   contrib_imports = [node for node in import_nodes if node.find("name", value="contrib")]
        # but for now acting on all imports
        for import_node in import_nodes:

            if len(import_node.targets) == 1:
                imported_class = import_node.targets[0].value
                new_imported_class = self.class_import_map.get(imported_class, None)
                if not new_imported_class:
                    logging.warning(f'Unhandled import: {import_node.dumps()}')
                    continue

                import_node.value = new_imported_class["value"]
            else:
                had_import_error = False
                for node in import_node.targets:
                
                    imported_class = node.value
                    new_imported_class = self.class_import_map.get(imported_class, None)
                    if not new_imported_class:
                        had_import_error = True
                        logging.warning(f'Unhandled import: {import_node.dumps()}')
                        continue
                    import_node.insert_after(f"from {new_imported_class['value']} import {imported_class}")
                if not had_import_error:
                    # RedBaron doesn't handle weird indentation well
                    # It's possible this throws the Exception
                    #   Exception: It appears that you have indentation in your CommaList, 
                    #   for now RedBaron doesn't know how to handle this situation 
                    #   (which requires a lot of work), sorry about that. You can find 
                    #   more information here https://github.com/PyCQA/redbaron/issues/100
                    del import_node.parent[import_node.index_on_parent]
    
    def fix_access_controls(self, red: RedBaron):
        # Check for DAG access controls
        dag_access_control_nodes = red.find_all("NameNode",value="access_control")
        if len(dag_access_control_nodes):
            accts = []
            for node in dag_access_control_nodes:
                accts.append(node.parent.dict_.dictitem_.key_.dumps())
                arg = node.parent
                arg.value = "None"
            logging.warning(f"Contains DAG access controls. Setting to None: {accts}")

    def fix_xcom_push(self, red: RedBaron):
        # Fix xcom_push -> do_xcom_push in Operator args
        xcom_push_nodes = red.find_all("NameNode",value='xcom_push')
        args_xcom_push_nodes = xcom_push_nodes.filter(lambda x: x.parent.type == "call_argument")
        args_xcom_push_nodes.map(lambda x: x.replace("do_xcom_push"))
    
    def fix_xcom_pull(self, red: RedBaron):
        # Fix xcom_push -> do_xcom_push in Operator args
        xcom_pull_nodes = red.find_all("NameNode",value='xcom_pull')
        args_xcom_pull_nodes = xcom_pull_nodes.filter(lambda x: x.parent.type == "call_argument")
        for node in args_xcom_pull_nodes:
            arg = node.parent
            self.remove_arg_via_fst(arg)
    
    # Method to resolve https://github.com/PyCQA/redbaron/issues/100
    @staticmethod
    def remove_arg_via_fst(arg):
        call_fst = arg.parent.fst()
        # Account for commas in Call FST
        # Last argument or last argument with trailing comma
        if len(call_fst["value"]) == arg.index_on_parent * 2 or \
            len(call_fst["value"]) == arg.index_on_parent * 2 + 1:
            call_fst["value"] = call_fst["value"][:arg.index_on_parent * 2]
        # Not last argument
        else:
            call_fst["value"] = call_fst["value"][:arg.index_on_parent * 2] + \
                call_fst["value"][arg.index_on_parent * 2  + 2:]
        new_call_node = Node.from_fst(call_fst, parent=arg.parent.parent, on_attribute="call")
        new_call_node.parent.call_.replace(new_call_node)

    def update_dag_name(self, red: RedBaron):
        # update dag name
        dag_def = red.find("NameNode",value='DAG').parent
        dag_name = dag_def.call_[0].string_.value
        dag_def.call_[0].value = dag_name[:-1] + "_upgraded" + dag_name[-1]

    def upgrade_dag_file(self, filename: str):
        red = self.load_dag_file(filename)
        self.fix_imports(red)
        self.fix_access_controls(red)
        self.fix_xcom_push(red)
        self.fix_xcom_pull(red)
        self.update_dag_name(red)
        self.write_updated_dag_file(filename, red)
    
    def load_dag_file(self, filename: str): 
        with open(filename, "r") as f:
            code = f.read()
        red = RedBaron(code)
        return red
    
    def write_updated_dag_file(self, filename: str, red: RedBaron):
        upgraded_filename = filename[:-3] + "_upgraded" + filename[-3:]
        if self.out_dir:
            upgraded_filename = join(self.out_dir, os.path.basename(upgraded_filename))
        
        with open(upgraded_filename, "w") as f:
            f.write(red.dumps())

    def get_dag_files_from_dir(self, dag_dir: str):
        dag_files = [
            join(dag_dir, f) for f in listdir(dag_dir) \
            if isfile(join(dag_dir, f)) and f[-3:] == ".py" and "upgraded" not in f
        ]
        return dag_files
    
    def create_out_dir_if_not_exists(self, out_dir: str):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    def upgrade_dag_files(self, dag_dir: str = None, out_dir: str = None):
        if self.dag_dir:
            dag_dir = self.dag_dir
        elif not dag_dir:
            logger.error("No DAG directory provided")
            exit()
        else:
            self.dag_dir = dag_dir
        
        if self.out_dir:
            out_dir = self.out_dir
        if out_dir:
            self.out_dir = out_dir
            self.create_out_dir_if_not_exists(out_dir)
        
        dag_files = self.get_dag_files_from_dir(dag_dir)
        for dag_file in dag_files:
            self.upgrade_dag_file(dag_file)
    
if __name__ == "__main__":
    upgrader = AirflowV2Upgrader(dag_dir="dags/", out_dir="dags/upgraded/")
    upgrader.generate_import_map()
    upgrader.upgrade_dag_files()


