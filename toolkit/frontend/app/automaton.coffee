
exports.automaton =
  init: ->
    console.log "LOL"
    return

    @t = new terra.Terrarium 100, 50,
      periodic: no
      trails: 0
      background: [255, 255, 255]
      cellSize: 5

    @register()

    @t.grid = @t.makeGridWithDistribution [
      # ['free_nucleotide', 1]
      ['protein', 1]
      ['gen', 1]
    ]

    # @t.grid[0][0] = @t.makeGrid([['free_aminoacids']])[0][0]

    # @t.animate()

  register: ->
    model_final = _.mapObject @models, (val, key) =>
      if key isnt 'commons' then _.extend val, @models.commons

    for a, b of _.omit model_final, 'commons'
      terra.registerCreature b

  models:
    commons:
      move: (neighbors) ->

        #: Find the spots which are free.
        spots = _.filter neighbors, (spot) ->
          not spot.creature

        if spots.length
          #: We found a new spot.
          step = spots[_.random(spots.length - 1)]
          #: Move with a probability

          if _.random(100) > 25
            return {
              x: step.coords.x
              y: step.coords.y
              creature: @
              successFn: ->
                #: Clear the original Location
                false
              failureFn: -> false
            }

        #: Didn't move.
        false

      degrade: (x, y, opts) ->

        # if @age > 10**3 or @health < 10 or _.random(10**5) < 25
        if @health < 1 or _.random(10**5) < 100
          degraded = terra.make @degrades_to,
            coords:
              x: x
              y: y

          return {
            x: x
            y: y
            creature: degraded
            successFn: -> false
            failureFn: -> true
          }

        return false

      successFn: -> false
      failureFn: -> false

      wait: ->
        # @age += 1
        return false

    gene:
      type: 'gene'
      symbol: undefined
      age: 0
      health: 100
      actionRadius: 1
      color: [30, 0, 30]
      degrades_to: 'free_nucleotide'

      mirna_gene_complex: (neighbors) ->
        spots = _.filter neighbors, (spot) =>
          return false if spot.creature.type isnt 'mirna'

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

      rrna_gene_complex: (neighbors) ->
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

      #: Inherits from commons.
      move: undefined
      degrade: undefined

      process: (neighbors, x, y) ->
        #: Increment the Age of gene.
        #: If we find a rRNA in neighbour, form rrna_gene_complex.
        #: If we find a miRNA in neighbour, form mirna_gene_complex.
        #: If age is more than age lambda, degrade.
        #: If none of the above, then, move into any random empty neighbour
        #: with a probability P, or stay there.

        @age += 1

        performance = [
          # @mirna_gene_complex
          # @rrna_gene_complex
          @move(neighbors)
        ]

        #: Perform Degrade action now. If this happens, other actions
        #  won't matter.
        degrade_act = @degrade(x, y)

        #: Eliminate all the act performances that resulted in a false
        accepted = _.compact performance
        #: Make sure degrade didn't happen
        accepted = if degrade_act then [degrade_act] else accepted

        if accepted.length
          #: If ANY valid action was performed
          #: Randomly pick one action.
          #: TODO: The actions must happen on the basis of rate const.
          step = accepted[_.random(accepted.length - 1)]

          # console.log step.creature

          return {
            x: step.x
            y: step.y
            creature: step.creature
            observed: yes
          }

        #: No action were taken
        return false

    mirna:
      type: 'mirna'
      symbol: undefined
      age: 0
      health: 100
      targets: []
      degrades_to: 'free_nucleotide'

      #: Inherits from commons.
      move: undefined
      degrade: undefined

      process: (neighbors, x, y) ->
        #: Increment the age
        #: miRNAs just move randomly and degrade after a certain age.
        #: The complex formation action is taken by the gene.
        #: SUGGESSTION: It IS possible for miRNA to take the decision
        #: instead. Will be changed later on.

        @age += 1

        #: If it doesn't degrades, then only TRY to move.
        step = @degrade(x, y) or @move(neighbors)

        if step
          #: Either Degraded, OR Moved.
          return {
            x: step.x
            y: step.y
            creature: step.creature
            observed: yes
          }

        #: Didn't move
        return false

    mirna_gene_complex:
      type: 'mirna_gene_complex'
      gene_ref: undefined
      mirna_ref: undefined
      age: 0
      health: 100
      dGbinding: 0
      degrades_to: 'free_nucleotide'

      #: Inherits from commons.
      move: undefined
      degrade: undefined

      dissociate: (neighbors, x, y) ->
        #: Dissociation happens where the miRNA and Gene dissociate. (Duh)
        #: However, the dissociation ONLY initiates if there's an empty
        #  neighbour.
        #: Having empty neighbour is not the only condition, though.
        #  We can have a scoring mechanism, that takes into account the
        #  health and age of the complex or other feedbacks.
        #: In current implementation, however, there's a simple
        #  stochastic decision here. P = 0.25 is maintained by a
        #  random number generator.
        #  TODO: Use the dGbinding value to determine probability.

        #: Find out if there're empty spots
        spots = _.filter neighbors, (spot) -> not spot.creature

        if spots.length
          #: YAY! Let's roll a dice.
          if _.random(10000) < 25
            #: Okay, we're dissociating.
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
              coords: step.coords   #: Put it at the empty space
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

        #: We aren't rolling.
        return false

      process: (neighbors, x, y) ->
        #: Process is simple. We try to degrade, then probabilisically
        #  we either move or dissociate.
        #: This is similar to the gene.process, hence comments are
        #  removed. See gene for details.

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

    rrna:
      type: 'rrna'
      age: 0
      health: 100
      degrades_to: 'free_nucleotide'

      color: [52, 152, 219]

      #: Inherits from commons.
      move: undefined
      degrade: undefined

      process: (neighbors, x, y) ->
        #: A dumb creature. Does nothing but move around and die.
        #  The genes may take this creature to form proteins.
        #: This function is not inherited due to a design limitation.
        #: See mirna.process for additional comments.

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

    rrna_gene_complex:
      type: 'rrna_gene_complex'
      gene_ref: undefined
      rrna_ref: undefined
      age: 0
      health: 100
      degrades_to: 'free_nucleotide'

      #: Inherits from commons.
      move: undefined
      degrade: undefined

      dissociate: (neighbors) ->
        #: Dissociation happens after translation is done.
        #: However, the dissociation ONLY initiates if there are
        #  two empty neighbour, and the protein is formed.
        #: The protein formation is signified by the age of complex
        #  reaching certain limit. Currently this is an arbitrary value
        #  but, this may be a value determined after taking into account
        #  the length of the mRNA sequence.
        #: See mirna_gene_complex.dissociate for additional comments.

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
        #: This complex may move, degrade, and after a certain age,
        #  dissociate to give back the gene, rrna, and a protein.
        #: See gene for details.

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

    protein:
      type: 'protein'
      gene_ref: undefined
      age: 0
      health: 100
      color: [22, 160, 133]
      degrades_to: 'free_aminoacids'

      #: Inherits from commons.
      move: undefined
      degrade: undefined

      process: (neighbors, x, y) ->
        #: Just moves, and degrades.
        #: See miRNA.process

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

    free_nucleotide:
      type: 'free_nucleotide'
      degrades_to: 'null'

      #: Inherits from commons.
      move: undefined

      color: [231, 76, 60]

      process: (neighbors, x, y) ->
        #: Just moves
        step = @move(neighbors)
        if step
          return {
            x: step.x
            y: step.y
            creature: step.creature
            observed: yes
          }
        return true

    free_aminoacids:
      type: 'free_aminoacids'
      degrades_to: 'null'
      color: [0, 0, 0]

      #: Inherits from commons.
      move: undefined

      process: (neighbors, x, y) ->
        #: Just moves
        step = @move(neighbors)
        if step
          return {
            x: step.x
            y: step.y
            creature: step.creature
            observed: yes
          }
        return true

    source:
      type: 'source'

    sink:
      type: 'sink'


