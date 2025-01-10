import FaultGraph
if __name__ == "__main__":
    # shpfile file path
    SHAPEFILE_PATH = "data/fortest/test3/test3.shp"
    # Namespace for rdf files
    NAMESPACE = "http://example.org/"
    # Path to the output file
    EXPORT_PATH = "graph_output0109.rdf"
    # Instantiating Objects
    fault = FaultGraph.FaultGraph(SHAPEFILE_PATH, NAMESPACE)
    # Generating maps
    fault.generate()
    # Fault generation time ordering
    fault.sort()
    # Show Sorting Results
    fault.show()
    # export rdf file
    fault.export_rdf(EXPORT_PATH)