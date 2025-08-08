from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

knowledgeBase = And (
    Or(AKnight, AKnave),  # A is either a knight or a knave
    Or(BKnight, BKnave),  # B is either a knight or a knave
    Or(CKnight, CKnave),   # C is either a knight or a knave
    Not(And(AKnight, AKnave)),  # A cannot be both a knight and a knave
    Not(And(BKnight, BKnave)),  # B cannot be both a knight and a knave
    Not(And(CKnight, CKnave))   # C cannot be both a knight and a knave
)

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # TODO
    knowledgeBase,
    Implication(AKnave, Not(And(AKnight, AKnave))), # A is a knave
    Implication(AKnight, And(AKnight, AKnave)),  # A is a knight
)
# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # TODO
    knowledgeBase,
    Implication(AKnave, Not(And(AKnave, BKnave))),  # A is a knave
    Implication(AKnight, (And(AKnave, BKnave)))  # A is a knight
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # TODO
    knowledgeBase,
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),  # A is a knight
    Implication(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),  # A is a knave

    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),  # B is a knight
    Implication(BKnave, Not(Or(And(AKnight, BKnave), And(AKnave, BKnight))))  # B is a knave
    
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # TODO
    knowledgeBase,
    Implication(AKnight, Or(AKnight, AKnave)),  # A is a knight
    Implication(AKnave, Not(Or(AKnight, AKnave))),  # A is a knave

    Implication(BKnight, AKnave),
    Implication(BKnave, Not(AKnave)),  # B is a knave

    Implication(BKnight, CKnave),  # B is a knight
    Implication(BKnave, Not(CKnave)),  # B is a knave

    Implication(CKnight, AKnight),  # C is a knight
    Implication(CKnave, Not(AKnight))  # C is a knave
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
