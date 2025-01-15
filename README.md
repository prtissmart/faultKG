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
