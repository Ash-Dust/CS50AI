import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # First, determine the probability of having # copies of the gene and trait
    # if a person has parents, their gene probability depends on the parents' genes
    # if a person does not have parents, use the unconditional probabilities
    # Remember to account for mutation probabilities

    # take example of joint_probability(people, {"Harry"}, {"James"}, {"James"})
    # Harry has 1 gene, James has 2 genes, Lily has 0 genes
    # James has the trait, Harry and Lily do not have the trait
    # The probability is: P(James) * P(Harry) * P(Lily)
    # P(Lily) = PROBS["gene"][0] * PROBS["trait"][0][False] = 0.96 * 0.99 = 0.9504
    # P(James) = PROBS["gene"][2] * PROBS["trait"][2][True] = 0.01 * 0.65 = 0.0065
 
    # P(Trait) = PROBS["trait"][1][False]
    # P(Gene) = P(Father passes gene & Mother not passes gene) + P(Mother passes gene & Father not passes gene)
    # P(Father passes gene & Mother not passes gene) = P(Father passes gene) * P(Mother not passes gene)
    # = (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) = 0.99 * 0.99 = 0.9801
    # P(Mother passes gene & Father not passes gene) = P(Mother passes gene) * P(Father not passes gene)
    # = PROBS["mutation"] * PROBS["mutation"] = 0.01 * 0.01 = 0.0001
    # P(Gene) = 0.9801 + 0.0001 = 0.9802
    # P(Harry) = P(Gene) * P(Trait) = 0.9802 * PROBS["trait"][1][False] = 0.9802 * 0.44 = 0.431288
    # P = P(James) * P(Harry) * P(Lily) = 0.0065 * 0.431288 * 0.9504 = 0.002667
    # joint_probability(people, {"Harry"}, {"James"}, {"James"}) = 0.002667

    # For each person, determine the number of genes they have
    # and whether they have the trait, then calculate the probability
    # and multiply all probabilities together to get the joint probability
    joint_prob = 1
    for person in people:
        # Determine number of genes
        if person in one_gene:
            num_genes = 1
        elif person in two_genes:
            num_genes = 2
        else:
            num_genes = 0
        # Determine if they have the trait
        has_trait = person in have_trait
        # Calculate probability for this person
        if people[person]["mother"] is None and people[person]["father"] is None:
            # No parents, use unconditional probability
            gene_prob = PROBS["gene"][num_genes]
        else:
            # Has parents, calculate based on their genes
            mother = people[person]["mother"]
            father = people[person]["father"]
            # Determine mother's gene probability
            if mother in one_gene:
                mother_prob = 0.5
            elif mother in two_genes:
                mother_prob = 1 - PROBS["mutation"]
            else:
                mother_prob = PROBS["mutation"]
            # Determine father's gene probability
            if father in one_gene:
                father_prob = 0.5
            elif father in two_genes:
                father_prob = 1 - PROBS["mutation"]
            else:
                father_prob = PROBS["mutation"]

            # Calculate gene probability based on number of genes
            if num_genes == 2:
                gene_prob = mother_prob * father_prob
            elif num_genes == 1:
                gene_prob = mother_prob * (1 - father_prob) + (1 - mother_prob) * father_prob
            else:
                gene_prob = (1 - mother_prob) * (1 - father_prob)
        trait_prob = PROBS["trait"][num_genes][has_trait]
        joint_prob *= gene_prob * trait_prob
    return joint_prob
    raise NotImplementedError

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    probabilities_copy = probabilities.copy()
    for person in probabilities_copy:
        # Update gene probabilities
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        # Update trait probabilities
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # Sum up the probabilities for each person 
    # Then divide each probability by the sum to normalize
    for person in probabilities:
        # Normalize gene probabilities
        gene_total = sum(probabilities[person]["gene"].values())
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] /= gene_total
        # Normalize trait probabilities
        trait_total = sum(probabilities[person]["trait"].values())
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] /= trait_total

if __name__ == "__main__":
    main()