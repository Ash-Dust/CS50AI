import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # 3 Steps:
    # Consider if the page has no links then return uniform distribution
    # If it has links, then with probability damping_factor choose one of the links
    # Otherwise, with probability 1 - damping_factor choose a random page from the corpus
    if not corpus[page]:
        return {p: 1 / len(corpus) for p in corpus}
    
    else:
        # Probability of choosing a link from the current page
        prob_links = damping_factor / len(corpus[page])
        # Probability of choosing any page in the corpus
        prob_random = (1 - damping_factor) / len(corpus)
        
        # Create the transition model
        transition = {p: prob_random for p in corpus}
        for link in corpus[page]:
            transition[link] += prob_links
        return transition
    raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #the return dictionary will hold the page names and their PageRank values, the values should be summed to 1
    #First create a sample of page
    #Then pass the sample to the transition model
    #Based on the transition model, update the sample and 
    #increment the count of the page in the return dictionary
    page_ranks = {page: 0 for page in corpus}
    current_page = random.choice(list(corpus.keys()))
    for _ in range(n):
        # Get the transition model for the current page
        transition = transition_model(corpus, current_page, damping_factor)
        # Choose the next page based on the transition model
        current_page = random.choices(
            list(transition.keys()), 
            weights=list(transition.values())
        )[0]
        # Increment the count for the current page
        page_ranks[current_page] += 1
    # Normalize the PageRank values
    total_count = sum(page_ranks.values())
    for page in page_ranks:
        page_ranks[page] /= total_count
    return page_ranks
    raise NotImplementedError
    
def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # PR formula:
    # PR(p) = (1 - d) / N + d * Σ (PR(i) / NumLinks(i))
    # Initialize PageRank values
    page_ranks = {page: 1 / len(corpus) for page in corpus}
    # Create a loop to update PageRank values until reach threshold
    convergence_threshold = 0.001
    converged = False
    while not converged:
        new_ranks = {}                                 
        for page in corpus:                      
            rank_sum = 0                       # Sum of PageRank contributions from all pages linking to the current page
            for potential_linker in corpus: # Check each page in the corpus to see if it links to the current page
                if page in corpus[potential_linker]:    # If it does, add its contribution to the sum
                    rank_sum += page_ranks[potential_linker] / len(corpus[potential_linker])      #(PR(i) / NumLinks(i))        
                if not corpus[potential_linker]:    # If the page has no links, it contributes evenly to all pages
                    rank_sum += page_ranks[potential_linker] / len(corpus)                  
            # Calculate the new PageRank value using the formula
            new_ranks[page] = (1 - damping_factor) / len(corpus) + damping_factor * rank_sum
        # Check for convergence
        converged = all(abs(new_ranks[page] - page_ranks[page]) < convergence_threshold for page in corpus)
        # Update PageRank values for the next iteration
        page_ranks = new_ranks
    return page_ranks                                   # Return the final PageRank values
    raise NotImplementedError

if __name__ == "__main__":
    main()
   