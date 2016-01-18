# Simulated Study: miRNA mediated gene regulation

In this simulation, we are primarily focused on studying the effects of various
simple interactions that may coexist to form the highly complicated regulatory
pathways.

This simulation aims to study the following interactions:
- Production of miRNAs from intronic regions of the genes
- Binding of the miRNAs to form a miRNA - gene complex that will prevent
  the expression of a particular gene.
- Effect of the cases where the genes are prevented from being expressed.

The simulation also tries to find out if the unexpressed genes also give rise
to the increase in production of some other gene which may in turn increase the
concentration of that gene, hence forming a positive feedback loop.

# Entity

This is a base class that describes behaviours common to all the molecules,
hereby denoted as "Entities" in the given cellular environment.

    class Entity
      constructor: (opts) ->
        {@symbol, @color} = opts
        @age = 0
        @health = 100
        @actionRadius = 1

## Movement

This function defines the basic movement of the entities. This movement can
assumed to be Brownian. Various studies have concluded that the Brownian motion
can be approximated by random walks in the simulated environments if the density
of entities is sufficiently high and the distance traversed in the random walk
performed by the entities is sufficiently small.

The following function takes in the surrounding entities (neighbors) and makes
an informed decision of the the movement.

      move: (neighbors) ->

The decision is taken as follows:
1. Find the spots that are empty.
2. In those empty spots, find the location where the cell could go next.

Currently, this dicision is taken with a random probability, however, a more
"vectorial" movement can easily be implemented.

        spots = _.filter neighbors, (spot) -> not spot.creature
        if spots.length
          step = spots[_.random(spots.length - 1)]

          # if _.random(100) > 25
          return {
            x: step.coords.x
            y: step.coords.y
            creature: @
            successFn: -> false
            failureFn: -> false
          }
        false

## Degradation

This is an important "function" of the entities that are present. Here, the
entities are expected to degrade into the constituents after they are either
too old, or have a "poor" health.

      degrade: (x, y, opts) ->
        if @age > 100 # or _.random(10**5) < 100
          degraded = new @degrades_to
            symbol: @symbol

          return {
            x: x
            y: y
            creature: degraded
            successFn: -> false
            failureFn: -> true
          }

        return false

      #: Some Functionally important defaults.
      successFn: -> false
      failureFn: -> false
      isDead: -> false
      boundEnergy: ->
      wait: -> false

## Process

The "proceess" function is the main entry point for each entity at every step.
This dumb function allows the entity to move and degrade.

      process: (neighbors, x, y) ->
        @age += 1
        step = @degrade(x, y) or @move(neighbors)
        if step
          return {
            x: step.x
            y: step.y
            creature: step.creature
            observed: yes
          }
        return false

# Genes

Genes extend the basic definition of the Entity. They can inherently move and
degrade, however they can do a few more things, namely, "express" by binding to
the rRNAs (definition given later) and making a rRNA-Gene complex, become
prevented by binding to the miRNAs and forming a miRNA-Gene complex.

    class Gene extends Entity
      constructor: (opts) ->
        @type = 'Gene'
        @degrades_to = FreeNucleotide
        super opts

The following function determines if the gene would form a miRNA Gene complex.
Basically, this will happen if the gene is one of the targets of the given
given miRNA. The "target" information can be carried by the miRNA and Gene both
from a technical perspective, hence we're storing this information with gene
iteself for a less complex computation requirement.

This function, similar to the "move" function, inspects its neighbors.

      miRNA_Gene_Complex: (neighbors) ->
        spots = _.filter neighbors, (spot) =>
          return false if spot.creature.type isnt 'miRNA'

          target_id = _.findIndex spot.creature.targets, (target) =>
            target.symbol is @symbol

          return target_id isnt -1

        if spots.length
          #: Order all the spots on the basis of least affinity
          spots = _.sortBy spots, (spot) =>
            target = _.find spot.creature.targets, (target) =>
              target.symbol is @symbol

            return target.affinity

          binding_mir = spots.first()

          target = _.find binding_mir.creature.targets, (target) =>
            target.symbol is @symbol

          complex_mir = terra.make 'mirna_gene_complex',
            coords: binding_mir.coords
            gene_ref: @.creature
            mirna_ref: binding_mir.creature
            dGbinding: target.affinity

          return {
            x: binding_mir.coords.x
            y: binding_mir.coords.y
            creature: complex_mir
            successFn: -> false
            failureFn: -> true
          }

        return false

