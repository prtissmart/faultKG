import FaultGraph
if __name__ == "__main__":
    # shpfile file path
    # enter "data/test1/FaultFromEuropa.shp" or
    # "data/test2/forTestSpecialCondition.shp"
    SHAPEFILE_PATH = "data/test1/FaultFromEuropa.shp"
    # Namespace for rdf files
    NAMESPACE = "http://example.org/"
    # Path to the output file
    EXPORT_PATH = "graph_output0109.rdf"
    # 1.Instantiating Objects
    fault = FaultGraph.FaultGraph(SHAPEFILE_PATH, NAMESPACE)
    # 2.Generating maps
    fault.generate()
    # 3.Fault generation time ordering
    # ATTENTION:Generate maps frist
    fault.sort()
    # 4.Show Sorting Results after fault.sort()
    fault.show()
    # 5.export rdf file
    fault.export_rdf(EXPORT_PATH)