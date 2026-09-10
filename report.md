# Project 1 Report: Intelligent Search Visualizer

> [!IMPORTANT]
> **AUTOGRADER COMPLIANCE INSTRUCTIONS:**
> This report is parsed automatically by the autograder. To ensure you receive full credit for your work:
> 1. **Do not modify** the section headers (`## ...`) or bold field keys (e.g., `**Name:**`, `**Selected Region:**`, `**Live Deployment URL:**`, etc.).
> 2. **Write your answers directly after** the colon `:` of each field, replacing the placeholder text completely (including the outer brackets `[` and `]`).
> 3. **Maintain the file structure**. Changing headers, bold titles, or deleting lines can cause the autograder to miss your responses and award 0 marks.

---

## Student Information 
- **Name:** Student Name
- **MMDT ID:** MMDT-2026-001

---

## Section 1: Selected City Region
- **Selected Region:** Myanmar

---

## Section 2: Map Graph Configuration
- **Total Cities Configured:** 22
- **Total Connection Edges:** 27
- **Graph Fully Connected:** Yes

---

## Section 3: Local Verification & Search Algorithms
*Check the algorithms you successfully ran and verified on your local development server by placing an `x` in the brackets (e.g., `[x]`):*
- [x] Breadth-First Search (BFS)
- [x] Depth-First Search (DFS)
- [x] Uniform Cost Search (UCS)
- [x] Iterative Deepening Search (IDS)
- [x] Greedy Best-First Search (Greedy)
- [x] A* Search (A*)

---

## Section 4: Deployed and Presentation Information
- **Deployment Platform:** Render
- **Live Deployment URL:** https://example.com/myanmar-search-visualizer
- **Video Presentation Link:** https://example.com/myanmar-search-video

---

## Section 5: Discussion
*Provide your written analysis for each point by replacing the bracket placeholders below:*
- **Which search algorithm is best for this route finding problem?** 
    A* is the best option for this route finding problem because it combines the cost travelled so far with a heuristic estimate of the remaining distance. In a road map with weighted edges, A* reaches the destination efficiently while still guaranteeing the lowest-cost path when the heuristic is admissible. UCS is also optimal, but it explores more states because it does not use heuristic guidance. For a realistic Myanmar road network, A* provides the best balance between speed and quality.
- **Link the idea of search algorithm to today Generative AI.** 
    Search algorithms are a foundational idea behind many modern AI systems, including generative AI, because they represent the process of exploring possible paths through a state space to find the best answer. In generative AI, model responses can be seen as a search over many possible continuations, guided by scoring and heuristics. Just as A* chooses promising routes in a map, generative systems use ranking and evaluation mechanisms to choose the most likely next token or best answer. This same idea of exploring candidate states efficiently is central to both classical AI planning and current generative systems.
