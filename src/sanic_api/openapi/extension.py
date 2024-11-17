from typing import TYPE_CHECKING

from sanic import Blueprint
from sanic_ext.extensions.openapi.blueprint import blueprint_factory
from sanic_ext.extensions.openapi.builders import SpecificationBuilder
from sanic_ext.extensions.openapi.extension import OpenAPIExtension as BaseExtension

if TYPE_CHECKING:
    from sanic_ext import Extend


class OpenAPIExtension(BaseExtension):
    name = "openapi"
    bp: Blueprint

    def startup(self, bootstrap: Extend) -> None:
        if self.app.config.OAS:
            self.bp = blueprint_factory(self.app.config)
            self.app.blueprint(self.bp)
            bootstrap._openapi = SpecificationBuilder()


"""
import inspect
import ast

def build_spec(app, loop):
    ...

source_code = inspect.getsource(blueprint_factory)
ast_tree = ast.parse(source_code)

my_source_code = inspect.getsource(build_spec)
my_func_ast = ast.parse(my_source_code)

ast_tree.body[0].body[6] = my_func_ast
modified_code = compile(ast_tree, filename="<ast>", mode="exec")



"""