Similar to the above, the following function determines if it should bind to the
rRNA and, if so, then, for how long. More comments on this will be added later.

      rRNA_Gene_Complex: (neighbors) ->
        spots = _.filter neighbors, (spot) ->
          spot.creature.type is 'rrna'

        if spots.length
          binding_rrna = spots[_.random(spots.length - 1)]

          complex_rrna = terra.make 'rrna_gene_complex',
            coords: binding_rrna.coords
            gene_ref: @.creature
            rrna_ref: binding_rrna.creature

          return {
            x: binding_rrna.coords.x
            y: binding_rrna.coords.y
            creature: complex_rrna
            successFn: -> false
            failureFn: -> true
          }

        return false

This function performs following functions, overriding the default behaviour,
when provided with the neighbors and its current coordinate in space. It takes
a decision from following:

- Increment the Age of gene.
- If we find a rRNA in neighbor, form rRNAGeneComplex.
- If we find a miRNA in neighbor, form miRNAGeneComplex.
- If age is more than some age, degrade.

If none of the above, happens, then we simply move.

      process: (neighbors, x, y) ->
        @age += 1

        performance = [
          # @mirna_gene_complex
          # @rrna_gene_complex
          @move(neighbors)
        ]

        degrade_act = @degrade(x, y)

        accepted = _.compact performance
        accepted = if degrade_act then [degrade_act] else accepted

        if accepted.length
          step = accepted[_.random(accepted.length - 1)]
          return {
            x: step.x
            y: step.y
            creature: step.creature
            observed: yes
          }

        return false

# miRNA

Similar to the genes, these miRNAs are simple entities that just move and
degrade. The regulatory effect is handled by the genes. Please note, however,
that this behaviour is just an implementation detail and NOT a representation
of what happens in reality. The (closer to) real behaviour is enforced here by
the Ranking Parameters and the Eigen Matrix rank selector that takes care of
multiple entities that are competing for the same spots.

    # coffeelint: disable=camel_case_classes
    class miRNA extends Entity
      constructor: (opts) ->
        @type = 'miRNA'
        @degrades_to = FreeNucleotide
        super opts

# miRNA Gene Complex

This is the complex that prevents the gene from being expressed. In simulation
environment this behaviour is expressed simply by allowing this entity to move,
degrade, and, dissociate.

    class miRNAGeneComplex extends Entity
      constructor: (opts) ->
        @type = 'miRNAGeneComplex'
        {@gene_ref, @mirna_ref} = opts
        @degrades_to = FreeNucleotide

Dissociation happens where the miRNA and Gene dissociate. (Duh) However, the
dissociation ONLY initiates if there's an empty neighbour.

Having empty neighbour is not the only condition, though. We have a scoring
mechanism, that takes into account the health and age of the complex as well as
the thermodynamics.

In current implementation, however, there's a simple stochastic decision here.
P = 0.25 is maintained by a random number generator. This will be changed after
debugging.

      dissociate: (neighbors, x, y) ->
        spots = _.filter neighbors, (spot) -> not spot.creature

        if spots.length
          if _.random(10000) < 25
            #: Take a random empty spot for the released miRNA
            step = spots[_.random(spots.length - 1)]

            #: Create a Gene at current position.
            gene = terra.make 'gene',
              coords:
                x: x
                y: y
              symbol: @gene_ref.symbol
              age: @gene_ref.age + 1
              health: @gene_ref.health - 1

            #: Create a miRNA
            mirna = terra.make 'mirna',
              coords: step.coords
              symbol: @mirna_ref.symbol
              age: @mirna_ref.age + 1
              health: @mirna_ref.health - 1
              targets: @mirna_ref.targets

            return {
              x: x
              y: y
              creature: gene
              successFn: -> true
              failureFn: -> false
            }

        return false

Process is simple. We try to degrade, then probabilisically we either move or
dissociate.

      process: (neighbors, x, y) ->
        @age += 1

        performance = [
          @dissociate(neighbors, x, y)
          @move(neighbors)
        ]

        degrade_act = @degrade(x, y)

        accepted = _.compact performance
        accepted = if degrade_act then [degrade_act] else accepted

        if accepted.length
          step = accepted[_.random(accepted.length - 1)]

          return {
            x: step.x
            y: step.y
            creature: step.creature
            observed: yes
          }

        return false

# rRNA

