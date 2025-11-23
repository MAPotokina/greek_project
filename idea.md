# LLM Assistant for Greek Mythology

## Overview

A stand-alone application that serves as an intelligent assistant for answering questions about Greek mythology. The application leverages advanced AI techniques including GraphRAG (Graph Retrieval-Augmented Generation) and provides an interactive visual graph interface for exploring mythological relationships.

## Core Features

### 1. Question Answering System
- **Primary Source**: Bibliotheca (attributed to Apollodorus of Athens)
  - A comprehensive ancient Greek mythological text that serves as the primary knowledge base
  - Provides authoritative information on Greek myths, gods, heroes, and legends

### 2. GraphRAG Implementation
- **Technology**: Graph Retrieval-Augmented Generation
  - Utilizes graph-based knowledge representation to enhance retrieval accuracy
  - Enables more contextual and relationship-aware responses
  - Improves understanding of complex mythological connections and narratives

### 3. Interactive Visual Graph
- **Data Source**: Greek god dataset from Kaggle
- **Functionality**:
  - Visual representation of relationships between Greek gods, goddesses, and mythological figures
  - Interactive exploration of mythological connections
  - Graph-based navigation of the mythological universe

## Technical Architecture

### Components
1. **LLM Backend**: Language model for generating responses
2. **GraphRAG System**: Graph-based retrieval and augmentation layer
3. **Knowledge Base**: Bibliotheca text corpus
4. **Graph Database**: Storage and querying of mythological relationships
5. **Visualization Engine**: Interactive graph rendering
6. **User Interface**: Stand-alone application interface

## Use Cases

- Answering questions about Greek mythology
- Exploring relationships between mythological figures
- Learning about myths, legends, and stories from Bibliotheca
- Visual discovery of connections in the Greek pantheon

## Data Sources

1. **Bibliotheca (Apollodorus)**: Primary textual source for mythological knowledge
2. **Kaggle Greek God Dataset**: Structured data for graph visualization

## Implementation Considerations

- Stand-alone application (no external dependencies for core functionality)
- Integration of GraphRAG for enhanced retrieval
- Interactive graph visualization for user exploration
- Natural language question answering interface

