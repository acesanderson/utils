import ast
import networkx as nx
import pycallgraph
from pycallgraph.output import GraphvizOutput
from pycallgraph.config import Config
import inspect
import sys
from graphviz import Digraph
import os


def create_static_call_graph(package_path):
    """
    Creates a static call graph using AST analysis.

    Args:
        package_path (str): Path to the Python package/module

    Returns:
        networkx.DiGraph: Directed graph representing function calls
    """

    def visit_module(module_path):
        with open(module_path) as f:
            tree = ast.parse(f.read())

        calls = []
        current_function = [None]

        class CallVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                parent_func = current_function[0]
                current_function[0] = node.name
                self.generic_visit(node)
                current_function[0] = parent_func

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    if current_function[0]:
                        calls.append((current_function[0], node.func.id))
                self.generic_visit(node)

        CallVisitor().visit(tree)
        return calls

    # Create graph
    G = nx.DiGraph()
    calls = visit_module(package_path)

    # Add edges for function calls
    for caller, callee in calls:
        G.add_edge(caller, callee)

    return G


def generate_dynamic_call_graph(package_name, output_path="call_graph.png"):
    """
    Generates a dynamic call graph using pycallgraph.

    Args:
        package_name (str): Name of the package to analyze
        output_path (str): Where to save the output graph
    """
    config = Config()
    config.trace_filter = GlobbingFilter(
        include=[f"{package_name}.*"], exclude=["pycallgraph.*"]
    )

    graphviz = GraphvizOutput(output_file=output_path)

    with PyCallGraph(output=graphviz, config=config):
        # Import and run the package here
        __import__(package_name)


def create_module_dependency_graph(package_dir):
    """
    Creates a module-level dependency graph using inspect.

    Args:
        package_dir (str): Directory containing the package

    Returns:
        Digraph: Graphviz graph showing module dependencies
    """
    dot = Digraph(comment="Module Dependencies")
    dot.attr(rankdir="LR")

    # Add package directory to path
    sys.path.insert(0, package_dir)

    def get_module_deps(module_name):
        try:
            module = __import__(module_name)
            deps = set()

            for name, obj in inspect.getmembers(module):
                if inspect.ismodule(obj):
                    if obj.__name__.startswith(module_name):
                        deps.add(obj.__name__)

            return deps
        except ImportError:
            return set()

    # Create nodes and edges
    modules = {}  # Keep track of processed modules
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            if file.endswith(".py"):
                module_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]

                if module_name not in modules:
                    modules[module_name] = True
                    dot.node(module_name)

                    # Add dependencies
                    deps = get_module_deps(module_name)
                    for dep in deps:
                        dot.edge(module_name, dep)

    return dot


# Example usage:
if __name__ == "__main__":
    # Static analysis
    package_path = "jailbreak.py"
    static_graph = create_static_call_graph(package_path)
    nx.draw(static_graph, with_labels=True)
    plt.savefig("static_call_graph.png")

    # Dynamic analysis
    generate_dynamic_call_graph("your_package_name")

    # Module dependencies
    dep_graph = create_module_dependency_graph("path/to/package/dir")
    dep_graph.render("module_dependencies", format="png")
