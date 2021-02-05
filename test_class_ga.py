#!/use/bin/python3
from population_evolve import Population
from class_configuration import ClassConfiguration
from class_configuration import GeneSequence

if __name__ == '__main__':
    #test the ClassConfiguration class
    print("Testing!")  
    test = ClassConfiguration(go_larger=False)
    #test = ClassConfiguration()
    test.printPretty()
    '''
    test = ClassConfiguration(3)
    print("Constructor with team size set")
    test.printPretty()
    test = ClassConfiguration(4,False)
    print("Constructor with team size set and False")
    test.printPretty()
    test = ClassConfiguration(go_larger=False)
    print("Constructor passing False only")
    test.printPretty()
    '''
    
    #test the GeneSequence class
    test_sequence = GeneSequence(test)
    #test_sequence.printPretty()

    pop = Population(test)
    print("Initial population")
    pop.printPretty()
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    num_generations=100_000
    verbose = False #True
    pop.evolve_population(num_generations,verbose)
    print("Final population")
    pop.printPretty()