These are the protein production entities. They only moves around in the
environment, and degrade. Similar to miRNA, it is 'dumb'.

    class rRNA extends Entity
      constructor: (opts) ->
        @type = 'rRNA'
        @degrades_to = FreeNucleotide
        super opts

# rRNA Gene Complex

These are where the protein is produced, and the genes are expressed. These
are smart entities that move, degrade, and if they have produced the protein,
they dissociate to give back the rRNA, Gene, and the Protein.

The ranking parameter calculates the appropriate age when the complex is
dissicated.

    class rRNAGeneComplex extends Entity
      constructor: (opts) ->
        @type = 'rRNAGeneComplex'
        @gene_ref = opts.gene_ref
        @degrades_to = FreeNucleotide # TODO
        super opts

Dissociation happens after translation is done. However, the dissociation ONLY
initiates if there are two empty neighbour, and the protein is formed.

The protein formation is signified by the age of complex reaching certain
value, as determined by the rank. Currently this is an arbitrary value

      dissociate: (neighbors) ->
        spots = _.filter neighbors, (spot) -> not spot.creature

        if spots.length >= 2
          if @age >= 25
            #: Take two random spots
            es1 = spots.splice(_.random(spots.length - 1), 1).pop()
            es2 = spots.splice(_.random(spots.length - 1), 1).pop()

            #: Create a Gene
            gene = terra.make 'gene',
              coords: @coords
              symbol: @gene_ref.symbol
              age: @gene_ref.age + 1
              health: @gene_ref.health - 1

            #: Create a protein
            protein = terra.make 'mirna',
              coords: es1.coords
              gene_ref: @gene_ref
              age: @gene_ref.age + 1
              health: @gene_ref.health - 1

            #: Create a rRNA
            rrna = terra.make 'rrna',
              coords: es2.coords
              age: @rrna_ref.age + 1
              health: @rrna_ref.health - 1

            return {
              x: gene.coords.x
              y: gene.coords.y
              creature: gene
              successFn: -> true
              failureFn: -> false
            }

        return false

      process: (neighbors, x, y) ->
        @age += 1

        performance = [
          @dissociate(neighbour, x, y)
          @move(x, y)
        ]

        degrade_act = @degrade(x, y)

        accepted = _.compact performance
        accepted = if degrade_act then [degrade_act] else accepted

        if accepted.length
          step = accepted[_.random(accepted.length - 1)]

          return {
            x: step.x
            y: step.y
            creature: step.creature
            observed: yes
          }

        return false

# Protein

This is also a dumb entity. Obviously, the "dumbness" refers to the technical
implementation here! We don't yet take into account the Protein-Protein
interactions, however, those are in todo. The dumb creature moves and
dissociates.

    class Protein extends Entity
      constructor: (opts) ->
        @type = 'Protein'
        @gene_ref = opts.gene_ref
        @degrades_to = FreeAminoAcid
        super opts

# Free Nucleotides and Amino Acids

These are VERY dumb entities that just move. Can not even degrade! Now. They
probably DO degrade, and are not REALLY dumb. But. That's chemistry.

    class FreeNucleotide extends Entity
      constructor: (opts) ->
        @type = 'FreeNucleotide'
        @degrades_to = undefined
        super opts

    class FreeAminoAcid extends Entity
      constructor: (opts) ->
        @type = 'FreeAminoAcid'
        @degrades_to = undefined
        super opts
    # coffeelint: enable=camel_case_classes


# Source and Sink

These are static entities. Sink has the work to simulate the semipermeable
memberane that are used to "secrete" the Proteins. In technical terms basically,
we're removing the proteins produced from the environment. These also let the
Free Nucleotides and Free Amino Acids to leave the environment too.

Source is an entity that is used to both replenish and introduce genes and
miRNAs into the simulation environment. These allow realtime interaction by the
users too, so, the effects seen on the network can be observed here as well.

    class Source extends Entity
      constructor: (opts) ->
        @type = 'Source'
        super opts

      process: (neighbors, x, y) ->
        return false

    class Sink extends Entity
      constructor: (opts) ->
        @type = 'Sink'
        super opts

      process: (neighbors, x, y) ->
        return false

    module.exports =
      Gene: Gene
      miRNA: miRNA
      rRNA: rRNA
      Protein: Protein
      Source: Source
      Sink: Sink
      rRNAGeneComplex: rRNAGeneComplex
      miRNAGeneComplex: miRNAGeneComplex
