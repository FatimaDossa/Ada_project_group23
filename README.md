# Ada_project_group23 : Graph Mining Healthcare Approach: Analysis and Recommendation

## Project Overview  
This project explores the use of **Frequent Subgraph Mining (FSM)** and **Discriminative Subgraph Mining (DSM)** for healthcare recommendation systems, specifically leveraging the **MIMIC dataset**. The aim is to apply graph mining techniques to improve predictive analytics in medical data, aiding in personalized patient recovery recommendations.

## Motivation  
This project is driven by our interest in healthcare applications and the opportunity to apply graph algorithms to real-world problems. Subgraph mining helps uncover underlying patterns and relationships in patient records, making it possible to predict recovery outcomes more effectively and support healthcare decision-making.

## Technical Summary  
- Patient symptoms and diagnoses are modeled as directed graphs, where nodes represent medical concepts and edges denote relationships.  
- FSM identifies recurring subgraphs across all patients, while DSM finds subgraphs strongly associated with specific recovery outcomes.  
- Our analysis revealed that DSM provides better prediction accuracy than FSM in healthcare scenarios.  
- This approach overcomes the limitations of traditional clustering methods, which are often sensitive to outliers and require extensive preprocessing.

## Techniques and Tools  
- Graph-based representations of medical data  
- FSM and DSM algorithms for pattern extraction  
- Analysis of predictive accuracy based on mined subgraphs  
- Use of the MIMIC dataset for patient records

## Checkpoint 3
- Completed technical summary and detailed report (available in `Checkpoint2/`)  
- Updated this README to reflect project direction and insights gained  
- Identified key implementation challenges including data transformation, computational complexity, and data privacy  
- Repository remains clean and well-structured with no temporary or backup files

## Checkpoint 4
- Successfully implemented both FSM and DSM algorithms
- Validated results through multiple test cases and comparative evaluation
- Generated a cleaned and structured dataset suitable for subgraph mining studies
- Completed implementation overview, summary, and detailed report (available in Checkpoint3/)
- Continued refining visualization and result interpretation
- Repository remains clean and well-organized with updated documentation

## Running Instructions
- Navigate to the src/ folder
- Run main.py
- If you encounter errors, ensure the path to data.csv inside the data/ folder is correct and properly referenced in your main.py code.
  
## Collaborators  
- Fatima Dossa  
- Maira Khan  
