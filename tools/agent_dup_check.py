#!/usr/bin/env python3
"""Check for duplicate agents based on semantic similarity."""

import sys
import yaml
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def load_agent(file_path):
    """Load agent YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def get_agent_text(agent_data):
    """Extract text representation of agent for embedding."""
    parts = []

    if 'name' in agent_data:
        parts.append(f"Name: {agent_data['name']}")

    if 'description' in agent_data:
        parts.append(f"Description: {agent_data['description']}")

    if 'capabilities' in agent_data:
        caps = ', '.join(agent_data['capabilities'])
        parts.append(f"Capabilities: {caps}")

    if 'tools' in agent_data:
        tools = ', '.join(agent_data['tools'])
        parts.append(f"Tools: {tools}")

    return ' '.join(parts)


def check_duplicates(files, threshold=0.85):
    """Check for duplicate agents based on semantic similarity."""
    if len(files) < 2:
        return []

    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load agents and create embeddings
    agents = []
    texts = []

    for file_path in files:
        try:
            agent_data = load_agent(file_path)
            agent_text = get_agent_text(agent_data)
            agents.append({
                'file': file_path,
                'data': agent_data,
                'text': agent_text
            })
            texts.append(agent_text)
        except Exception as e:
            print(f"Error loading {file_path}: {e}", file=sys.stderr)
            continue

    if len(texts) < 2:
        return []

    # Create embeddings
    embeddings = model.encode(texts)

    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(embeddings)

    # Find duplicates
    duplicates = []
    checked_pairs = set()

    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            pair = (i, j)
            if pair not in checked_pairs:
                similarity = similarity_matrix[i][j]
                if similarity >= threshold:
                    duplicates.append({
                        'file1': agents[i]['file'],
                        'file2': agents[j]['file'],
                        'similarity': float(similarity),
                        'agent1_name': agents[i]['data'].get('name', 'Unknown'),
                        'agent2_name': agents[j]['data'].get('name', 'Unknown')
                    })
                checked_pairs.add(pair)

    return duplicates


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: agent_dup_check.py <agent_files...>")
        sys.exit(1)

    files = sys.argv[1:]
    duplicates = check_duplicates(files)

    if duplicates:
        print("\n⚠️  Potential duplicate agents found:\n")
        for dup in duplicates:
            print(f"  - {dup['agent1_name']} ({Path(dup['file1']).name})")
            print(f"    {dup['agent2_name']} ({Path(dup['file2']).name})")
            print(f"    Similarity: {dup['similarity']:.2%}\n")

        print("Consider consolidating duplicate agents or differentiating their capabilities.")
        sys.exit(1)
    else:
        print("✅ No duplicate agents detected")
        sys.exit(0)


if __name__ == "__main__":
    main()