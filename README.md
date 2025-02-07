# Introduction
  This is a program for creating a faulted knowledge graph and sorting it in time.This program extracts the fault data from the shpfile and creates a directed graph based on the fault cuts.
## The file structure
The file structure includes the test data folder, the fault class faultKG.py, and the main test program.
![file](https://github.com/user-attachments/assets/6a0b597a-41a3-4230-acef-2fbc45db2a5d)
## program function：
1.Generate a fault directed graph.  
2.Determine the generation order based on the fault cutting relationship and sort by generation time.  
3.Output rdf files are generally opened in different knowledge graph databases.
## How to start：
1.You can open test_main.py or Create a new file for testing.  
2.The data folder contains two test data.You can use both or use your own fault data.  
3.File paths for inputting fault data and outputting rdf files.
### Flow chart
![flow](https://github.com/user-attachments/assets/6fed3de0-10bb-47ce-99e6-c025437a55df)  
## How to use rdf file  
### Importing rdf into neo4j  
#### step1 Download plug-ins 
Go to the neosemantics GitHub page to download the plugin.(https://github.com/neo4j-labs/neosemantics)
#### step2 Place the plugin JAR file into the Neo4j plugin directory
Place the plugin JAR file into the Neo4j plugin directory;  
If you are using the default installation, the plugin directory is usually located at: 
**<neo4j_home>/plugins/**
#### step3 Modify the Neo4j config file
Open the Neo4j configuration file neo4j.conf, the file path is usually: 
**<neo4j_home>/conf/neo4j.conf**
Make sure the following lines are added to the configuration file  
`
dbms.security.procedures.unrestricted=n10s.*
dbms.security.procedures.allowlist=n10s.*
`
#### step4 Restart Neo4j
#### step5 Verify plugin installation
Once the installation is complete, you can verify that the plugin was installed successfully by executing the following query in your Neo4j browser:
`RETURN n10s.version()`
  
  If the installation is successful, you will see output similar to the following:  

  ```
+-------------------+  
  
| n10s.version()    |  

+-------------------+  

| "4.0.0"           |  

+-------------------+
```
#### step6 Importing RDF Data to Neo4j 
Importing RDF data (from a file or URL) to Neo4j using n10s.rdf.import.fetch
```
CALL n10s.graphconfig.init({
    rdfTypes: ['http://www.w3.org/1999/02/22-rdf-syntax-ns#type']
})

CALL n10s.rdf.import.fetch("file:///path/to/your/file.rdf", "RDF/XML")
```
